# Jamf Framework Redeployment Script

This script automates the redeployment of the Jamf management framework for macOS devices using Jamf Pro’s APIs. It is intended to support proactive remediation of macOS devices with broken Jamf framework.



```
"In some situations, a managed computer can enter a state where MDM commands process normally, but functionality that relies on the Jamf management framework is consistently failing. In this state, policies fail to execute and the Jamf Pro logs report "Device Signature" errors for the computer.

To restore management with the Jamf Pro server, the Jamf management framework should be reinstalled on the affected computer. As long as the MDM profile on the computer is still valid, you can use Jamf Pro to redeploy the Jamf management framework using the v1/jamf-management-framework/redeploy endpoint in the Jamf Pro API."
```
  - Read more about redeploying the Jamf management framework using the Jamf Pro API [here](https://learn.jamf.com/en-US/bundle/technical-articles/page/Redeploying_the_Jamf_Management_Framework_Using_the_Jamf_Pro_API.html).

**Note**: This script uses a customized version of the [Jamf Pro SDK for Python](https://github.com/macadmins/jamf-pro-sdk-python) and was inspired by Mann Consulting's ["Flawless MDM Communication"](https://github.com/mannconsulting/JNUC2024/) presentation at JNUC 2024. I highly recommend you check out both.


## What It Does

- Connects to the Jamf Pro Classic API to retrieve members of a specific computer group.
- Sends a `POST /v1/jamf-management-framework/redeploy/{id}` command to each device via the Pro API.
- Returns a `deviceId` and `commandUuid` to confirm execution.


## Prerequisites

This script assumes you've configured two smart groups and a configuration profile in Jamf Pro:

### 1. Configuration Profile
- Create a configuration profile that includes no payloads or settings.
- Assign it to stale devices via a smart group (**Group A**)
- This profile acts as a marker to confirm devices are still reachable by MDM.

#### Preference Domain (set to whatever you want):
```xml
com.jp-cpe.null
```
#### Application & Custom Settings Payload:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>null</key>
    <true/>
  </dict>
</plist>
```
#### Scope:
```xml
Group A: "Not Checked In (14+ Days)"
```

### 2. Smart Group Setup

#### Group A: "Not Checked In (14+ Days)"
- Criteria:
  - `Last Check-In` is more than 14 days ago

#### Group B: "Not Checked In (14+ Days) + Configuration Profile Installed"
- Criteria:
  - `Last Check-In` is more than 14 days ago
  - `Profile Name` is `<name of configuration profile>`

---
**Group A** is used as the scope for the Configuration Profile. **Group B** is used as the target for this script.


## Usage

### 1. Create the two Smart Computer Groups in Jamf
- Note the ID of **Group B** (located in the URL of the group) 
  - Ex: `https://company.jamfcloud.com/OSXConfigurationProfiles.html?id=777`)

### 2. Create the Configuration Profile in Jamf
- Scope the Configuration Profile to **Group A**

### 3. Create an API Role and API Client in Jamf
- API Role Privileges Required:
  - `Send Computer Remote Command to Install Package`
  - `Read Computer Check-In`
  - `Read Smart Computer Groups`

### 4. Clone this repository

### 5. Configure the GitHub workflow file
The workflow is set to run **every Monday at 2:00 AM UTC** by default. It can also be run manually from within the repository's **Actions** tab. 

Edit the cron schedule to your preferred time or remove this code from the workflow file if you prefer to only run the job manually:

```
schedule:
    - cron: '0 2 * * 1'  # Runs every Sunday 7 PM PT (Monday 2 AM UTC)
```
### 6. Add these secrets to your repository
- Repository > Settings > Secrets and variables > Actions
  - `GROUP_ID` (the ID of **Group B**)
  - `JAMF_BASE_URL` (the URL of your Jamf server: **company.jamfcloud.com**)
  - `JAMF_CLIENT_ID` (the client ID of your API client)
  - `JAMF_CLIENT_SECRET` (the client secret of your API client)

## Example Output
If a single ID is passed, a single model is returned. If multiple IDs are passed, a list is returned.

```json
[
  {
    "deviceId": "000",
    "commandUuid": "9ee7f9a8-bf4f-4d0c-aa7e-38c983681c8a"
  },
  {
    "deviceId": "123",
    "commandUuid": "5e489e68-3704-40b9-b781-bdb04225f9eb"
  }
]
```
