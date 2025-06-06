# Jamf Framework Redeployment Script

This script automates the redeployment of the Jamf management framework to macOS devices using Jamf Pro’s APIs. It is intended to support proactive remediation of macOS devices with broken Jamf framework.


> "In some situations, a managed computer can enter a state where MDM commands process normally, but functionality that relies on the Jamf management framework is consistently failing. In this state, policies fail to execute and the Jamf Pro logs report "Device Signature" errors for the computer. 
>
> To restore management with the Jamf Pro server, the Jamf management framework should be reinstalled on the affected computer. As long as the MDM profile on the computer is still valid, you can use Jamf Pro to redeploy the Jamf management framework using the v1/jamf-management-framework/redeploy endpoint in the Jamf Pro API."

- Read more about redeploying the Jamf management framework using the Jamf Pro API [here](https://learn.jamf.com/en-US/bundle/technical-articles/page/Redeploying_the_Jamf_Management_Framework_Using_the_Jamf_Pro_API.html).


## What It Does

- Identifies devices with broken Jamf binary.
- Sends a `POST /v1/jamf-management-framework/redeploy/{id}` command to each device via the Pro API.
- Returns a `deviceId` and `commandUuid` to confirm execution.


## Prerequisites

This utility assumes you've configured two smart groups and a configuration profile in Jamf Pro:

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
- **Group A** is used as the scope for the Configuration Profile. 
- **Group B** is used as the target for the Jamf framework redeployment.


## Setup

### 1. Create the two Smart Computer Groups in Jamf
- Note the ID of **Group B** (located in the URL of the group) 
  - Example: `https://company.jamfcloud.com/OSXConfigurationProfiles.html?id=777`)

### 2. Create the Configuration Profile in Jamf
- Scope the Configuration Profile to **Group A**

### 3. Create an API Role and API Client in Jamf
- API Role Privileges Required:
  - `Send Computer Remote Command to Install Package`
  - `Read Computer Check-In`
  - `Read Smart Computer Groups`

### 4. Clone this repository or click "Use this template"

### 5. Add these secrets to your repository
- Repository > Settings > Secrets and variables > Actions
  - `GROUP_ID` (the ID of **Group B**)
  - `JAMF_BASE_URL` (the URL of your Jamf server: **company.jamfcloud.com**)
  - `JAMF_CLIENT_ID` (the client ID of your API client)
  - `JAMF_CLIENT_SECRET` (the client secret of your API client)

# Usage
### Scheduled Run
The scheduled workflow is set to run **every Monday at 2:00 AM UTC** by default.

Edit the cron schedule to your preferred time or remove this code from the workflow file if you prefer to only run the job manually:

```
schedule:
    - cron: '0 2 * * 1'  # Runs every Sunday 7 PM PT (Monday 2 AM UTC)
```

### Manual Run
The workflow can also be run manually by going to **Actions** > **Scheduled Jamf Framework Redeploy** > *Run workflow.*

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

## Advanced Setup
The current setup is straightforward and allows admins to run the redeploy workflow manually or on a schedule. However, it executes the script regardless of whether any devices actually require a framework redeployment.

A more efficient solution is an event-driven approach: using a Jamf webhook and a FastAPI service to listen for Smart Group membership changes. This enables the workflow to trigger only when a device truly meets the redeploy criteria—delivering real-time remediation without unnecessary execution.

### Generate Webhook Secret 
To generate a secure webhook secret for verifying that incoming requests actually came from Jamf (or any source), you want a random, cryptographically strong string. Here’s how to do that safely and effectively:

```
openssl rand -hex 32
```

This gives you a 64-character hex string (256 bits of entropy), e.g.:

```
9e4a3d6f3bf24316a2d80d7f1a8a82dcd75d3c48b8a9c25e1a2b28e9b2752e4
```

You can use that as your **WEBHOOK_SECRET** when configuring your FastAPI service.

### Generate GitHub PAT (Personal Access Token)
Navigate to GitHub Settings > Developer Settings > Personal access tokens > Fine-grained tokens
(https://github.com/settings/personal-access-tokens)

1. Click "Generate new token"
2. Add a token name
3. Set an Expiration
4. Select your repository
5. Permissions: 
    - **Actions** > *Read and write*
6. Generate the token and save the value

### FastAPI Service
To parse the data sent by the Jamf webhook and subsequently trigger the Github workflow we must first set up a FastAPI service. This FastAPI service can be hosted anywhere, but for our example we will use Fly.io.

1. Install the Fly.io CLI

    ```sh
    brew install flyctl
    ```

2. Authenticate with Fly

    ```sh
    fly auth login
    ```

3. Create and Launch Your App

    ```sh
    cd fastapi_webhook
    fly launch
    ```

    You’ll be prompted to:

    - Name your app (or auto-generate one)

    - Choose a region (e.g. sjc, ord, etc.)

    - Deploy now? (you can say no if you want to edit **fly.toml** first)

    It will create:

    - fly.toml (config)

    - .dockerignore (if not present)

4. Add Secrets

    ```sh
    fly secrets set GITHUB_PAT=your_github_pat REPO=your_github_repo WEBHOOK_SECRET=your_webhook_secret
    ```

    Note: the REPO value should include your GitHub username + repository name (e.g., **jp-cpe/auto-redeploy-jamf-framework**)

5. Deploy the App

    ```sh
    fly deploy
    ```

    This packages your app in a container, deploys it, and returns a public URL (e.g., https://fastapi-webhook.fly.dev/).

6. Test the Webhook (Optional)

    ```
    curl -X POST https://fastapi-webhook.fly.dev/ \
      -H "Content-Type: application/json" \
      -H "x-webhook-secret: 9e4a3d6f3bf24316a2d80d7f1a8a82dcd75d3c48b8a9c25e1a2b28e9b2752e4" \
      -d '{
        "event": {
          "groupAddedDevicesIds": [777]
        }
      }'
    ```

    If successful, you should get:

    ```
    {"status":"dispatched","results":[{"computer_id":777,"status_code":204}
    ```

    To view logs:

    ```
    fly logs
    ```

### Jamf Webhook
Real time detection of eligible devices requires a Jamf webhook that fires when Smart Group Membership changes are made.

To add a webhook in Jamf:
1. Go to **Settings** > **Global** > **Webhooks** > ***New***
2. Add the **Webhook URL** 
3. For **Authentication Type** select **Header Authentication**
    - Add your webhook secret
    ```
    { "x-webhook-secret": "ef8b6c082d18d654dcc19b58d18b492cfb88372c63644e7dc775d09e5b47a04" }
    ```
4. For **Content Type** select **JSON**
5. Set **Webhook Event** to *SmartGroupComputerMembershipChange*
6. Set **Target Smart Computer Group** to **[Smart Group B]**

### Slack Notifications

## Notes
No user interaction is required. The framework redeploys via the "Install Enterprise Application" MDM command over APNs. This triggers an "Enrollment Complete" state, running any associated policies and applying Global > Re-enrollment Settings. The devices will resume check-ins with Jamf, potentially triggering a backlog of policies if it’s been offline for a while.

## Credit
This script uses a customized version of the [Jamf Pro SDK for Python](https://github.com/macadmins/jamf-pro-sdk-python) and was inspired by Mann Consulting's ["Flawless MDM Communication"](https://github.com/mannconsulting/JNUC2024/) presentation at JNUC 2024. I highly recommend you check out both projects.
