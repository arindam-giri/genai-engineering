# Copyright (c) Microsoft. All rights reserved.

"""
ServiceNow Incident Creation Workflow with Conditional Routing

This workflow demonstrates:
- Querying batch jobs from database based on failure threshold
- Validating incident data with conditional routing
- Creating ServiceNow incidents only when validation passes
- Handling validation failures with appropriate error messages

The workflow uses Microsoft Agent Framework patterns:
- AgentExecutor for wrapping LLM agents
- WorkflowBuilder for wiring executors and edges
- Edge conditions for conditional routing based on validation results
- Pydantic models for structured outputs
- Executor decorators for custom workflow steps
"""

import asyncio
import os
import sys
from typing import Any

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agent_framework import (
    AgentExecutor,
    AgentExecutorRequest,
    AgentExecutorResponse,
    ChatMessage,
    Role,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from pydantic import BaseModel
from typing_extensions import Never

from modules.database import BatchJobDatabase
from modules.servicenow import ServiceNowClient
from modules.validator import ValidationResult, IncidentData


# ============================================================================
# Pydantic Models for Structured Outputs
# ============================================================================

class JobQueryResult(BaseModel):
    """Result from database query for failed jobs."""

    has_failed_jobs: bool
    job_count: int
    job_data: dict = {}
    reason: str = ""


class IncidentCreationResult(BaseModel):
    """Result from ServiceNow incident creation."""

    success: bool
    incident_number: str = ""
    error_message: str = ""


# ============================================================================
# Edge Condition Functions
# ============================================================================

def get_validation_condition(expected_valid: bool):
    """
    Create a condition callable that routes based on ValidationResult.is_valid.

    Args:
        expected_valid: True to route on valid data, False to route on invalid data

    Returns:
        Condition function for edge routing
    """

    def condition(message: Any) -> bool:
        # Guard against non-AgentExecutorResponse
        if not isinstance(message, AgentExecutorResponse):
            return True

        try:
            # Parse ValidationResult from agent response
            validation = ValidationResult.model_validate_json(message.agent_run_response.text)
            return validation.is_valid == expected_valid
        except Exception:
            # Fail closed on parse errors
            return False

    return condition


def get_job_query_condition(expected_has_jobs: bool):
    """
    Create a condition callable that routes based on whether jobs were found.

    Args:
        expected_has_jobs: True to route when jobs found, False when no jobs

    Returns:
        Condition function for edge routing
    """

    def condition(message: Any) -> bool:
        if not isinstance(message, AgentExecutorResponse):
            return True

        try:
            query_result = JobQueryResult.model_validate_json(message.agent_run_response.text)
            return query_result.has_failed_jobs == expected_has_jobs
        except Exception:
            return False

    return condition


# ============================================================================
# Workflow Executor Functions
# ============================================================================

@executor(id="handle_validation_failure")
async def handle_validation_failure(
    response: AgentExecutorResponse, ctx: WorkflowContext[Never, str]
) -> None:
    """
    Handle validation failure by yielding error message.

    Args:
        response: Agent response containing ValidationResult
        ctx: Workflow context for yielding output
    """
    validation = ValidationResult.model_validate_json(response.agent_run_response.text)

    error_parts = ["❌ Incident creation failed - Validation errors:"]

    if validation.missing_fields:
        error_parts.append(f"  Missing fields: {', '.join(validation.missing_fields)}")

    if validation.validation_errors:
        error_parts.append(f"  Validation errors:")
        for error in validation.validation_errors:
            error_parts.append(f"    - {error}")

    await ctx.yield_output("\n".join(error_parts))


@executor(id="transform_to_snow_request")
async def transform_to_snow_request(
    response: AgentExecutorResponse, ctx: WorkflowContext[AgentExecutorRequest]
) -> None:
    """
    Transform validated incident data into ServiceNow creation request.

    Args:
        response: Agent response containing ValidationResult
        ctx: Workflow context for sending messages
    """
    validation = ValidationResult.model_validate_json(response.agent_run_response.text)

    if not validation.is_valid:
        raise RuntimeError("This executor should only handle valid incident data.")

    # Create message with incident data for ServiceNow agent
    import json
    incident_json = json.dumps(validation.incident_data)
    user_msg = ChatMessage(Role.USER, text=f"Create ServiceNow incident with data: {incident_json}")
    await ctx.send_message(AgentExecutorRequest(messages=[user_msg], should_respond=True))


@executor(id="handle_incident_creation")
async def handle_incident_creation(
    response: AgentExecutorResponse, ctx: WorkflowContext[Never, str]
) -> None:
    """
    Handle ServiceNow incident creation result.

    Args:
        response: Agent response containing IncidentCreationResult
        ctx: Workflow context for yielding output
    """
    result = IncidentCreationResult.model_validate_json(response.agent_run_response.text)

    if result.success:
        await ctx.yield_output(f"✅ ServiceNow incident created successfully: {result.incident_number}")
    else:
        await ctx.yield_output(f"❌ Failed to create incident: {result.error_message}")


@executor(id="transform_to_validation_request")
async def transform_to_validation_request(
    response: AgentExecutorResponse, ctx: WorkflowContext[AgentExecutorRequest]
) -> None:
    """
    Transform job query result into validation request.

    Args:
        response: Agent response containing JobQueryResult
        ctx: Workflow context for sending messages
    """
    query_result = JobQueryResult.model_validate_json(response.agent_run_response.text)

    if not query_result.has_failed_jobs:
        raise RuntimeError("This executor should only handle results with failed jobs.")

    # Forward job data to validation agent
    import json
    job_json = json.dumps(query_result.job_data)
    user_msg = ChatMessage(Role.USER, text=f"Validate and transform job data: {job_json}")
    await ctx.send_message(AgentExecutorRequest(messages=[user_msg], should_respond=True))


@executor(id="handle_no_jobs")
async def handle_no_jobs(response: AgentExecutorResponse, ctx: WorkflowContext[Never, str]) -> None:
    """
    Handle case where no failed jobs were found.

    Args:
        response: Agent response containing JobQueryResult
        ctx: Workflow context for yielding output
    """
    query_result = JobQueryResult.model_validate_json(response.agent_run_response.text)
    await ctx.yield_output(f"ℹ️  No failed jobs found exceeding threshold. Reason: {query_result.reason}")


# ============================================================================
# Main Workflow
# ============================================================================

async def main() -> None:
    """Main workflow execution."""

    print("\n" + "=" * 80)
    print(" Microsoft Agent Framework - ServiceNow Incident Creation with Edge Conditions")
    print("=" * 80 + "\n")

    # Initialize modules
    db = BatchJobDatabase(db_path="/path/to/batch_jobs.db")
    snow_client = ServiceNowClient(
        instance_url="https://dev12345.service-now.com",
        username="admin",
        password="password"
    )

    # Initialize Azure OpenAI Chat Client
    # Using AzureCliCredential for authentication
    chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())

    # ============================================================================
    # Agent 1: Job Query Agent
    # ============================================================================
    job_query_agent = AgentExecutor(
        chat_client.create_agent(
            instructions=(
                "You are a database query assistant that retrieves failed batch jobs. "
                "Return JSON with fields: has_failed_jobs (bool), job_count (int), "
                "job_data (dict with complete job details), and reason (string). "
                "If jobs are found, include the first job's complete data in job_data."
            ),
            response_format=JobQueryResult,
        ),
        id="job_query_agent",
    )

    # ============================================================================
    # Agent 2: Validation Agent
    # ============================================================================
    validation_agent = AgentExecutor(
        chat_client.create_agent(
            instructions=(
                "You are a data validation assistant for ServiceNow incidents. "
                "Validate that job data contains all mandatory fields: "
                "assignment_group, priority, category, impact, urgency. "
                "Return JSON with fields: is_valid (bool), missing_fields (list), "
                "validation_errors (list), and incident_data (dict). "
                "Transform job data into proper ServiceNow incident format."
            ),
            response_format=ValidationResult,
        ),
        id="validation_agent",
    )

    # ============================================================================
    # Agent 3: ServiceNow Agent
    # ============================================================================
    servicenow_agent = AgentExecutor(
        chat_client.create_agent(
            instructions=(
                "You are a ServiceNow integration assistant that creates incidents. "
                "Return JSON with fields: success (bool), incident_number (string), "
                "and error_message (string if failed)."
            ),
            response_format=IncidentCreationResult,
        ),
        id="servicenow_agent",
    )

    # ============================================================================
    # Build Workflow with Conditional Routing
    # ============================================================================
    workflow = (
        WorkflowBuilder()
        .set_start_executor(job_query_agent)
        # Path 1: Jobs found -> validate
        .add_edge(job_query_agent, transform_to_validation_request, condition=get_job_query_condition(True))
        .add_edge(transform_to_validation_request, validation_agent)
        # Path 2: Validation passed -> create incident
        .add_edge(validation_agent, transform_to_snow_request, condition=get_validation_condition(True))
        .add_edge(transform_to_snow_request, servicenow_agent)
        .add_edge(servicenow_agent, handle_incident_creation)
        # Path 3: Validation failed -> error handler
        .add_edge(validation_agent, handle_validation_failure, condition=get_validation_condition(False))
        # Path 4: No jobs found -> info handler
        .add_edge(job_query_agent, handle_no_jobs, condition=get_job_query_condition(False))
        .build()
    )

    # ============================================================================
    # Execute Workflow - Demo 1: Successful flow with valid job
    # ============================================================================
    print("🔄 Demo 1: Processing job with complete data (JOB_001)")
    print("-" * 80)

    failed_jobs = db.get_failed_jobs(failure_threshold=10)
    if failed_jobs:
        import json
        job_data = failed_jobs[0]
        job_json = json.dumps(job_data)

        request = AgentExecutorRequest(
            messages=[ChatMessage(Role.USER, text=f"Query result: {job_json}")],
            should_respond=True
        )

        events = await workflow.run(request)
        outputs = events.get_outputs()
        if outputs:
            print(f"\n{outputs[0]}\n")

    # ============================================================================
    # Execute Workflow - Demo 2: Validation failure with incomplete job
    # ============================================================================
    print("\n" + "=" * 80)
    print("🔄 Demo 2: Processing job with missing mandatory fields (JOB_004)")
    print("-" * 80)

    job_data_incomplete = db.get_job_by_id("JOB_004")
    if job_data_incomplete:
        import json
        job_json = json.dumps(job_data_incomplete)

        request = AgentExecutorRequest(
            messages=[ChatMessage(Role.USER, text=f"Query result: {job_json}")],
            should_respond=True
        )

        events = await workflow.run(request)
        outputs = events.get_outputs()
        if outputs:
            print(f"\n{outputs[0]}\n")

    # Cleanup
    db.close()

    print("=" * 80)
    print("✅ Workflow demonstration completed")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
