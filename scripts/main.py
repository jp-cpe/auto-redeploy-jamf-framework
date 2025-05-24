from utils.jamf_client import client

# Redeploy management framework for computers in group
group = client.classic_api.get_computer_group_by_id(GROUP_ID)
computers = group.computers or []

if computers:
    computer_ids = [c.id for c in computers]
    result = client.pro_api.redeploy_management_framework_v1(computer_ids)
    print(result)
else:
    print(f"No computers in Computer Group with ID={GROUP_ID}")
