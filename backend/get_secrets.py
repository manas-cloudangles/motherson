import asyncio
import random
import boto3
from botocore.config import Config
import json
import sys
import aioboto3
import os
import aiohttp
from botocore.exceptions import ClientError


# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Make sure this exists

# async def run_model(system_prompt: str, user_message: str):
#     """
#     Run a model call using OpenAI API compatible endpoint.
#     """

#     system_prompt = """
# You are an expert AI trained to analyze software product documentation (PRDs). You will be given a Product Requirements Document as input. Your task is to determine the single **primary user role** the application is intended for and produce a concise, evidence-based justification in the exact format below.

# REQUIREMENTS:
# 1. Read the entire PRD (user stories, goals, features, usage scenarios, functional requirements, flows, and any FR codes).
# 2. Identify **one** primary user role (e.g., Customer, Admin, Manager, Vendor, Technician, Support Agent). The role must be explicitly stated or clearly implied by the PRD. If the PRD does not support a definitive primary role, output "Unable to determine primary user role from the PRD." and briefly (1–2 sentences) explain why.
# 3. Do **not** invent facts, do not speculate, and do not use information not present in the PRD.
# 4. When naming the role, use Title Case and one-word or short phrase (e.g., Customer, Admin).
# 5. Provide justification by citing specific PRD elements (exact phrases, quoted snippets, flow names, or FR codes such as FR1.1, FR2.3 whenever present).
# 6. Keep the output limited to the structured format below. **Do not add any extra commentary or analysis outside this format.**

# OUTPUT FORMAT (exactly):
# **Primary User Role: <Role>**\n\n**Justification:**\n\n<One short lead sentence stating why this role is primary (1–2 sentences).>\n\n1. **<Evidence title>**: <Quoted or referenced PRD text or FR code and short explanation of how it supports the role.>\n\n2. **<Evidence title>**: <Quoted or referenced PRD text or FR code and short explanation.>\n\n3. **<Evidence title>**: <...>\n\n(Include as many numbered evidence items as needed — usually 3–5 — each referencing specific PRD elements.)\n\n<One final concluding sentence reaffirming that the app's functionality targets the identified role and noting absence of other role-focused features if applicable.>

# EXAMPLES OF ACCEPTABLE EVIDENCE:
# - Direct quotes from PRD such as "Users aged 15–45" or "Order confirmation with tracking numbers."
# - Named flows like "Pizza Selection → Customization → Delivery Details → Checkout."
# - FR codes like FR1.1, FR2.4 linked to actions (browsing, ordering, customizing, checkout).

# If the PRD explicitly shows multiple primary audiences with equal weighting, output "Unable to determine primary user role from the PRD." and explain which roles are tied and which parts of the PRD support them (1–2 sentences).

# Remember: produce **only** the formatted result exactly as specified above.

# """
#     url = "https://phoenix-engine.loca.lt/v1/chat/completions"

#     headers = {
#         "Content-Type": "application/json",
#     }

#     data = {
#         "model": "qwen/qwen3-next-80b",  # Update based on model list
#         "messages": [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_message}
#         ],
#         "temperature": 0.3,      # Optional
#         "max_tokens": 15000      # Optional
#     }

#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, headers=headers, json=data) as resp:
#             if resp.status != 200:
#                 text = await resp.text()
#                 raise RuntimeError(f"API Error {resp.status}: {text}")

#             response_json = await resp.json()

#             print(response_json)
#             # Extract completion text
#             return response_json["choices"][0]["message"]["content"]

def get_secret(secret_name, region_name="ap-south-1"):
    """
    Fetch a secret value from AWS Secrets Manager.
    """
    try:
        # Use default credential chain - no profile specified
        client = boto3.client("secretsmanager", region_name="us-east-1")
        response = client.get_secret_value(SecretId=secret_name)

        if "SecretString" in response:
            secret = response["SecretString"]
            return json.loads(secret)  # Expecting JSON format
        else:
            print("Secret is not a string (binary not supported).")
            sys.exit(1)

    except Exception as e:
        print(f"Error fetching secret: {e}")

