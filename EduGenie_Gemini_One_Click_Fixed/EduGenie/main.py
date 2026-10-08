"""FastAPI routes for EduGenie (run: uvicorn main:app --reload)."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel, Field
from ai_client import AIServiceError, valid_key
from qna import answer_question_with_gemini
from explanation_module import explain_topic
from summary_module import summarize_text
from quiz_module import generate_quiz
from learning_path import get_learning_recommendations

BASE = Path(__file__).resolve().parent
app = FastAPI(title="EduGenie", description="Gemini-powered learning assistant", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE / "templates"))

class TextInput(BaseModel):
    text: str = Field(min_length=2, max_length=20000)

class TopicInput(BaseModel):
    topic: str = Field(min_length=2, max_length=1500)
    level: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")

class LearningInput(TopicInput):
    weeks: int = Field(default=4, ge=1, le=24)

@app.exception_handler(AIServiceError)
async def ai_error_handler(request: Request, exc: AIServiceError):
    from fastapi.responses import JSONResponse
    code = 503 if "key" in str(exc).lower() or "reach" in str(exc).lower() or "quota" in str(exc).lower() else 502
    return JSONResponse(status_code=code, content={"detail": str(exc)})

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/health")
async def health():
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return {"status": "ok", "mode": "demo" if os.getenv("DEMO_MODE", "false").lower() == "true" else "gemini", "key_configured": valid_key()}

@app.get("/qa")
async def qa(question: str = Query(min_length=2, max_length=1500)):
    return {"answer": answer_question_with_gemini(question)}

@app.post("/explain")
async def explain(data: TopicInput):
    return {"topic": data.topic, "explanation": explain_topic(data.topic, data.level)}

@app.post("/summarize")
async def summarize(data: TextInput):
    return {"summary": summarize_text(data.text)}

@app.post("/quiz")
async def quiz(data: TextInput):
    return {"quiz": generate_quiz(data.text)}

@app.get("/learn/recommendations")
async def learning_get(topic: str = Query(min_length=2, max_length=1500), level: str = "beginner", weeks: int = Query(default=4, ge=1, le=24)):
    data = LearningInput(topic=topic, level=level, weeks=weeks)
    return {"topic": data.topic, "recommendation": get_learning_recommendations(data.topic, data.level, data.weeks)}

@app.post("/learn/recommendations")
async def learning_post(data: LearningInput):
    return {"topic": data.topic, "recommendation": get_learning_recommendations(data.topic, data.level, data.weeks)}
