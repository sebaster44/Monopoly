import random
from collections.abc import Callable

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.domain.rules import Rules
from app.handlers import METHODS
from app.lobby import Lobby
from app.rpc.dispatcher import Dispatcher
from app.session import Session

dispatcher = Dispatcher(METHODS)


def roll_six_sided_die() -> int:
    return random.randint(1, 6)


def create_app(
    roll_die: Callable[[], int] = roll_six_sided_die, rules: Rules | None = None
) -> FastAPI:
    app = FastAPI(title="Monopoly")
    lobby = Lobby(roll_die, rules or Rules())

    @app.websocket("/ws")
    async def game_socket(websocket: WebSocket) -> None:
        await websocket.accept()
        session = Session(websocket, lobby)
        try:
            while True:
                response = await dispatcher.handle(await websocket.receive_text(), session)
                if response is not None:
                    await websocket.send_json(response)
        except WebSocketDisconnect:
            session.close()

    return app


app = create_app()
