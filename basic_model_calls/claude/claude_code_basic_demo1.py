import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # AWS Bedrock Configuration
    os.environ["CLAUDE_CODE_USE_BEDROCK"] = "1"
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["ANTHROPIC_MODEL"] = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
    os.environ["ANTHROPIC_SMALL_FAST_MODEL"] = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    os.environ["DISABLE_PROMPT_CACHING"] = "1"
    os.environ["AWS_PROFILE"] = "arindam_linux"
    
    # Create a test directory and files for the agent to work with
    test_dir = "./test_workspace"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create sample files
    with open(f"{test_dir}/sample.txt", "w") as f:
        f.write("This is a sample text file for testing.")
    
    with open(f"{test_dir}/data.json", "w") as f:
        f.write('{"name": "test", "value": 42}')
    
    print("=" * 80)
    print("CLAUDE CODE AGENT SDK - COMPREHENSIVE TOOL DEMO")
    print("=" * 80)
    
    # Example 1: File Operations (read, write, edit)
    print("\n### Example 1: File Operations ###")
    options1 = ClaudeAgentOptions(
        system_prompt="You are a helpful file management assistant.",
        working_directory=test_dir,
        enable_file_operations=True
    )
    
    async for message in query(
        prompt="""Read the sample.txt file, then create a new file called 'output.txt' 
        with the content in uppercase. Also list all files in the directory.""",
        options=options1
    ):
        print(f"[File Ops] {message}")
    
    print("\n" + "-" * 80)
    
    # Example 2: Shell Commands (bash execution)
    print("\n### Example 2: Shell Command Execution ###")
    options2 = ClaudeAgentOptions(
        system_prompt="You are a helpful system administrator assistant.",
        working_directory=test_dir,
        enable_shell_commands=True,
        enable_file_operations=True
    )
    
    async for message in query(
        prompt="""Use shell commands to:
        1. List all files with their sizes
        2. Count the number of lines in sample.txt
        3. Show the current directory path""",
        options=options2
    ):
        print(f"[Shell] {message}")
    
    print("\n" + "-" * 80)
    
    # Example 3: Code Execution (Python)
    print("\n### Example 3: Python Code Execution ###")
    options3 = ClaudeAgentOptions(
        system_prompt="You are a helpful Python programming assistant.",
        working_directory=test_dir,
        enable_code_execution=True,
        enable_file_operations=True
    )
    
    async for message in query(
        prompt="""Write and execute a Python script that:
        1. Reads data.json file
        2. Parses the JSON
        3. Calculates the square of the 'value' field
        4. Writes the result to a new file called 'result.txt'""",
        options=options3
    ):
        print(f"[Code Exec] {message}")
    
    print("\n" + "-" * 80)
    
    # Example 4: Web Search
    print("\n### Example 4: Web Search ###")
    options4 = ClaudeAgentOptions(
        system_prompt="You are a helpful research assistant with web search capabilities.",
        enable_web_search=True
    )
    
    async for message in query(
        prompt="Search the web for the latest Python 3.13 release date and major features.",
        options=options4
    ):
        print(f"[Web Search] {message}")
    
    print("\n" + "-" * 80)
    
    # Example 5: Multi-tool Complex Task
    print("\n### Example 5: Complex Multi-Tool Task ###")
    options5 = ClaudeAgentOptions(
        system_prompt="You are a versatile AI assistant with access to multiple tools.",
        working_directory=test_dir,
        enable_file_operations=True,
        enable_shell_commands=True,
        enable_code_execution=True,
        enable_web_search=True,
        max_iterations=10  # Allow multiple tool uses
    )
    
    async for message in query(
        prompt="""Create a comprehensive report:
        1. Search for the current Python version
        2. Create a Python script that generates a system info report
        3. Execute the script to collect: OS info, Python version, current timestamp
        4. Save the report to 'system_report.txt'
        5. Use shell commands to show the file size and content""",
        options=options5
    ):
        print(f"[Multi-Tool] {message}")
    
    print("\n" + "-" * 80)
    
    # Example 6: Interactive conversation with context
    print("\n### Example 6: Multi-turn Conversation ###")
    options6 = ClaudeAgentOptions(
        system_prompt="You are a helpful coding tutor.",
        working_directory=test_dir,
        enable_file_operations=True,
        enable_code_execution=True,
        conversation_history=[]  # Maintains context across queries
    )
    
    # First query
    print("\n[Turn 1]")
    async for message in query(
        prompt="Create a simple Python function to calculate factorial and save it to factorial.py",
        options=options6
    ):
        print(message)
    
    # Second query - builds on first
    print("\n[Turn 2]")
    async for message in query(
        prompt="Now test the factorial function with the numbers 5 and 10",
        options=options6
    ):
        print(message)
    
    print("\n" + "-" * 80)
    
    # Example 7: Error Handling and Recovery
    print("\n### Example 7: Error Handling ###")
    options7 = ClaudeAgentOptions(
        system_prompt="You are a careful assistant that handles errors gracefully.",
        working_directory=test_dir,
        enable_file_operations=True,
        enable_code_execution=True,
        max_retries=3
    )
    
    async for message in query(
        prompt="""Try to read a file called 'nonexistent.txt'. 
        If it doesn't exist, create it with some sample content, then read it.""",
        options=options7
    ):
        print(f"[Error Handling] {message}")
    
    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED!")
    print("=" * 80)
    
    # Cleanup (optional)
    print("\nTest files created in:", test_dir)
    print("You can inspect the files or delete the directory when done.")

if __name__ == "__main__":
    asyncio.run(main())