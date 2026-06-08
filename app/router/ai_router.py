from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.dependency import AIServiceDep, CurrentUserDep
from app.schema import ChatEvent, ChatEventType, ChatRequest

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: CurrentUserDep,
    service: AIServiceDep,
):
    async def event_stream():
        try:
            async for event in service.chat(
                project_id=request.project_id,
                prompt=request.prompt,
                user_id=current_user.id,
                session_id=request.session_id,
            ):
                yield event.to_sse()

        except Exception as e:
            error_event = ChatEvent(
                ChatEventType.ERROR,
                {"message": str(e)},
            )
            yield error_event.to_sse()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
