from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileRequest(BaseModel):
    goal: str | None = None
    level: str | None = None
    equipment: str | None = None
    days_per_week: int | None = None


class AskRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)


class AskResponse(BaseModel):
    answer: str


class WorkoutPlanRequest(BaseModel):
    goal: str | None = None
    level: str | None = None
    equipment: str | None = None
    days_per_week: int | None = None


class WorkoutPlanResponse(BaseModel):
    plan: str