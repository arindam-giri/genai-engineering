# Microsoft Agent Framework V2 - ServiceNow Incident Creation with Conditional Routing

This implementation uses the **official Microsoft Agent Framework** patterns from the `edge_condition.py` sample, demonstrating conditional routing and control flow for automated ServiceNow incident creation based on batch job failures.

## Key Differences from V1

This V2 implementation follows the official Microsoft Agent Framework patterns:

| Feature | V1 (Custom) | V2 (Official MAF) |
|---------|-------------|-------------------|
| **Agent Creation** | Custom `ChatAgent` class | `AgentExecutor` with `create_agent()` |
| **Client** | Placeholder `AzureOpenAIChatClient` | Real `AzureOpenAIChatClient` from `agent_framework.azure` |
| **Workflow** | Custom sequential executor | `WorkflowBuilder` with edge conditions |
| **Control Flow** | Sequential with error checks | Conditional routing with edge predicates |
| **Authentication** | Hardcoded credentials | `AzureCliCredential` |
| **Structured Output** | Manual parsing | Pydantic `response_format` |
| **Execution** | Synchronous | Async with `asyncio` |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              WorkflowBuilder with Edge Conditions           │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Job Query    │    │  Validation  │    │  ServiceNow  │
│ Agent        │───▶│    Agent     │───▶│    Agent     │
│              │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        │                    │                    │
        ▼                    ▼                    ▼
 [Has Jobs?]          [Is Valid?]          [Create Inc]
        │                    │                    │
    True│False          True│False               │
        │                    │                    │
        ▼                    ▼                    ▼
  [Continue]         [Continue│Error]      [Success Handler]
```

## Workflow Flow with Edge Conditions

1. **Job Query Agent** → Returns `JobQueryResult`
   - **Edge Condition**: `has_failed_jobs == True` → Continue to validation
   - **Edge Condition**: `has_failed_jobs == False` → Handle "no jobs" message

2. **Validation Agent** → Returns `ValidationResult`
   - **Edge Condition**: `is_valid == True` → Continue to ServiceNow
   - **Edge Condition**: `is_valid == False` → Handle validation failure

3. **ServiceNow Agent** → Returns `IncidentCreationResult`
   - Always routes to success handler
   - Handler checks `success` field and yields appropriate message

## Key Components

### 1. Pydantic Models (Structured Outputs)

```python
class ValidationResult(BaseModel):
    is_valid: bool
    missing_fields: List[str] = []
    validation_errors: List[str] = []
    incident_data: Dict = {}
```

All agents use `response_format` parameter to enforce structured JSON output, making parsing safe and predictable.

### 2. Edge Conditions

```python
def get_validation_condition(expected_valid: bool):
    def condition(message: Any) -> bool:
        if not isinstance(message, AgentExecutorResponse):
            return True
        try:
            validation = ValidationResult.model_validate_json(
                message.agent_run_response.text
            )
            return validation.is_valid == expected_valid
        except Exception:
            return False
    return condition
```

Edge conditions enable branching logic based on agent outputs.

### 3. Executor Decorators

```python
@executor(id="handle_validation_failure")
async def handle_validation_failure(
    response: AgentExecutorResponse,
    ctx: WorkflowContext[Never, str]
) -> None:
    validation = ValidationResult.model_validate_json(
        response.agent_run_response.text
    )
    await ctx.yield_output(f"Validation failed: {validation.missing_fields}")
```

Executors are workflow steps that can:
- Transform data between agents
- Handle terminal states
- Yield workflow outputs

### 4. Workflow Builder

```python
workflow = (
    WorkflowBuilder()
    .set_start_executor(job_query_agent)
    # Valid path
    .add_edge(validation_agent, transform_to_snow_request,
              condition=get_validation_condition(True))
    # Invalid path
    .add_edge(validation_agent, handle_validation_failure,
              condition=get_validation_condition(False))
    .build()
)
```

Declarative workflow construction with conditional edges.

## Project Structure

```
MAF_demo_v2/
├── incident_workflow.py         # Main workflow with edge conditions
├── requirements.txt              # Dependencies
├── README.md                     # This file
├── config/                       # Configuration files
├── resources/
│   └── sample_job.json          # Sample job data
└── src/
    └── modules/
        ├── database.py          # Database operations
        ├── servicenow.py        # ServiceNow API client
        └── validator.py         # Data validation with Pydantic
```

## Prerequisites

### 1. Azure Setup

- Azure OpenAI resource with GPT-4 deployment
- Azure CLI installed and authenticated: `az login`
- Environment variables set:

```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="gpt-4"
```

### 2. Python Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Installation

```bash
# Install Microsoft Agent Framework
pip install agent-framework

# Install Azure dependencies
pip install azure-identity azure-core

# Install Pydantic for structured outputs
pip install pydantic
```

## Usage

### Run the Workflow

```bash
cd MAF_demo_v2
python incident_workflow.py
```

### Expected Output

```
================================================================================
 Microsoft Agent Framework - ServiceNow Incident Creation with Edge Conditions
================================================================================

🔄 Demo 1: Processing job with complete data (JOB_001)
--------------------------------------------------------------------------------

