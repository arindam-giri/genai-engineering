"""
Validation module for checking mandatory fields before ServiceNow incident creation.
"""
from typing import Dict, List, Tuple
from pydantic import BaseModel


class ValidationResult(BaseModel):
    """Represents the result of incident data validation."""

    is_valid: bool
    missing_fields: List[str] = []
    validation_errors: List[str] = []
    incident_data: Dict = {}


class IncidentData(BaseModel):
    """Structured format for ServiceNow incident."""

    short_description: str
    assignment_group: str
    priority: str
    category: str
    impact: str
    urgency: str
    description: str = ""
    u_job_id: str = ""
    u_failure_count: int = 0
    u_last_failure_time: str = ""
    contact_type: str = "Monitoring"


class IncidentValidator:
    """Validates incident data before ServiceNow submission."""

    # Mandatory fields required for ServiceNow incident creation
    MANDATORY_FIELDS = [
        "short_description",
        "assignment_group",
        "priority",
        "category",
        "impact",
        "urgency"
    ]

    @staticmethod
    def validate_mandatory_fields(incident_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate that all mandatory fields are present and non-empty.

        Args:
            incident_data: Dictionary containing incident data

        Returns:
            Tuple of (is_valid, list_of_missing_fields)
        """
        missing_fields = []

        for field in IncidentValidator.MANDATORY_FIELDS:
            if field not in incident_data or not incident_data[field]:
                missing_fields.append(field)

        return len(missing_fields) == 0, missing_fields

    @staticmethod
    def validate_field_values(incident_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate that field values meet ServiceNow requirements.

        Args:
            incident_data: Dictionary containing incident data

        Returns:
            Tuple of (is_valid, list_of_validation_errors)
        """
        errors = []

        # Validate priority (should be 1-5)
        priority = incident_data.get("priority")
        if priority:
            try:
                priority_int = int(priority)
                if priority_int < 1 or priority_int > 5:
                    errors.append(f"Priority must be between 1-5, got: {priority}")
            except ValueError:
                errors.append(f"Priority must be numeric, got: {priority}")

        # Validate impact (should be 1-3)
        impact = incident_data.get("impact")
        if impact:
            try:
                impact_int = int(impact)
                if impact_int < 1 or impact_int > 3:
                    errors.append(f"Impact must be between 1-3, got: {impact}")
            except ValueError:
                errors.append(f"Impact must be numeric, got: {impact}")

        # Validate urgency (should be 1-3)
        urgency = incident_data.get("urgency")
        if urgency:
            try:
                urgency_int = int(urgency)
                if urgency_int < 1 or urgency_int > 3:
                    errors.append(f"Urgency must be between 1-3, got: {urgency}")
            except ValueError:
                errors.append(f"Urgency must be numeric, got: {urgency}")

        # Validate short_description length (max 160 chars for ServiceNow)
        short_desc = incident_data.get("short_description", "")
        if len(short_desc) > 160:
            errors.append(f"Short description exceeds 160 characters: {len(short_desc)} chars")

        return len(errors) == 0, errors

    @staticmethod
    def transform_job_to_incident(job_data: Dict) -> Dict:
        """
        Transform batch job data into ServiceNow incident format.

        Args:
            job_data: Dictionary containing batch job data

        Returns:
            Dictionary formatted for ServiceNow incident creation
        """
        incident_data = {
            "short_description": f"Batch Job Failure: {job_data.get('job_name', 'Unknown')} (ID: {job_data.get('job_id', 'Unknown')})",
            "description": job_data.get("description", f"Job {job_data.get('job_name')} has failed {job_data.get('failure_count')} times. Last error: {job_data.get('error_message')}"),
            "assignment_group": job_data.get("assignment_group"),
            "priority": job_data.get("priority"),
            "category": job_data.get("category"),
            "impact": job_data.get("impact"),
            "urgency": job_data.get("urgency"),
            "u_job_id": job_data.get("job_id"),
            "u_failure_count": job_data.get("failure_count"),
            "u_last_failure_time": job_data.get("last_failure_time"),
            "contact_type": "Monitoring"
        }

        return incident_data

    @staticmethod
    def validate_and_transform(job_data: Dict) -> ValidationResult:
        """
        Complete validation: transform job data and validate all fields.

        Args:
            job_data: Dictionary containing batch job data

        Returns:
            ValidationResult with status and details
        """
        # Transform job data to incident format
        incident_data = IncidentValidator.transform_job_to_incident(job_data)

        # Validate mandatory fields
        is_valid_fields, missing_fields = IncidentValidator.validate_mandatory_fields(incident_data)

        if not is_valid_fields:
            return ValidationResult(
                is_valid=False,
                missing_fields=missing_fields,
                incident_data=incident_data
            )

        # Validate field values
        is_valid_values, validation_errors = IncidentValidator.validate_field_values(incident_data)

        if not is_valid_values:
            return ValidationResult(
                is_valid=False,
                validation_errors=validation_errors,
                incident_data=incident_data
            )

        # All validations passed
        return ValidationResult(
            is_valid=True,
            incident_data=incident_data
        )
