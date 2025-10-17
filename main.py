from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os, json, requests
from builder.app_generator import generate_app
from builder.repo_manager import create_or_update_github_repo

# Load environment variables
load_dotenv()

app = FastAPI(title="Autobuilder API", version="3.5")

# === Load required secrets ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
STUDENT_SECRET = os.getenv("STUDENT_SECRET")
AIPIPE_URL = os.getenv("AIPIPE_URL", "http://127.0.0.1:9000/aipipe")

# Validate environment variables
if not GITHUB_TOKEN:
    raise Exception("❌ Missing GITHUB_TOKEN in .env file")

if not STUDENT_SECRET:
    raise Exception("❌ Missing STUDENT_SECRET in .env file")

print("✅ Autobuilder environment loaded successfully.")
print(f"🔗 Connected AI Pipe endpoint: {AIPIPE_URL}")

# === Root endpoint ===
@app.get("/")
async def home():
    return {"message": "Welcome to the Autobuilder API. Use POST /api-endpoint to submit tasks."}


# === Task endpoint (Instructor Request) ===
@app.post("/api-endpoint")
async def build_app(request: Request):
    """
    Main entry point for instructor evaluations.
    Receives a JSON payload with a 'brief' and other metadata.
    """
    try:
        data = await request.json()
        print("\n📩 Received Task:")
        print(json.dumps(data, indent=2))

        # Validate secret
        secret = data.get("secret")
        if secret != STUDENT_SECRET:
            print("❌ Invalid secret provided — rejecting request.")
            return JSONResponse({"error": "Invalid secret"}, status_code=403)

        # Extract parameters
        brief = data.get("brief", "").strip()
        task_name = data.get("task", "autobuilder-app").strip()
        evaluation_url = data.get("evaluation_url", "").strip()
        email = data.get("email", "")
        round_num = data.get("round", 1)
        nonce = data.get("nonce", "")

        if not brief:
            return JSONResponse({"error": "Missing 'brief' field"}, status_code=400)

        print(f"🧠 Generating app for task: {task_name}")
        print(f"💡 Brief: {brief}")

        # === Step 1: Generate HTML using AI Pipe ===
        html_code = generate_app(brief)

        # === Step 2: Create or update GitHub repository ===
        repo_url, pages_url = create_or_update_github_repo(task_name, html_code)

        print(f"✅ Deployment successful!")
        print(f"   📁 Repo URL: {repo_url}")
        print(f"   🌐 Live Site: {pages_url}")

        # === Step 3: Notify evaluation endpoint ===
        payload = {
            "email": email,
            "task": task_name,
            "round": round_num,
            "nonce": nonce,
            "repo_url": repo_url,
            "pages_url": pages_url
        }

        if evaluation_url:
            try:
                print(f"📬 Notifying evaluation API at: {evaluation_url}")
                res = requests.post(evaluation_url, json=payload, timeout=10)
                print(f"✅ Evaluation API responded: {res.status_code}")
            except Exception as e:
                print(f"⚠️ Could not reach evaluation URL: {e}")
        else:
            print("⚠️ No evaluation URL provided — skipping notification.")

        # === Step 4: Return response to instructor ===
        return JSONResponse({
            "message": "✅ Task successfully processed and deployed.",
            "repo_url": repo_url,
            "pages_url": pages_url
        }, status_code=200)

    except Exception as e:
        print(f"❌ Fatal Error during task processing: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
