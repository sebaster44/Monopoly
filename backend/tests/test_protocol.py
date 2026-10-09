"""JSON-RPC 2.0 error handling, observed on the raw socket."""

from typing import Any

import pytest

from tests.support import Connect


def send(connect: Connect, frame: str) -> dict[str, Any]:
    socket = connect().socket
    socket.send_text(frame)
    response: dict[str, Any] = socket.receive_json()
    return response


@pytest.mark.parametrize(
    ("frame", "request_id", "code"),
    [
        ("{not json", None, -32700),
        ('{"id": 1, "method": "game.rollDice"}', None, -32600),
        ('{"jsonrpc": "2.0", "id": 2, "method": "game.teleport"}', 2, -32601),
        (
            '{"jsonrpc": "2.0", "id": 3, "method": "game.create",'
            ' "params": {"playerName": "Alice", "seats": 5}}',
            3,
            -32602,
        ),
        (
            '{"jsonrpc": "2.0", "id": "four", "method": "game.create",'
            ' "params": {"playerName": "  ", "seats": 2}}',
            "four",
            -32602,
        ),
    ],
    ids=["parse error", "invalid request", "unknown method", "seats out of range", "blank name"],
)
def test_errors_follow_the_spec(
    connect: Connect, frame: str, request_id: int | str | None, code: int
) -> None:
    response = send(connect, frame)

    assert response["jsonrpc"] == "2.0"
    assert response["id"] == request_id
    assert response["error"]["code"] == code


def test_invalid_params_name_the_offending_field(connect: Connect) -> None:
    frame = '{"jsonrpc": "2.0", "id": 1, "method": "game.create", "params": {"playerName": "A"}}'

    response = send(connect, frame)

    assert response["error"]["data"] == [{"field": "seats", "message": "Field required"}]
