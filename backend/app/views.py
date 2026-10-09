"""JSON snapshots of the game sent to clients. Keys are camelCase for the TypeScript side."""

from dataclasses import asdict

from pydantic.alias_generators import to_camel

from app.domain.board import Property, Square
from app.domain.events import Event
from app.domain.game import Game
from app.domain.player import Player
from app.rpc.protocol import Message


def game_view(code: str, game: Game) -> Message:
    current = game.current_player
    return {
        "code": code,
        "status": game.status.value,
        "seats": game.seats,
        "board": [
            _square_view(square, game.owners.get(position))
            for position, square in enumerate(game.rules.board)
        ],
        "players": [_player_view(player) for player in game.players],
        "currentPlayerId": None if current is None else current.id,
        "winnerId": game.winner_id,
        "log": [_event_view(event) for event in game.log],
    }


def _square_view(square: Square, owner_id: str | None) -> Message:
    if isinstance(square, Property):
        return {
            "kind": "property",
            "name": square.name,
            "price": square.price,
            "rent": square.rent,
            "ownerId": owner_id,
        }
    return {"kind": "empty", "name": square.name}


def _player_view(player: Player) -> Message:
    return {
        "id": player.id,
        "name": player.name,
        "money": player.money,
        "position": player.position,
        "isBankrupt": player.is_bankrupt,
    }


def _event_view(event: Event) -> Message:
    fields = {to_camel(name): value for name, value in asdict(event).items()}
    return {"type": type(event).__name__, **fields}
