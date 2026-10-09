import asyncio
import secrets
from contextlib import suppress

from fastapi import WebSocket, WebSocketDisconnect

from app.domain.errors import GameError
from app.domain.game import Game
from app.rpc.protocol import CamelModel, Message, notification_message
from app.views import game_view

STATE_NOTIFICATION = "game.updated"


class UnknownToken(GameError):
    def __init__(self) -> None:
        super().__init__("This seat token is not valid for this game")


class Seat(CamelModel):
    """A player's place in a game. The token lets them take it back after reconnecting."""

    game_code: str
    player_id: str
    token: str


class Room:
    """A game and the sockets of its players. Every change is broadcast to all of them."""

    def __init__(self, code: str, game: Game) -> None:
        self.code = code
        self._game = game
        self._seats: dict[str, Seat] = {}  # by token
        self._sockets: dict[str, WebSocket] = {}  # player id -> live socket
        # Held across "change + broadcast" so that concurrent turns cannot interleave their
        # broadcasts and deliver states out of order.
        self._lock = asyncio.Lock()

    async def join(self, name: str, socket: WebSocket) -> Seat:
        async with self._lock:
            player = self._game.add_player(name)
            seat = Seat(game_code=self.code, player_id=player.id, token=secrets.token_urlsafe(16))
            self._seats[seat.token] = seat
            self._sockets[player.id] = socket
            await self._broadcast()
        return seat

    async def reconnect(self, token: str, socket: WebSocket) -> Seat:
        seat = self._seats.get(token)
        if seat is None:
            raise UnknownToken()
        async with self._lock:
            self._sockets[seat.player_id] = socket
            await socket.send_json(self._state_message())
        return seat

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