✅ ServiceNow incident created successfully: INC0001234

================================================================================
🔄 Demo 2: Processing job with missing mandatory fields (JOB_004)
--------------------------------------------------------------------------------

❌ Incident creation failed - Validation errors:
  Missing fields: impact, urgency
  Validation errors:
    - Priority must be between 1-5, got: 2

================================================================================
✅ Workflow demonstration completed
================================================================================
```

## Workflow Execution Details

### Demo 1: Successful Flow

1. **Job Query Agent** finds JOB_001 (12 failures)
2. **Edge Condition** routes to validation (has_failed_jobs=True)
3. **Validation Agent** validates all fields pass
4. **Edge Condition** routes to ServiceNow (is_valid=True)
5. **ServiceNow Agent** creates incident INC0001234
6. **Success Handler** yields success message

### Demo 2: Validation Failure

1. **Job Query Agent** finds JOB_004 (20 failures)
2. **Edge Condition** routes to validation (has_failed_jobs=True)
3. **Validation Agent** finds missing fields: impact, urgency
4. **Edge Condition** routes to error handler (is_valid=False)
5. **Error Handler** yields validation failure message

## Edge Condition Patterns

### Pattern 1: Boolean Field Routing

```python
# Route based on boolean flag in response
condition=get_validation_condition(True)   # Route when valid
condition=get_validation_condition(False)  # Route when invalid
```

### Pattern 2: Data Presence Routing

```python
# Route based on whether data exists
condition=get_job_query_condition(True)   # Route when jobs found
condition=get_job_query_condition(False)  # Route when no jobs
```

### Pattern 3: Value-Based Routing

```python
def get_priority_condition(expected_priority: str):
    def condition(message: Any) -> bool:
        result = IncidentData.model_validate_json(message.agent_run_response.text)
        return result.priority == expected_priority
    return condition
```

## Customization

### Add New Validation Rule

```python
# In modules/validator.py
MANDATORY_FIELDS = [
    "short_description",
    "assignment_group",
    "priority",
    "category",
    "impact",
    "urgency",
    "your_custom_field"  # Add here
]
```

### Add New Workflow Path

```python
# Add edge for high-priority incidents
workflow = (
    WorkflowBuilder()
    .set_start_executor(job_query_agent)
    .add_edge(validation_agent, urgent_handler,
              condition=get_priority_condition("1"))
    .add_edge(validation_agent, normal_handler,
              condition=get_priority_condition("2"))
    .build()
)
```

### Add Notification Agent

```python
notification_agent = AgentExecutor(
    chat_client.create_agent(
        instructions="Send notification to team...",
        response_format=NotificationResult,
    ),
    id="notification_agent",
)

workflow = (
    WorkflowBuilder()
    # ... existing edges ...
    .add_edge(servicenow_agent, notification_agent)
    .add_edge(notification_agent, handle_notification)
    .build()
)
```

## Debugging

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Workflow Events

```python
events = await workflow.run(request)
print(f"Events: {events}")
print(f"Outputs: {events.get_outputs()}")
```

### Test Edge Conditions

```python
# Test validation condition directly
from agent_framework import AgentExecutorResponse

mock_response = AgentExecutorResponse(...)
condition_func = get_validation_condition(True)
result = condition_func(mock_response)
print(f"Condition result: {result}")
```

## Comparison: V1 vs V2 Code

### V1: Custom Sequential Workflow

```python
# V1 approach
workflow = SequentialWorkflow(name="Incident Creation")
workflow.add_step("query", db_agent)
workflow.add_step("validate", validation_agent)
workflow.add_step("create", snow_agent)
result = workflow.execute(context)
```

### V2: Microsoft Agent Framework

```python
# V2 approach with conditional routing
workflow = (
    WorkflowBuilder()
    .set_start_executor(job_query_agent)
    .add_edge(job_query_agent, validation_agent,
              condition=get_job_query_condition(True))
    .add_edge(validation_agent, snow_agent,
              condition=get_validation_condition(True))
    .add_edge(validation_agent, error_handler,
              condition=get_validation_condition(False))
    .build()
)
events = await workflow.run(request)
```

## Troubleshooting

### Issue: Authentication Error

```
Error: AzureCliCredential authentication failed
```

**Solution**: Login with Azure CLI
```bash
az login
az account show  # Verify authentication
```

### Issue: Agent Response Parse Error

```
Error: Failed to validate JSON from agent response
```

**Solution**: Check `response_format` matches Pydantic model exactly
```python
# Ensure model fields match agent instructions
response_format=ValidationResult  # Must match returned JSON structure
```

### Issue: Edge Condition Always False

```
Warning: Workflow terminates early, no edges activate
```

**Solution**: Add defensive guards in conditions
```python
def condition(message: Any) -> bool:
    if not isinstance(message, AgentExecutorResponse):
        return True  # Allow edge to pass
    # ... rest of condition
```

## References

- [Microsoft Agent Framework Documentation](https://learn.microsoft.com/en-us/agent-framework/)
- [Edge Condition Sample (Source)](https://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/workflows/control-flow/edge_condition.py)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## License

This is a demonstration project based on Microsoft Agent Framework samples.
