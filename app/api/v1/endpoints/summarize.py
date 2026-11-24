from fastapi import APIRouter, Security
from app.core.zero_trust import get_current_user
from app.ml.thread_summarizer import summarizer_engine
from app.schemas.auth import UserContext
from app.schemas.summary import ThreadSummaryRequest, ThreadSummaryResponse

router = APIRouter()


@router.post(
    "/summarize",
    response_model=ThreadSummaryResponse,
    summary="Generate AI Thread Summary & Action Items",
)
async def summarize_thread_endpoint(
    payload: ThreadSummaryRequest,
    user: UserContext = Security(get_current_user, scopes=["email:read"]),
):
    return summarizer_engine.summarize_thread(
        thread_id=payload.thread_id,
        message_bodies=payload.message_bodies,
    )