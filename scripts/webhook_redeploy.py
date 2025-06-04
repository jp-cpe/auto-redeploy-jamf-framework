import sys
from utils.jamf_client import redeploy_framework

computer_ids = sys.argv[1]

print(f"Redeploying framework for computer ID {computer_ids}")
result = redeploy_framework(computer_ids)
print(f"Redeploy triggered for IDs: {computer_ids}")
print(result)

