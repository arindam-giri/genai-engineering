#!/usr/bin/env python3
"""
Test Claude Agent SDK with AWS Bedrock
Configures claude_agent_sdk to use Claude 4 via AWS Bedrock
"""
import asyncio
import logging
import boto3
import os
from claude_agent_sdk import query, ClaudeAgentOptions
from anthropic import AnthropicBedrock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Test claude_agent_sdk using AWS Bedrock as the model provider"""
    try:
        # CRITICAL: Set environment variable to enable Bedrock
        os.environ["CLAUDE_CODE_USE_BEDROCK"] = "1"
        
        # Optional: Set AWS credentials via environment variables (if not using profile)
        # os.environ["AWS_ACCESS_KEY_ID"] = "your_access_key_here"
        # os.environ["AWS_SECRET_ACCESS_KEY"] = "your_secret_key_here"
        # os.environ["AWS_REGION"] = "us-east-1"
        
        # Set up boto3 session with your AWS profile
        boto3.setup_default_session(profile_name="arindam_linux")
        
        logger.info("Initializing with Bedrock (CLAUDE_CODE_USE_BEDROCK=1)...")
        
        # Set AWS region for Bedrock
        os.environ["AWS_REGION"] = "us-east-1"  # Change to your preferred region
        
        # Verify AWS credentials are set
        session = boto3.Session(profile_name="arindam_linux")
        credentials = session.get_credentials()
        logger.info(f"AWS Region: {session.region_name}")
        logger.info(f"AWS Credentials loaded: {credentials is not None}")
        
        # Configure Claude Agent options
        options = ClaudeAgentOptions(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",  # Bedrock ARN format
            system_prompt="You are an expert Python developer",
            permission_mode='acceptEdits',
            cwd=".",  # Current directory
            allowed_tools=["Read", "Write", "Bash"],
            max_turns=5  # Limit turns to avoid infinite loops
        )
        
        # Test prompt
        test_prompt = "Write a simple Python function to calculate factorial of a number and save it to factorial.py"
        
        logger.info(f"Sending prompt: {test_prompt}")
        print("="*50)
        
        # Add timeout to avoid hanging
        try:
            # Query Claude Agent SDK with Bedrock with timeout
            message_count = 0
            async for message in query(
                prompt=test_prompt,
                options=options
            ):
                print(f"\nMessage {message_count + 1}:")
                print(message)
                print("-" * 40)
                message_count += 1
                
                # Break if we get a result message
                if hasattr(message, 'subtype') and message.subtype in ['success', 'error']:
                    logger.info(f"Received final message: {message.subtype}")
                    break
        except asyncio.TimeoutError:
            logger.error("Request timed out!")
            print("\nPossible issues:")
            print("1. Check AWS Bedrock model access is enabled")
            print("2. Verify the model ARN is correct for your region")
            print("3. Check AWS credentials have Bedrock permissions")
            return
        
        print("="*50)
        logger.info("✓ Successfully called Claude Agent SDK via AWS Bedrock!")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Install: pip install anthropic[bedrock] claude-agent-sdk")
        print("2. Ensure AWS profile 'arindam_linux' exists in ~/.aws/credentials")
        print("3. Ensure Bedrock model access is enabled in AWS Console")
        print("4. Check your AWS region supports Claude 4")

if __name__ == "__main__":
    asyncio.run(main())