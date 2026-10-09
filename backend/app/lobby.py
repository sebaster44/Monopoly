import secrets
from collections.abc import Callable

from app.domain.errors import GameError
from app.domain.game import Game
from app.domain.rules import Rules
from app.room import Room

# Without 0/O and 1/I so codes are easy to read aloud and type.
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 5


class GameNotFound(GameError):
    def __init__(self, code: str) -> None:
        super().__init__(f"No game found with code {code}")


class Lobby:
    """In-memory registry of the open games, by game code."""

    def __init__(self, roll_die: Callable[[], int], rules: Rules) -> None:
        self._roll_die = roll_die
        self._rules = rules
        self._rooms: dict[str, Room] = {}

    def open(self, seats: int) -> Room:
        room = Room(self._new_code(), Game(seats, self._roll_die, self._rules))
        self._rooms[room.code] = room
        return room

    def find(self, code: str) -> Room:
        room = self._rooms.get(code.strip().upper())
        if room is None:
            raise GameNotFound(code)
        return room

    def _new_code(self) -> str:
        while True:
            code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
            if code not in self._rooms:
                return code
