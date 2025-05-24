import sys
from utils.jamf_client import redeploy_framework

computer_ids = sys.argv[1]

print(f"Redeploying framework for computer ID {computer_ids}")
redeploy_framework(computer_ids)
