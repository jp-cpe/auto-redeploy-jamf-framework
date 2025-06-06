# Webhook-Driven FastAPI Adapter Setup (Optional)

This guide explains how to deploy an event-driven FastAPI service that listens for Jamf Smart Group membership changes and triggers a GitHub workflow to redeploy the Jamf Framework.

---

## 📚 Table of Contents

* [Generate Webhook Secret](#-generate-webhook-secret)
* [Generate GitHub PAT](#-generate-github-pat-(personal-access-token))
* [Deploy FastAPI to Fly.io](#-deploy-fastapi-to-fly.io)
* [Test the Webhook](#-test-the-webhook)
* [Configure Jamf Webhook](#-configure-jamf-webhook)

---
## 🔐 Generate Webhook Secret

Use this command to create a secure 256-bit hex string:

```bash
openssl rand -hex 32
```

Set this as your `WEBHOOK_SECRET` when configuring the FastAPI adapter and Jamf webhook.

---

## 🔑 Generate GitHub PAT (Personal Access Token)

1. Go to [GitHub > Settings > Developer Settings > PATs](https://github.com/settings/personal-access-tokens)
2. Click **Generate new token (Fine-grained)**
3. Name it, set expiration, and select the repo
4. Set permissions:

   * **Actions** → `Read and Write`
5. Save the token

---

## 🚀 Deploy FastAPI to Fly.io

### 1. Install Fly CLI

```bash
brew install flyctl
```

### 2. Authenticate

```bash
fly auth login
```

### 3. Launch App

```bash
cd fastapi_webhook
fly launch
```

Select:

* App name (or auto-generate)
* Region (e.g. `sjc`, `ord`)
* Choose **No** if you want to edit `fly.toml` first

### 4. Add Secrets

```bash
fly secrets set \
  GITHUB_PAT=your_github_pat \
  REPO=your_user/your_repo \
  WEBHOOK_SECRET=your_webhook_secret
```

### 5. Deploy

```bash
fly deploy
```

Fly will package your app and return a public URL (e.g. `https://fastapi-webhook.fly.dev`)

---

## ✅ Test the Webhook

Use `curl` to verify:

```bash
curl -X POST https://fastapi-webhook.fly.dev/ \
  -H "Content-Type: application/json" \
  -H "x-webhook-secret: YOUR_SECRET" \
  -d '{
    "event": {
      "groupAddedDevicesIds": [777]
    }
  }'
```

Expected output:

```json
{"status":"dispatched","results":[{"computer_id":777,"status_code":204}]}
```

Check logs:

```bash
fly logs
```

---

## ⚙️ Configure Jamf Webhook

1. In Jamf Pro, go to: `Settings > Global > Webhooks > New`
2. Name your webhook and paste your Fly URL
3. Authentication Type: `Header Authentication`
4. Header Key: `x-webhook-secret`
5. Header Value: your `WEBHOOK_SECRET`

    ```
    { "x-webhook-secret": "YOUR_SECRET" }
    ```
6. Content Type: `JSON`
7. Webhook Event: `SmartGroupComputerMembershipChange`
8. Target Smart Group: **Group B** (Not Checked In + Null Profile Installed)

Done! You now have a real-time, event-based remediation flow.
