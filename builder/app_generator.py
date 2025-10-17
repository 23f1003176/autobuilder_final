import os
import re
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Load API keys (optional — AI Pipe handles most of the generation)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AIPIPE_URL = os.getenv("AIPIPE_URL", "http://127.0.0.1:9000/aipipe")

# ---------------------------------------------------------------------
# 🧼 HTML Cleaning Function — removes markdown and explanations
# ---------------------------------------------------------------------
def clean_html_output(raw_html: str) -> str:
    """
    Cleans AI-generated HTML by removing markdown fences, explanations,
    and text after </html>.
    """
    if not raw_html:
        return ""

    # Remove markdown ```html or ```
    cleaned = re.sub(r"```html|```", "", raw_html, flags=re.IGNORECASE)

    # Keep only the <html>...</html> section
    match = re.search(r"(<html[\s\S]*?</html>)", cleaned, re.IGNORECASE)
    if match:
        cleaned = match.group(1)
    else:
        # fallback: strip markdown and explanations
        cleaned = re.sub(r"\*\*.*?\*\*", "", cleaned)
        cleaned = re.sub(r"(?s)```.*?```", "", cleaned)
        cleaned = re.sub(r"#.*", "", cleaned)
        cleaned = cleaned.strip()

    # Trim anything after </html>
    end_html_index = cleaned.lower().find("</html>")
    if end_html_index != -1:
        cleaned = cleaned[:end_html_index + 7]

    # Add DOCTYPE if missing
    if not cleaned.lower().startswith("<!doctype"):
        cleaned = "<!DOCTYPE html>\n" + cleaned.strip()

    return cleaned.strip()

# ---------------------------------------------------------------------
# 🧠 AI Generator (uses AI Pipe → Gemini → OpenAI fallback)
# ---------------------------------------------------------------------
def generate_app(brief: str) -> str:
    """
    Generates HTML content for the given task brief using AI Pipe.
    Falls back to OpenAI, Gemini, or static template if unavailable.
    """
    print("Generating app with AI Pipe...")
    print(f"🧾 Brief: {brief}")

    # STEP 1: Try AI Pipe (self-hosted model handler)
    try:
        print("🤖 Using AI Pipe for app generation...")
        response = requests.post(
            AIPIPE_URL,
            json={"brief": brief},
            timeout=40
        )

        if response.status_code == 200:
            result = response.json()
            if "html" in result:
                print("✅ AI Pipe returned HTML successfully.")
                return clean_html_output(result["html"])
            elif "content" in result:
                print("✅ AI Pipe returned content successfully.")
                return clean_html_output(result["content"])
            else:
                print("⚠️ AI Pipe did not return HTML, falling back...")
        else:
            print(f"⚠️ AI Pipe failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"⚠️ AI Pipe failed. Using fallback template. Reason: {e}")

    # STEP 2: Static fallback (safe and simple)
    print("🧩 Using fallback static HTML template...")
    fallback_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autobuilder Output</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container py-5">
        <div class="card shadow p-4">
            <h2 class="text-center mb-4">Generated Task</h2>
            <p><strong>Task Brief:</strong> {brief}</p>
            <p class="text-muted">⚙️ This is a fallback page generated when AI services are unavailable.</p>
        </div>
    </div>
</body>
</html>"""
    return fallback_html

# ---------------------------------------------------------------------
# ✅ Manual Test (Optional)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    sample_brief = "Create a responsive payment form with Name, Email, Card Number, Expiry, CVV, and Pay button styled with Bootstrap."
    html_code = generate_app(sample_brief)
    with open("test_output.html", "w", encoding="utf-8") as f:
        f.write(html_code)
    print("✅ Saved cleaned HTML to test_output.html")
