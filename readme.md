# GenAI Engineering Examples

A collection of code samples and demonstrations for working with Generative AI models, particularly focusing on Claude and AWS Bedrock integration.

## Project Structure

- `basic_model_calls` - Basic examples of calling AI models
  - `claude/` - Direct Claude model invocation examples using AWS Bedrock
    - `claude_invoke_model.py` - Basic model invocation
    - `claude_converse.py` - Conversation API examples

- `agent_frameworks` - Advanced AI agent implementations
  - `claude-code-agent-sdk/` - Examples using Claude Code Agent SDK
    - `claude_code_sdk4.py` - Basic SDK usage
    - `claude_code_tool_demo1.py` - Comprehensive tool demonstrations
    - `excel_analysis_claude_code_agent.py` - Excel analysis agent
    - `claude_code_basic_demo1.py` - Basic feature demonstrations

## Requirements

- Python 3.12+
- AWS Account with Bedrock access
- Configured AWS credentials

## Setup

1. Create a Python virtual environment:
\`\`\`bash
python -m venv venv312
source venv312/bin/activate  # Linux/Mac
\`\`\`

2. Install dependencies:
\`\`\`bash
pip install boto3 anthropic claude-agent-sdk
\`\`\`

3. Configure AWS credentials with Bedrock access

## Usage

Each example file can be run independently. See individual files for specific usage instructions.

## License

MIT
