import asyncio
import random
import boto3
from botocore.config import Config
import json
import sys
from pathlib import Path
import aioboto3
import os
from botocore.exceptions import ClientError

# Ensure backend directory is in Python path for imports
_backend_dir = Path(__file__).resolve().parent.parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from app.core.config import (
    AWS_PROFILE, LLM_REGION, LLM_MAX_TOKENS, LLM_TEMPERATURE,
    LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL
)

# -- Utility --

async def retry_bedrock(operation, *args, max_retries=6, **kwargs):
    base = 0.5
    for attempt in range(max_retries):
        try:
            return await operation(*args, **kwargs)

        except ClientError as e:
            error_code = e.response["Error"]["Code"]

            if error_code in ("ThrottlingException", "TooManyRequestsException"):
                wait = base * (2 ** attempt) + random.random()
                print(f"Retrying due to throttling... waiting {wait:.2f}s")
                await asyncio.sleep(wait)
                continue

            raise  # different AWS error → rethrow

    raise RuntimeError("Failed after retries")


# ============================================================================
# BEDROCK IMPLEMENTATION
# ============================================================================

async def run_model_bedrock(system_prompt: str, user_message: str):
    """
    Run a model call to Bedrock with given prompts.
    """
    # Use config for profile
    session = aioboto3.Session(
        profile_name=AWS_PROFILE,
        region_name=LLM_REGION
    )

    config = Config(
        read_timeout=100000,
        connect_timeout=60,
        retries={'max_attempts': 3, "mode": "adaptive"},
        max_pool_connections=50
    )
    
    # Use the client as an async context manager
    async with session.client("bedrock-runtime", region_name=LLM_REGION, config=config) as client:
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": LLM_MAX_TOKENS,
            "temperature": 0.1, # Using 0.1 for deterministic code generation
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}]
        }
        
        # Hardcoded model ID from original file - strictly keeping it
        model_id = "arn:aws:bedrock:us-east-1:807923266708:inference-profile/global.anthropic.claude-sonnet-4-20250514-v1:0"
        
        response = await retry_bedrock(client.invoke_model,
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )

        # Read the response body
        body_content = await response["body"].read()

        parsed = json.loads(body_content)
        return parsed["content"][0]["text"]


# ============================================================================
# GROQ IMPLEMENTATION
# ============================================================================

async def run_model_groq(system_prompt: str, user_message: str):
    """
    Run a model call to Groq API with given prompts.
    """
    try:
        from groq import Groq
    except ImportError as exc:
        raise ImportError(
            "Groq SDK not installed. Install it with: pip install groq"
        ) from exc
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")
    
    client = Groq(api_key=GROQ_API_KEY)
    
    # Groq API format
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
    )
    
    return response.choices[0].message.content


# ============================================================================
# UNIFIED INTERFACE - TOGGLE BETWEEN PROVIDERS
# ============================================================================

async def run_model(system_prompt: str, user_message: str):
    """
    Unified interface to run model calls.
    Switches between Bedrock and Groq based on LLM_PROVIDER config.
    
    To switch providers:
    - Set environment variable: LLM_PROVIDER=bedrock (or groq)
    - Or modify the .env file: LLM_PROVIDER=groq
    - Or comment/uncomment the provider check below for manual toggle
    """
    # ========================================================================
    # TOGGLE POINT: Comment/uncomment to switch providers manually
    # ========================================================================
    
    # Option 1: Use environment variable (recommended)
    if LLM_PROVIDER.lower() == "groq":
        print("[LLM] Using Groq provider")
        return await run_model_groq(system_prompt, user_message)
    else:
        print("[LLM] Using Bedrock provider")
        return await run_model_bedrock(system_prompt, user_message)
    
    # Option 2: Manual toggle (uncomment one, comment the other)
    # return await run_model_groq(system_prompt, user_message)  # Use Groq
    # return await run_model_bedrock(system_prompt, user_message)  # Use Bedrock


async def run_model_qwen(system_prompt: str, user_message: str):
    print("[DEBUG] Entered run_model_qwen()")

    session = aioboto3.Session(
        profile_name=AWS_PROFILE,
        region_name=LLM_REGION
    )

    config = Config(
        read_timeout=100000,
        connect_timeout=60000,
        retries={'max_attempts': 3},
        max_pool_connections=50
    )

    model_id = "qwen.qwen3-coder-30b-a3b-v1:0"
    print(f"[DEBUG] Invoking Bedrock model: {model_id}")

    async with session.client("bedrock-runtime", region_name=LLM_REGION, config=config) as client:
        print("[DEBUG] Building Qwen chat request...")
        request_body = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 15000,
            "temperature": 0.1,
            "top_p": 0.9
        }

        print("[DEBUG] Sending request to Bedrock...")

        response = await client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )

        print("[DEBUG] Response received, reading body...")

        body_content = await response["body"].read()
        parsed = json.loads(body_content)

        output_text = parsed.get("output_text") \
            or parsed.get("response", "") \
            or parsed.get("choices", [{}])[0].get("message", {}).get("content", "")

        print(f"[DEBUG] Model output (truncated): {str(output_text)[:200]}")
        return output_text
