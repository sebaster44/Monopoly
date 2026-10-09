from collections.abc import Iterator
from contextlib import ExitStack

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from tests.support import RULES, Client, Connect, ScriptedDie, StartGame


@pytest.fixture
def die() -> ScriptedDie:
    return ScriptedDie()


@pytest.fixture
def connect(die: ScriptedDie) -> Iterator[Connect]:
    with TestClient(create_app(roll_die=die, rules=RULES)) as http, ExitStack() as sockets:
        yield lambda: Client(sockets.enter_context(http.websocket_connect("/ws")))


@pytest.fixture
def start_game(connect: Connect) -> StartGame:
    """Seat Alice, Bob, ... and return their clients once the game has started."""

    def start(seats: int) -> list[Client]:
        names = ["Alice", "Bob", "Carol", "Dave"][:seats]
        host = connect()
        host.seat = host.call("game.create", playerName=names[0], seats=seats)
        clients = [host]
        for name in names[1:]:
            guest = connect()
            guest.seat = guest.call("game.join", gameCode=host.seat["gameCode"], playerName=name)
            clients.append(guest)
        for client in clients:
            while client.state["status"] != "playing":
                client.receive_state()
        return clients

    return start
