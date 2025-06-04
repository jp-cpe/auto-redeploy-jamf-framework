import os
import logging

from jamf_pro_sdk import JamfProClient, SessionConfig
from jamf_pro_sdk.clients.auth import ApiClientCredentialsProvider
from jamf_pro_sdk.helpers import logger_quick_setup

# Load configuration from environment
JAMF_CLIENT_ID = os.getenv("JAMF_CLIENT_ID")
JAMF_CLIENT_SECRET = os.getenv("JAMF_CLIENT_SECRET")
JAMF_BASE_URL = os.getenv("JAMF_BASE_URL")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO").upper()
if not hasattr(logging, LOGGING_LEVEL):
    LOGGING_LEVEL = "INFO"

# Logging
logger_quick_setup(level=getattr(logging, LOGGING_LEVEL))

# Session config
config = SessionConfig(
    timeout=30,
    max_retries=3,
    max_concurrency=5,
    return_exceptions=True,
    verify=True
)

# Initialize JamfProClient
client = JamfProClient(
    server=JAMF_BASE_URL,
    credentials=ApiClientCredentialsProvider(JAMF_CLIENT_ID, JAMF_CLIENT_SECRET),
    session_config=config
)

def redeploy_framework(computer_ids):
    return client.pro_api.redeploy_management_framework_v1(computer_ids)

def get_computers_in_group(group_id):
    group = client.classic_api.get_computer_group_by_id(group_id)
    return group.computers or []