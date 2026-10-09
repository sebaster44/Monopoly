import asyncio
import secrets
from contextlib import suppress
from dataclasses import dataclass

from fastapi import WebSocket, WebSocketDisconnect

from app.domain.errors import GameError
from app.domain.game import Game
from app.rpc.protocol import Message, notification_message
from app.views import game_view

STATE_NOTIFICATION = "game.updated"


class UnknownToken(GameError):
    def __init__(self) -> None:
        super().__init__("This seat token is not valid for this game")


@dataclass(frozen=True)
class Seat:
    player_id: str
    token: str  # secret that lets the player take the seat back after reconnecting


class Room:
    """A game and the sockets of its players. Every change is broadcast to all of them."""

    def __init__(self, code: str, game: Game) -> None:
        self.code = code
        self._game = game
        self._tokens: dict[str, str] = {}  # token -> player id
        self._sockets: dict[str, WebSocket] = {}  # player id -> live socket
        # Held across "change + broadcast" so that concurrent turns cannot interleave their
        # broadcasts and deliver states out of order.
        self._lock = asyncio.Lock()

    async def join(self, name: str, socket: WebSocket) -> Seat:
        async with self._lock:
            player = self._game.add_player(name)
            seat = Seat(player.id, secrets.token_urlsafe(16))
            self._tokens[seat.token] = player.id
            self._sockets[player.id] = socket
            await self._broadcast()
        return seat

    async def reconnect(self, token: str, socket: WebSocket) -> str:
        player_id = self._tokens.get(token)
        if player_id is None:
            raise UnknownToken()
        async with self._lock:
            self._sockets[player_id] = socket
            await socket.send_json(self._state_message())
        return player_id

    async def play_turn(self, player_id: str) -> None:
        async with self._lock:
            self._game.play_turn(player_id)
            await self._broadcast()

    def disconnect(self, player_id: str, socket: WebSocket) -> None:
        # The player may already have reconnected on a newer socket; keep that one.
        if self._sockets.get(player_id) is socket:
            del self._sockets[player_id]

    async def _broadcast(self) -> None:
        message = self._state_message()
        for socket in list(self._sockets.values()):
            # A socket closing mid-broadcast is cleaned up by its own endpoint.
            with suppress(WebSocketDisconnect, RuntimeError):
                await socket.send_json(message)

    def _state_message(self) -> Message:
        return notification_message(STATE_NOTIFICATION, game_view(self.code, self._game))
