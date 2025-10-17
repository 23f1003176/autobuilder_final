from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os, re, json, google.generativeai as genai, openai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Pipe Server", version="3.1")

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


def clean_html_output(raw_html: str) -> str:
    """
    Removes Markdown fences, extra commentary, and extracts only <html>...</html> block.
    Works for Gemini and OpenAI outputs.
    """
    if not raw_html:
        return ""

    # Remove code fences (```html or ```)
    cleaned = re.sub(r"```html|```", "", raw_html, flags=re.IGNORECASE)

    # Remove AI explanations that appear outside HTML tags
    match = re.search(r"(<html[\s\S]*</html>)", cleaned, re.IGNORECASE)
    if match:
        cleaned = match.group(1)

    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()

    # Safety check
    if not cleaned.lower().startswith("<!doctype") and not cleaned.lower().startswith("<html"):
        cleaned = f"<!DOCTYPE html>\n{cleaned}"

    return cleaned


@app.post("/aipipe")
async def generate(request: Request):
    data = await request.json()
    brief = data.get("brief", "").strip()
    if not brief:
        return JSONResponse({"error": "Missing 'brief' field"}, status_code=400)

    print(f"\n🧠 Received brief: {brief}")

    html_code = None

    # Try Gemini first
    if GEMINI_API_KEY:
        try:
            print("🤖 Trying Gemini model: models/gemini-2.0-flash-exp")
            model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
            result = model.generate_content(f"Generate a valid HTML/JS web app for this task:\n{brief}")
            html_code = clean_html_output(result.text)
            print("✅ Gemini generation successful.")
        except Exception as e:
            print(f"⚠️ Gemini failed: {e}")

    # Try OpenAI fallback
    if not html_code and OPENAI_API_KEY:
        try:
            print("🤖 Trying OpenAI GPT-3.5 Turbo fallback...")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert web app generator. Always output only valid HTML."},
                    {"role": "user", "content": f"Generate a valid, standalone HTML/JS/CSS app for this task:\n{brief}"}
                ]
            )
            raw_output = response.choices[0].message["content"]
            html_code = clean_html_output(raw_output)
            print("✅ OpenAI generation successful.")
        except Exception as e:
            print(f"⚠️ OpenAI failed: {e}")

    # Fallback static HTML if all else fails
    if not html_code:
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Autobuilder App</title></head>
        <body>
            <h1>Autobuilder App</h1>
            <p>Brief: {brief}</p>
        </body>
        </html>
        """

    return JSONResponse({"html": html_code})
