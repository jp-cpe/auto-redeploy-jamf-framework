import os
import logging

# jamf-pro-sdk imports
from jamf_pro_sdk import JamfProClient, SessionConfig
from jamf_pro_sdk.clients.auth import ApiClientCredentialsProvider
from jamf_pro_sdk.helpers import logger_quick_setup

# Environment constants
JAMF_CLIENT_ID = os.environ.get("JAMF_CLIENT_ID")
JAMF_CLIENT_SECRET = os.environ.get("JAMF_CLIENT_SECRET")
JAMF_BASE_URL = os.environ.get("JAMF_BASE_URL")
GROUP_ID = os.environ.get("GROUP_ID")

# Session config
config = SessionConfig()
config.timeout = 30
config.max_retries = 3
config.max_concurrency = 5
config.return_exceptions = True
config.verify = True
config

# Logging
logger_quick_setup(level=logging.DEBUG)

# initialize JamfProClient
client = JamfProClient(
    server=JAMF_BASE_URL,
    credentials=ApiClientCredentialsProvider(JAMF_CLIENT_ID, JAMF_CLIENT_SECRET),
    session_config=config
)

# Retrieve Computer Group Data
computer_group_data = client.classic_api.get_computer_group_by_id(GROUP_ID)

# If there are members of the Group, grab their device IDs and pass them into the redeploy_management_framework_v1 function
if computer_group_data.computers:
    computers = computer_group_data.computers or []

    computer_ids = []

    for computer in computers:
        computer_ids.append(computer.id)

    action = client.pro_api.redeploy_management_framework_v1(computer_ids)
    print(action)
else:
    print("No Computers in Group")