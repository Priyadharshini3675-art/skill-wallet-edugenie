# EduGenie – Gemini-Powered Learning Assistant

Five study modules: Question Answering, Explanation, Three-Question Quiz with scoring, Summarization, and Personalized Learning Roadmap. FastAPI backend, responsive HTML/CSS/JavaScript frontend, Google's `google-genai` Python SDK.

## Start on Windows with one click

1. Install Python 3.10+ from https://www.python.org/downloads/ (check **Add Python to PATH**).
2. Extract this ZIP, open the `EduGenie` folder, and double-click **Run_EduGenie.bat**.
3. Wait while it creates `.venv` and installs packages (only on the first launch).
4. Paste your API key at the **hidden** prompt. Get a key at https://aistudio.google.com/apikey.
5. Use the opened browser at http://127.0.0.1:8000.

On later runs, simply double-click the batch file. Leave its command window running while using the app. The launcher no longer silently stays in demo mode: a key is required for real responses.

## Verify your Gemini setup

Open http://127.0.0.1:8000/health and confirm the values `"mode": "gemini"`, `"key_configured": true`. This checks that your configuration was loaded, **not** that Google accepted your key. Ask `What is 2+2?` in the Q&A tab to confirm a live Google response. For HTTP status and request testing, visit http://127.0.0.1:8000/docs.

If you get `quota or rate limit reached`, your Google account has reached API limits; consult Google AI Studio. If you get `model unavailable`, try a currently available model in `.env`. If you get an authentication error, replace the key in `.env`. Key and quota availability are determined by Google; this project cannot bypass them.

## Manual start in VS Code

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe config_setup.py
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

The `config_setup.py` helper writes a private `.env` in the project directory. Do not commit or share `.env`. `.gitignore` excludes it. To change the API key, close the server, edit `.env` and relaunch. `DEMO_MODE=false` is required; the package intentionally never generates fake study replies.

## API endpoints

- `GET /qa?question=...` — answer question
- `POST /explain` JSON `{ "topic": "photosynthesis", "level": "beginner" }`
- `POST /quiz` JSON `{ "text": "Pythagorean theorem" }`
- `POST /summarize` JSON `{ "text": "your passage" }`
- `GET /learn/recommendations?topic=SQL` or `POST /learn/recommendations` JSON `{ "topic": "SQL", "level": "beginner", "weeks": 4 }`
- `GET /health` — configuration status without revealing the key

## Automated tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Tests use mocked AI responses, so they cannot establish that your account has an active Gemini key or adequate quota. Real inference must be tested online from your computer. Google Gemini and an Internet connection are mandatory for all actual AI responses.


## Updated one-click Gemini integration (October 2026)
Unzip and double-click `Run_EduGenie.bat`. The launcher installs Python dependencies, accepts a fresh Google AI Studio key privately, and performs a live key/model diagnostic. Default model is `gemini-3.5-flash`; change `GEMINI_MODEL` in `.env` to a model enabled for your account if necessary. Never commit `.env`.
