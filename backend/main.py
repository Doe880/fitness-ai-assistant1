from dotenv import load_dotenv
load_dotenv()

import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from agent import ask_agent
from auth import create_access_token, get_current_user, hash_password, verify_password
from db import get_db, init_db
from models import ChatMessage, User, UserProfile, WorkoutPlan
from schemas import (
    AskRequest,
    AskResponse,
    LoginRequest,
    ProfileRequest,
    RegisterRequest,
    TokenResponse,
    WorkoutPlanRequest,
    WorkoutPlanResponse,
)


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


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Fitness AI Assistant"
    }


@app.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email=req.email,
        password_hash=hash_password(req.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    profile = UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()

    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(access_token=token)


@app.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(access_token=token)


@app.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }


@app.post("/profile")
def save_profile(
    req: ProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    profile.goal = req.goal
    profile.level = req.level
    profile.equipment = req.equipment
    profile.days_per_week = req.days_per_week

    db.commit()

    return {"status": "saved"}


@app.get("/history")
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.asc())
        .limit(50)
        .all()
    )

    return [
        {
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at.isoformat()
        }
        for message in messages
    ]


@app.post("/ask", response_model=AskResponse)
async def ask(
    req: AskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        previous_messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.user_id == current_user.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(8)
            .all()
        )

        history = [
            {
                "role": message.role,
                "content": message.content
            }
            for message in reversed(previous_messages)
        ]

        answer, sources = await ask_agent(req.query, history)

        db.add(ChatMessage(
            user_id=current_user.id,
            role="user",
            content=req.query
        ))

        db.add(ChatMessage(
            user_id=current_user.id,
            role="assistant",
            content=answer
        ))

        db.commit()

        return AskResponse(answer=answer)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workout-plan", response_model=WorkoutPlanResponse)
async def create_workout_plan(
    req: WorkoutPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    goal = req.goal or (profile.goal if profile else "общая форма")
    level = req.level or (profile.level if profile else "новичок")
    equipment = req.equipment or (profile.equipment if profile else "зал или дом")
    days_per_week = req.days_per_week or (profile.days_per_week if profile else 3)

    prompt = (
        f"Составь тренировочный план на неделю. "
        f"Цель: {goal}. "
        f"Уровень: {level}. "
        f"Оборудование: {equipment}. "
        f"Дней в неделю: {days_per_week}. "
        f"Используй только базу знаний."
    )

    answer, sources = await ask_agent(prompt, history=[])

    plan = WorkoutPlan(
        user_id=current_user.id,
        title=f"План на неделю: {goal}",
        content=answer
    )

    db.add(plan)
    db.commit()

    return WorkoutPlanResponse(plan=answer)


@app.get("/workout-plans")
def get_workout_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plans = (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == current_user.id)
        .order_by(WorkoutPlan.created_at.desc())
        .all()
    )

    return [
        {
            "id": plan.id,
            "title": plan.title,
            "content": plan.content,
            "created_at": plan.created_at.isoformat()
        }
        for plan in plans
    ]