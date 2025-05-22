import sys
from utils.jamf_client import get_jamf_client

computer_id = sys.argv[1]
client = get_jamf_client()

print(f"Redeploying framework for computer ID {computer_id}")
client.redeploy_management_framework(computer_id)
