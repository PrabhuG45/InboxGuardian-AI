from typing import List
from pydantic import BaseModel, Field


class ThreadSummaryRequest(BaseModel):
    thread_id: str
    message_bodies: List[str] = Field(
        ...,
        min_items=1,
        description="Chronological email bodies belonging to the thread",
    )


class ThreadSummaryResponse(BaseModel):
    thread_id: str
    concise_digest: str
    bullet_points: List[str]
    action_items: List[str]
    participant_count: int