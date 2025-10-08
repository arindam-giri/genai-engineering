# Test Bedrock connection directly before using the SDK
from anthropic import AnthropicBedrock
import boto3
import logging
import os
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

boto3.setup_default_session(profile_name="arindam_linux")

# Verify AWS credentials are set
session = boto3.Session(profile_name="arindam_linux")
credentials = session.get_credentials()
logger.info(f"AWS Region: {session.region_name}")
logger.info(f"AWS Credentials loaded: {credentials is not None}")

bedrock = AnthropicBedrock(aws_region="us-east-1")
response = bedrock.messages.create(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hello"}]
)
print(response.content[0].text)