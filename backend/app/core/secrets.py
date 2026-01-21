import boto3
import json
import sys
from app.core.config import LLM_REGION

def get_secret(secret_name, region_name=LLM_REGION):
    """
    Fetch a secret value from AWS Secrets Manager.
    """
    try:
        # Use default credential chain
        client = boto3.client("secretsmanager", region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)

        if "SecretString" in response:
            secret = response["SecretString"]
            return json.loads(secret)  # Expecting JSON format
        else:
            print("Secret is not a string (binary not supported).")
            sys.exit(1)

    except Exception as e:
        print(f"Error fetching secret: {e}")
