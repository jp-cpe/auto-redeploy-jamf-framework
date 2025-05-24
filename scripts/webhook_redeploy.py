import sys
from utils.jamf_client import client


computer_id = sys.argv[1]

print(f"Redeploying framework for computer ID {computer_id}")
client.redeploy_management_framework(computer_id)
