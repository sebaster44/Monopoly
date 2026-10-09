"""The JSON-RPC methods exposed to clients."""

from typing import Annotated

from pydantic import Field

from app.domain.rules import MAX_SEATS, MIN_SEATS
from app.room import Seat
from app.rpc.dispatcher import Method
from app.rpc.protocol import CamelModel
from app.session import Session

type PlayerName = Annotated[str, Field(min_length=1, max_length=20)]


class CreateParams(CamelModel):
    player_name: PlayerName
    seats: int = Field(ge=MIN_SEATS, le=MAX_SEATS)


class JoinParams(CamelModel):
    game_code: str
    player_name: PlayerName


class ReconnectParams(CamelModel):
    game_code: str
    token: str


class NoParams(CamelModel):
    pass


async def create_game(params: CreateParams, session: Session) -> Seat:
    room = session.lobby.open(params.seats)
    return await session.join(room, params.player_name)


async def join_game(params: JoinParams, session: Session) -> Seat:
    room = session.lobby.find(params.game_code)
    return await session.join(room, params.player_name)


async def reconnect(params: ReconnectParams, session: Session) -> Seat:
    room = session.lobby.find(params.game_code)
    return await session.reconnect(room, params.token)


async def roll_dice(_: NoParams, session: Session) -> None:
    await session.play_turn()


METHODS: dict[str, Method[Session]] = {
    "game.create": Method(CreateParams, create_game),
    "game.join": Method(JoinParams, join_game),
    "game.reconnect": Method(ReconnectParams, reconnect),
    "game.rollDice": Method(NoParams, roll_dice),
}
