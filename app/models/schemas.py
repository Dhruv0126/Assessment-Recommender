from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    messages: list[Message] = Field(..., min_length=1)


class Recommendation(BaseModel):
    name: str
    url: HttpUrl
    test_type: str
    description: str | None = None
    duration: str | None = None
    category: str | None = None
    skills_measured: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    recommendations: list[Recommendation] = Field(default_factory=list)
    end_of_conversation: bool = False
