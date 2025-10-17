# 🚀 Autobuilder

**Autobuilder** is a FastAPI-based application that can automatically **build, deploy, and update** small web apps based on AI-generated code.  
It receives structured JSON task requests (from instructors or automated systems), validates the request, generates the required app using AI (Gemini or OpenAI), pushes it to **GitHub Pages**, and finally sends back deployment details for evaluation.

---

## ⚙️ Features

- 🧠 AI-driven app generation (Gemini / OpenAI / AI Pipe backend)
- 📦 Automated GitHub repository creation & updates
- 🌐 Instant GitHub Pages deployment
- 🔍 Evaluation-ready structure (MIT License, README, valid Pages URL)
- 🔁 Supports multiple “rounds” (update requests)

---

## 🧩 Project Structure

autobuilder/
│
├── main.py # Main FastAPI app - handles instructor requests
├── aipipe_server.py # AI Pipe microservice to generate code via Gemini/OpenAI
├── builder/
│ ├── app_generator.py # Code generation logic
│ ├── repo_manager.py # Handles GitHub repo creation & Pages deployment
│
├── requirements.txt
└── .env # Contains API keys and secrets (not uploaded to GitHub)

---

## 🧠 How It Works

1. Instructor (or user) sends a JSON request to `/api-endpoint`
2. Autobuilder validates the `secret`
3. AI Pipe (Gemini/OpenAI) generates HTML/JS/CSS for the task brief
4. Code is committed & pushed to GitHub automatically
5. GitHub Pages is enabled and deployment URL returned
6. The result is notified to the evaluation API

---

## ▶️ How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Add .env file

```bash
GITHUB_TOKEN=your_github_token
STUDENT_SECRET=my-super-secret
AIPIPE_API_KEY=your_ai_key
```

## 3. Run the AI Pipe microservice

```bash
python aipipe_server.py
```

## 4. Run the main FastAPI app

```bash
uvicorn main:app --reload
```

# 📤 Example Test (Payment Form Task)

```bash
Invoke-RestMethod -Method POST "http://127.0.0.1:8000/api-endpoint" `
-Headers @{"Content-Type"="application/json"} `
-Body '{
  "email": "student@example.com",
  "secret": "my-super-secret",
  "task": "payment-form-site",
  "round": 1,
  "nonce": "pmt200",
  "brief": "Create a responsive payment form with Name, Email, Card Number, Expiry, CVV, and Pay button styled with Bootstrap that shows an alert on submit.",
  "evaluation_url": "https://example.com/notify"
}'
```

## 🎯 Expected Result

✅ A new GitHub repository (e.g. payment-form-site)
✅ GitHub Pages live site (e.g. `https://username.github.io/payment-form-site/`)
✅ A working web app generated automatically from AI.
