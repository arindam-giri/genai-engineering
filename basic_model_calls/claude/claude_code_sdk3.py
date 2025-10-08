#!/usr/bin/env python3
"""
Simple test of Claude Agent SDK with AWS Bedrock
"""
import asyncio
import logging
import boto3
import os
from claude_agent_sdk import query, ClaudeAgentOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_with_timeout():
    """Test with explicit timeout to avoid hanging"""
    try:
        # CRITICAL: Enable Bedrock mode
        os.environ["CLAUDE_CODE_USE_BEDROCK"] = "1"
        
        # Set up AWS
        boto3.setup_default_session(profile_name="arindam_linux")
        os.environ["AWS_REGION"] = "us-east-1"
        
        logger.info("Starting Claude Agent SDK with Bedrock...")
        
        # Simple options - minimal configuration
        options = ClaudeAgentOptions(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",
            permission_mode='bypassPermissions',  # Bypass permissions for testing
            max_turns=1,  # Only allow 1 turn
            allowed_tools=[]  # No tools for this simple test
        )
        
        # Very simple prompt that doesn't require tools
        test_prompt = "Say 'Hello from Bedrock!' and nothing else."
        
        logger.info(f"Prompt: {test_prompt}")
        print("="*60)
        
        # Set a timeout for the entire query
        message_count = 0
        try:
            async def run_query():
                nonlocal message_count
                async for message in query(prompt=test_prompt, options=options):
                    message_count += 1
                    print(f"\n[Message {message_count}]")
                    print(f"Type: {type(message).__name__}")
                    
                    # Print relevant parts based on message type
                    if hasattr(message, 'subtype'):
                        print(f"Subtype: {message.subtype}")
                    
                    if hasattr(message, 'content'):
                        print(f"Content: {message.content}")
                    
                    # Check for completion
                    if hasattr(message, 'subtype') and message.subtype in ['success', 'error', 'result']:
                        print(f"\n✓ Got final message: {message.subtype}")
                        return
                    
                    print("-"*60)
            
            # Run with 30 second timeout
            await asyncio.wait_for(run_query(), timeout=30.0)
            
        except asyncio.TimeoutError:
            logger.error("⏱️  Request timed out after 30 seconds")
            logger.error(f"Received {message_count} messages before timeout")
            print("\n🔍 Debug: The SDK is likely waiting for tool execution or user input")
            print("This might be a limitation with how Claude Agent SDK handles Bedrock")
            return
        
        print("="*60)
        logger.info(f"✓ Completed! Total messages: {message_count}")
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_direct_bedrock():
    """Test direct Bedrock call to verify it works"""
    logger.info("\n\n📝 Testing direct Bedrock call (for comparison)...")
    
    boto3.setup_default_session(profile_name="arindam_linux")
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    
    import json
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "messages": [{"role": "user", "content": [{"type": "text", "text": "Say hello"}]}],
    }
    
    try:
        response = client.invoke_model(
            modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
            body=json.dumps(native_request)
        )
        model_response = json.loads(response["body"].read())
        print(f"Direct Bedrock response: {model_response['content'][0]['text']}")
        print("✓ Direct Bedrock call successful!\n")
    except Exception as e:
        print(f"❌ Direct Bedrock call failed: {e}\n")

async def main():
    # First verify direct Bedrock works
    await test_direct_bedrock()
    
    # Then test with Agent SDK
    await test_with_timeout()

if __name__ == "__main__":
    asyncio.run(main())