"""
Example configuration file for MAF Demo V2.
Uses Azure CLI authentication instead of hardcoded credentials.
"""

import os

# Azure OpenAI Configuration
# Set these as environment variables:
# export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
# export AZURE_OPENAI_DEPLOYMENT="gpt-4"
AZURE_OPENAI_CONFIG = {
    "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/"),
    "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
    # Note: Authentication uses AzureCliCredential (az login)
}

# ServiceNow Configuration
# In production, use environment variables or Azure Key Vault
SERVICENOW_CONFIG = {
    "instance_url": os.getenv("SNOW_INSTANCE_URL", "https://dev12345.service-now.com"),
    "username": os.getenv("SNOW_USERNAME", "admin"),
    "password": os.getenv("SNOW_PASSWORD", "password"),
}

# Database Configuration
DATABASE_CONFIG = {
    "db_path": os.getenv("DB_PATH", "/path/to/batch_jobs.db"),
    "failure_threshold": int(os.getenv("FAILURE_THRESHOLD", "10")),
}

# Workflow Configuration
WORKFLOW_CONFIG = {
    "enable_logging": True,
    "log_level": "INFO",
}
