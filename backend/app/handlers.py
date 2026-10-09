"""The JSON-RPC methods exposed to clients."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.domain.rules import MAX_SEATS, MIN_SEATS
from app.rpc.dispatcher import Method
from app.session import Session


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


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


class SeatResult(CamelModel):
    game_code: str
    player_id: str
    token: str


async def create_game(params: CreateParams, session: Session) -> SeatResult:
    room = session.lobby.open(params.seats)
    seat = await session.join(room, params.player_name)
    return SeatResult(game_code=room.code, player_id=seat.player_id, token=seat.token)


async def join_game(params: JoinParams, session: Session) -> SeatResult:
    room = session.lobby.find(params.game_code)
    seat = await session.join(room, params.player_name)
    return SeatResult(game_code=room.code, player_id=seat.player_id, token=seat.token)


async def reconnect(params: ReconnectParams, session: Session) -> SeatResult:
    room = session.lobby.find(params.game_code)
    player_id = await session.reconnect(room, params.token)
    return SeatResult(game_code=room.code, player_id=player_id, token=params.token)


async def roll_dice(_: NoParams, session: Session) -> None:
    await session.play_turn()


METHODS: dict[str, Method[Session]] = {
    "game.create": Method(CreateParams, create_game),
    "game.join": Method(JoinParams, join_game),
    "game.reconnect": Method(ReconnectParams, reconnect),
    "game.rollDice": Method(NoParams, roll_dice),
}
