import pytest

from tests.support import GAME_ERROR, Connect, RpcFailure, ScriptedDie, StartGame


def test_host_waits_alone_until_others_join(connect: Connect) -> None:
    host = connect()

    seat = host.call("game.create", playerName="Alice", seats=3)

    assert seat["playerId"] == "p1"
    assert host.state["code"] == seat["gameCode"]
    assert host.state["status"] == "waiting"
    assert host.state["seats"] == 3


def test_game_code_is_case_insensitive(connect: Connect) -> None:
    host = connect()
    code = host.call("game.create", playerName="Alice", seats=2)["gameCode"]

    seat = connect().call("game.join", gameCode=code.lower(), playerName="Bob")

    assert seat["gameCode"] == code


def test_full_game_cannot_be_joined(start_game: StartGame, connect: Connect) -> None:
    alice, _ = start_game(2)

    with pytest.raises(RpcFailure, match="already full") as failure:
        connect().call("game.join", gameCode=alice.seat["gameCode"], playerName="Eve")
    assert failure.value.code == GAME_ERROR


def test_unknown_game_code_is_rejected(connect: Connect) -> None:
    with pytest.raises(RpcFailure, match="No game found") as failure:
        connect().call("game.join", gameCode="NOPE9", playerName="Eve")
    assert failure.value.code == GAME_ERROR


def test_connection_cannot_take_two_seats(connect: Connect) -> None:
    host = connect()
    code = host.call("game.create", playerName="Alice", seats=2)["gameCode"]

    with pytest.raises(RpcFailure, match="already takes part") as failure:
        host.call("game.join", gameCode=code, playerName="Alice again")
    assert failure.value.code == GAME_ERROR


def test_rolling_requires_a_seat(connect: Connect) -> None:
    with pytest.raises(RpcFailure, match="Create or join") as failure:
        connect().call("game.rollDice")
    assert failure.value.code == GAME_ERROR


def test_player_takes_their_seat_back_with_the_token(
    start_game: StartGame, connect: Connect, die: ScriptedDie
) -> None:
    alice, bob = start_game(2)
    returning = connect()

    seat = returning.call(
        "game.reconnect", gameCode=alice.seat["gameCode"], token=alice.seat["token"]
    )
    die.rolls = [1]
    returning.call("game.rollDice")

    assert seat["playerId"] == alice.seat["playerId"]
    assert bob.receive_state()["board"][1]["ownerId"] == alice.seat["playerId"]


def test_reconnect_with_a_wrong_token_is_rejected(start_game: StartGame, connect: Connect) -> None:
    alice, _ = start_game(2)

    with pytest.raises(RpcFailure, match="token") as failure:
        connect().call("game.reconnect", gameCode=alice.seat["gameCode"], token="forged")
    assert failure.value.code == GAME_ERROR
