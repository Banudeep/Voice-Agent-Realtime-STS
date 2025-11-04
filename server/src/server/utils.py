from typing import AsyncIterator
from starlette.websockets import WebSocket, WebSocketDisconnect


async def websocket_stream(websocket: WebSocket) -> AsyncIterator[str]:
    """Yield text messages from `websocket` until the client disconnects.

    When the client disconnects, `websocket.receive_text()` raises
    `WebSocketDisconnect`. Catch it and end the iterator cleanly so callers
    (like `amerge`) do not receive unexpected exceptions.
    """
    while True:
        try:
            data = await websocket.receive_text()
        except WebSocketDisconnect:
            break
        yield data
