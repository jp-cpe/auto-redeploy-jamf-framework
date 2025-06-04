from utils.jamf_client import get_computers_in_group, redeploy_framework
import os

GROUP_ID = os.getenv("GROUP_ID")

print(f"Getting computers in group with ID={GROUP_ID}")
computers = get_computers_in_group(GROUP_ID)

if computers:
    computer_ids = [c.id for c in computers]
    print(f"Redeploying framework for computer IDs: {computer_ids}")
    result = redeploy_framework(computer_ids)
    print(f"Redeploy triggered for IDs: {computer_ids}")
    print(result)
else:
    print(f"No computers found in group with ID={GROUP_ID}")