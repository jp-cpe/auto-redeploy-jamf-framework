from fastapi import FastAPI, Request, Header, HTTPException
import httpx
import os

app = FastAPI()

@app.post("/")
async def handle_webhook(request: Request, x_webhook_secret: str = Header(...)):
    expected_secret = os.getenv("WEBHOOK_SECRET")
    if x_webhook_secret != expected_secret:
        raise HTTPException(status_code=401, detail="Unauthorized")

    payload = await request.json()

    try:
        computer_ids = payload["event"]["groupAddedDevicesIds"]
    except Exception as e:
        return {"status": "error", "detail": str(e)}

    results = []
    for computer_id in computer_ids:
        result = await trigger_github_workflow(computer_id)
        results.append({"computer_id": computer_id, **result})

    return {"status": "dispatched", "results": results}


async def trigger_github_workflow(computer_id: int):
    GITHUB_TOKEN = os.getenv("GITHUB_PAT")
    REPO = os.getenv("REPO")
    WORKFLOW_FILE = "webhook-redeploy-jamf-framework.yml"
    REF = "main"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    payload = {
        "ref": REF,
        "inputs": {
            "computer_id": str(computer_id),
            "source": "jamf-webhook"
        }
    }

    print(f"Triggering workflow: {WORKFLOW_FILE} on branch {REF}")
    print(f"Payload: {payload}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches",
            headers=headers,
            json=payload
    )
    print(f"GitHub response: {response.status_code}")
    return {"status_code": response.status_code}