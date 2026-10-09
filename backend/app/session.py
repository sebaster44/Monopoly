from fastapi import WebSocket

from app.domain.errors import GameError
from app.lobby import Lobby
from app.room import Room, Seat


class NotSeated(GameError):
    def __init__(self) -> None:
        super().__init__("Create or join a game first")


class AlreadySeated(GameError):
    def __init__(self) -> None:
        super().__init__("This connection already takes part in a game")


class Session:
    """One WebSocket connection and the seat it occupies, if any."""

    def __init__(self, socket: WebSocket, lobby: Lobby) -> None:
        self.socket = socket
        self.lobby = lobby
        self._room: Room | None = None
        self._seat: Seat | None = None

    async def join(self, room: Room, name: str) -> Seat:
        self._ensure_unseated()
        self._seat = await room.join(name, self.socket)
        self._room = room
        return self._seat

    async def reconnect(self, room: Room, token: str) -> Seat:
        self._ensure_unseated()
        self._seat = await room.reconnect(token, self.socket)
        self._room = room
        return self._seat

    async def play_turn(self) -> None:
        if self._room is None or self._seat is None:
            raise NotSeated()
        await self._room.play_turn(self._seat.player_id)

    def close(self) -> None:
        if self._room is not None and self._seat is not None:
            self._room.disconnect(self._seat.player_id, self.socket)

    def _ensure_unseated(self) -> None:
        if self._room is not None:
            raise AlreadySeated()
