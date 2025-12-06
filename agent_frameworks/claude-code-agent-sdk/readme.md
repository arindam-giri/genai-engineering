# Claude code setup instructions
- Sample command to enable claude code via AWS bedrock
- Copy directly and paste in terminal before running `claude`
```
export CLAUDE_CODE_USE_BEDROCK=1 && \
export AWS_REGION=us-east-1 && \
export AWS_PROFILE=arindam_linux && \
export ANTHROPIC_MODEL=global.anthropic.claude-sonnet-4-20250514-v1:0 && \
export ANTHROPIC_SMALL_FAST_MODEL=us.anthropic.claude-3-5-haiku-20241022-v1:0 && \
export DISABLE_PROMPT_CACHING=1
```
