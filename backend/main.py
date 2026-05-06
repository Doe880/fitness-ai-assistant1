from dotenv import load_dotenv
load_dotenv()

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import ask_agent
from logger import log_query


FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5500,http://127.0.0.1:5500"
    ).split(",")
    if origin.strip()
]


app = FastAPI(title="Fitness AI Assistant")


app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class AskRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    history: list[ChatMessage] = []


class AskResponse(BaseModel):
    answer: str
    sources: list[dict]


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Fitness AI Assistant",
        "allowed_origins": FRONTEND_ORIGINS
    }


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    try:
        history = [
            {
                "role": message.role,
                "content": message.content
            }
            for message in req.history
        ]

        answer, sources = await ask_agent(req.query, history)

        log_query(
            query=req.query,
            answer=answer,
            sources=sources
        )

        return AskResponse(
            answer=answer,
            sources=sources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))