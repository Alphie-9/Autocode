from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import re

from agent import run_agent

app = FastAPI(title="AI Data Analyst")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list = []


BLOCKED_PATTERNS = [
    r"\bos\.system\b",
    r"\bshutil\.rmtree\b",
    r"\b__import__\b",
    r"rm\s+-rf",
]


def is_safe_input(text: str) -> bool:
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    return True


@app.post("/chat")
async def chat(request: ChatRequest):
    if not is_safe_input(request.message):
        raise HTTPException(status_code=400, detail="Input contains potentially unsafe content.")
    try:
        result = run_agent(request.message, request.history)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
