from dotenv import load_dotenv
load_dotenv()

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import ask_agent


# CORS настройки
FRONTEND_ORIGINS = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5500,http://127.0.0.1:5500"
).split(",")


app = FastAPI(title="Fitness AI Assistant")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Схемы запрос/ответ
class AskRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)


class AskResponse(BaseModel):
    answer: str


# Health check
@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Fitness AI Assistant"
    }


# Основной endpoint
@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    answer = await ask_agent(req.query)
    return AskResponse(answer=answer)