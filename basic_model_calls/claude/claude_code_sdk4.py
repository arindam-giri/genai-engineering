"""
Basic Example of using the Claude Agent SDK with Bedrock integration.
This example sets up the environment to use AWS Bedrock and queries the model.
Author: Arindam Giri
Date: October 2025
"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions
import os
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():

    os.environ["CLAUDE_CODE_USE_BEDROCK"] = "1"
    
    # Optional: Set AWS credentials via environment variables (if not using profile)
    # os.environ["AWS_ACCESS_KEY_ID"] = "xx"
    # os.environ["AWS_SECRET_ACCESS_KEY"] = "xx"
    os.environ["AWS_REGION"] = "us-east-1"
    # os.environ["AWS_BEARER_TOKEN_BEDROCK"] = "xx"
    os.environ["ANTHROPIC_MODEL"] = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
    os.environ["ANTHROPIC_SMALL_FAST_MODEL"] = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    os.environ["DISABLE_PROMPT_CACHING"] = "1"
    os.environ["AWS_PROFILE"] = "arindam_linux"
    # Set up boto3 session with your AWS profile
    # boto3.setup_default_session(profile_name="arindam_linux")
        #     
    options = ClaudeAgentOptions(
        system_prompt="You are an helpfull AI assistant"
    )

    async for message in query(
        prompt="Tell me a joke.",
        options=options
    ):
        print(message)


asyncio.run(main())