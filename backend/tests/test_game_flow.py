import pytest

from tests.support import GAME_ERROR, Client, RpcFailure, ScriptedDie, StartGame


def last_event(client: Client) -> dict[str, object]:
    event: dict[str, object] = client.state["log"][-1]
    return event


def test_game_starts_when_last_seat_is_filled(start_game: StartGame) -> None:
    alice, bob = start_game(2)

    assert alice.state == bob.state
    assert alice.state["status"] == "playing"
    assert alice.state["currentPlayerId"] == alice.seat["playerId"]
    assert [player["money"] for player in alice.state["players"]] == [500, 500]


def test_landing_on_a_free_property_buys_it(start_game: StartGame, die: ScriptedDie) -> None:
    alice, bob = start_game(2)
    die.rolls = [1]

    alice.call("game.rollDice")
    state = bob.receive_state()

    assert state["board"][1]["ownerId"] == alice.seat["playerId"]
    assert bob.money_of(alice) == 400
    assert state["currentPlayerId"] == bob.seat["playerId"]


def test_landing_on_an_owned_property_pays_rent(start_game: StartGame, die: ScriptedDie) -> None:
    alice, bob = start_game(2)
    die.rolls = [1, 1]

    alice.call("game.rollDice")
    bob.call("game.rollDice")

    assert last_event(bob) == {
        "type": "RentPaid",
        "payerId": bob.seat["playerId"],
        "ownerId": alice.seat["playerId"],
        "position": 1,
        "amount": 50,
    }
    assert bob.money_of(alice) == 450
    assert bob.money_of(bob) == 450


def test_reaching_start_pays_the_salary(start_game: StartGame, die: ScriptedDie) -> None:
    alice, _ = start_game(2)
    die.rolls = [4]

    alice.call("game.rollDice")

    assert last_event(alice) == {
        "type": "SalaryCollected",
        "playerId": alice.seat["playerId"],
        "amount": 100,
    }
    assert alice.money_of(alice) == 600


def test_player_who_cannot_pay_rent_goes_bankrupt_and_last_player_wins(
    start_game: StartGame, die: ScriptedDie
) -> None:
    alice, bob = start_game(2)
    die.rolls = [3, 3]

    alice.call("game.rollDice")
    bob.call("game.rollDice")
    state = alice.receive_state()

    assert [event["type"] for event in state["log"][-2:]] == ["PlayerBankrupted", "GameWon"]
    assert state["status"] == "finished"
    assert state["winnerId"] == alice.seat["playerId"]
    assert state["currentPlayerId"] is None
    assert alice.money_of(alice) == 300 + 500
    with pytest.raises(RpcFailure) as failure:
        alice.call("game.rollDice")
    assert failure.value.code == GAME_ERROR


def test_bankrupt_player_loses_properties_and_is_skipped(
    start_game: StartGame, die: ScriptedDie
) -> None:
    alice, bob, carol = start_game(3)
    # Alice buys Oak, Bob buys Maple, Carol idles, Alice wraps to Start, Bob lands on Oak.
    die.rolls = [3, 1, 2, 1, 2]

    for player in [alice, bob, carol, alice, bob]:
        player.call("game.rollDice")

    state = bob.state
    assert state["players"][1]["isBankrupt"] is True
    assert state["board"][1]["ownerId"] is None
    assert state["status"] == "playing"
    assert state["currentPlayerId"] == carol.seat["playerId"]

    die.rolls = [2]
    carol.call("game.rollDice")
    assert carol.state["currentPlayerId"] == alice.seat["playerId"]


def test_only_the_current_player_can_roll(start_game: StartGame) -> None:
    _, bob = start_game(2)

    with pytest.raises(RpcFailure, match="It is not your turn") as failure:
        bob.call("game.rollDice")
    assert failure.value.code == GAME_ERROR
