from collections.abc import Callable
from typing import Any

from starlette.testclient import WebSocketTestSession

from app.domain.board import EmptySquare, Property
from app.domain.rules import Rules

GAME_ERROR = -32000

# A tiny board keeps scenarios short: 1 step buys Maple, 3 steps buys Oak, 4 steps wraps to Start.
RULES = Rules(
    board=(
        EmptySquare("Start"),
        Property("Maple", price=100, rent=50),
        EmptySquare("Park"),
        Property("Oak", price=200, rent=600),
    ),
    starting_money=500,
    start_salary=100,
)


class ScriptedDie:
    def __init__(self) -> None:
        self.rolls: list[int] = []

    def __call__(self) -> int:
        return self.rolls.pop(0)


class RpcFailure(Exception):
    def __init__(self, error: dict[str, Any]) -> None:
        super().__init__(error["message"])
        self.code: int = error["code"]


class Client:
    """A test player talking JSON-RPC over its own WebSocket."""

    def __init__(self, socket: WebSocketTestSession) -> None:
        self.socket = socket
        self.seat: dict[str, Any] = {}  # result of game.create / game.join
        self.state: dict[str, Any] = {}  # latest game.updated snapshot
        self._next_id = 0

    def call(self, method: str, **params: Any) -> Any:
        self._next_id += 1
        self.socket.send_json(
            {"jsonrpc": "2.0", "id": self._next_id, "method": method, "params": params}
        )
        return self._response()

    def receive_state(self) -> dict[str, Any]:
        message = self.socket.receive_json()
        assert message["method"] == "game.updated"
        self.state = message["params"]
        return self.state

    def money_of(self, other: "Client") -> int:
        player = next(p for p in self.state["players"] if p["id"] == other.seat["playerId"])
        return int(player["money"])

    def _response(self) -> Any:
        """Read until the next response, keeping the latest state from notifications on the way."""
        while True:
            message = self.socket.receive_json()
            if "method" in message:
                self.state = message["params"]
            elif "error" in message:
                raise RpcFailure(message["error"])
            else:
                return message["result"]


type Connect = Callable[[], Client]
type StartGame = Callable[[int], list[Client]]