def create_client(region_name="us-east-1"):
    """
    Create a Bedrock client.
    """
    try:
        # Use default credential chain - no profile specified
        session = boto3.Session(
            profile_name='cloudangles-mlops', 
            region_name=region_name)
        client = session.client("bedrock-runtime", region_name=region_name)
        return client
    except Exception as e:
        print(f"Error creating Bedrock client: {e}")
        sys.exit(1)


# -- anthropic--
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

async def run_model(system_prompt: str, user_message: str):
    """
    Run a model call to Bedrock with given prompts.
    """

    # Use default credential chain - no profile specified
    session = aioboto3.Session(
        profile_name="cloudangles-mlops",
        region_name="us-east-1"
    )

    config = Config(
        read_timeout=100000,
        connect_timeout=60,
        retries={'max_attempts': 3 , 
                 "mode": "adaptive"
                 },
        max_pool_connections=50
    )
    # Use the client as an async context manager
    async with session.client("bedrock-runtime", region_name="us-east-1", config=config) as client:
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 35000,
            "temperature": 0.1,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}]
        }
        response = await retry_bedrock(client.invoke_model,
            modelId="arn:aws:bedrock:us-east-1:807923266708:inference-profile/global.anthropic.claude-sonnet-4-20250514-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )

        # print(f"Response received, reading body...,{response}")

        # Read the response body
        body_content = await response["body"].read()

        parsed = json.loads(body_content)
        return parsed["content"][0]["text"]


# --qwen--

# DEFAULT_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "qwen.qwen3-coder-30b-a3b-v1:0")

async def run_model_qwen(system_prompt: str, user_message: str):
    print("[DEBUG] Entered run_model()")

    session = aioboto3.Session(
        profile_name="cloudangles-mlops",
        region_name="us-east-1"
    )

    config = Config(
        read_timeout=100000,
        connect_timeout=60000,
        retries={'max_attempts': 3},
        max_pool_connections=50
    )

    # model_id = DEFAULT_MODEL_ID.lower()
    model_id = "qwen.qwen3-coder-30b-a3b-v1:0"
    print(f"[DEBUG] Invoking Bedrock model: {model_id}")

    async with session.client("bedrock-runtime", region_name="us-east-1", config=config) as client:

        if model_id.startswith("qwen."):
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
        else:
            raise ValueError(f"Unsupported model ID: {model_id}")

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

def check_aws_credentials():
    """
    Helper function to check available AWS credentials and profiles
    """
    print("=== AWS Credential Check ===")

    # Check environment variables
    print("\n1. Environment Variables:")
    env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN',
                'AWS_PROFILE', 'AWS_DEFAULT_REGION']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'TOKEN' in var:
                print(f"  {var}: ***SET*** (length: {len(value)})")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: Not set")

    # Check available profiles
    print("\n2. Available Profiles:")
    try:
        session = boto3.Session()
        profiles = session.available_profiles
        if profiles:
            for profile in profiles:
                print(f"  - {profile}")
        else:
            print("  No profiles found in ~/.aws/config")
    except Exception as e:
        print(f"  Error checking profiles: {e}")

    # Check current credentials
    print("\n3. Current Credentials:")
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials:
            print(f"  Access Key: ***{credentials.access_key[-4:] if credentials.access_key else 'None'}")
            print(f"  Has Secret Key: {'Yes' if credentials.secret_key else 'No'}")
            print(f"  Has Token: {'Yes' if credentials.token else 'No'}")

            # Try to get caller identity
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            print(f"  Account: {identity['Account']}")
            print(f"  User/Role ARN: {identity['Arn']}")
        else:
            print("  No credentials found")
    except Exception as e:
        print(f"  Error checking credentials: {e}")

    print("=" * 30)

if __name__ == "__main__":
    # Check AWS credentials (optional - remove in production)
    check_aws_credentials()

    secret_name = "codebenders-dev"   # your secret name
    region_name = "us-east-1"      # change if needed

    secret = get_secret(secret_name, region_name)
    print(secret)
    print("✅ Secret fetched successfully:")


