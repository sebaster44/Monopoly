from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerJoined:
    player_id: str


@dataclass(frozen=True)
class GameStarted:
    pass


@dataclass(frozen=True)
class Moved:
    player_id: str
    roll: int
    position: int


@dataclass(frozen=True)
class SalaryCollected:
    player_id: str
    amount: int


@dataclass(frozen=True)
class PropertyBought:
    player_id: str
    position: int
    price: int


@dataclass(frozen=True)
class RentPaid:
    payer_id: str
    owner_id: str
    position: int
    amount: int


@dataclass(frozen=True)
class PlayerBankrupted:
    player_id: str
    creditor_id: str


@dataclass(frozen=True)
class GameWon:
    player_id: str


type Event = (
    PlayerJoined
    | GameStarted
    | Moved
    | SalaryCollected
    | PropertyBought
    | RentPaid
    | PlayerBankrupted
    | GameWon
)
