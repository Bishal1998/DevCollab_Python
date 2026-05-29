# app/router/AiRouter.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.dependency import AiServiceDep, CurrentUserDep
from app.schema import ChatRequest

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: CurrentUserDep,
    service: AiServiceDep,
):
    """
    Stream an AI response for the given prompt.

    The frontend sends a POST with the prompt, and receives
    a streaming response with text/event-stream content type.
    Each chunk is a piece of the LLM's response that can be
    displayed immediately.
    """

    async def event_stream():
        """
        Wraps the service's async generator into SSE format.

        SSE protocol requires each event to be formatted as:
            data: <content>\n\n

        The "data: " prefix and double newline are part of the
        SSE spec — the browser's EventSource API expects this
        exact format to parse events correctly.
        """
        try:
            async for chunk in service.chat(
                project_id=request.project_id,
                prompt=request.prompt,
                user_id=current_user.id,
                session_id=request.session_id,
            ):
                # SSE format: "data: <content>\n\n"
                yield f"data: {chunk}\n\n"

            # Signal that the stream is complete
            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            # Prevents buffering by proxies/load balancers
            "X-Accel-Buffering": "no",
            # Keeps the connection alive for streaming
            "Connection": "keep-alive",
        },
    )
