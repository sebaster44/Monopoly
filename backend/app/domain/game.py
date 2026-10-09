from collections.abc import Callable
from enum import StrEnum

from app.domain.board import Property
from app.domain.errors import GameFull, GameNotInProgress, InvalidSeatCount, NotYourTurn
from app.domain.events import (
    Event,
    GameStarted,
    GameWon,
    Moved,
    PlayerBankrupted,
    PlayerJoined,
    PropertyBought,
    RentPaid,
    SalaryCollected,
)
from app.domain.player import Player
from app.domain.rules import MAX_SEATS, MIN_SEATS, Rules


class GameStatus(StrEnum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"


class Game:
    def __init__(self, seats: int, roll_die: Callable[[], int], rules: Rules) -> None:
        if not MIN_SEATS <= seats <= MAX_SEATS:
            raise InvalidSeatCount(MIN_SEATS, MAX_SEATS)
        self.seats = seats
        self.rules = rules
        self.status = GameStatus.WAITING
        self.players: list[Player] = []
        self.owners: dict[int, str] = {}  # board position -> owner's player id
        self.winner_id: str | None = None
        self.log: list[Event] = []
        self._turn = 0  # index into players
        self._roll_die = roll_die

    @property
    def current_player(self) -> Player | None:
        return self.players[self._turn] if self.status is GameStatus.PLAYING else None

    def add_player(self, name: str) -> Player:
        if self.status is not GameStatus.WAITING:
            raise GameFull()
        player = Player(id=f"p{len(self.players) + 1}", name=name, money=self.rules.starting_money)
        self.players.append(player)
        self.log.append(PlayerJoined(player.id))
        if len(self.players) == self.seats:
            self._start()
        return player

    def play_turn(self, player_id: str) -> None:
        player = self.current_player
        if player is None:
            raise GameNotInProgress()
        if player.id != player_id:
            raise NotYourTurn()
        self._move(player, self._roll_die())
        self._resolve_square(player)
        if self.status is GameStatus.PLAYING:
            self._pass_turn()

    def _start(self) -> None:
        self.status = GameStatus.PLAYING
        self.log.append(GameStarted())

    def _move(self, player: Player, roll: int) -> None:
        laps, player.position = divmod(player.position + roll, len(self.rules.board))
        self.log.append(Moved(player.id, roll, player.position))
        if laps:
            player.money += self.rules.start_salary
            self.log.append(SalaryCollected(player.id, self.rules.start_salary))

    def _resolve_square(self, player: Player) -> None:
        square = self.rules.board[player.position]
        if not isinstance(square, Property):
            return
        owner_id = self.owners.get(player.position)
        if owner_id is None:
            self._buy(player, square)
        elif owner_id != player.id:
            self._pay_rent(player, self._player(owner_id), square)

    def _buy(self, player: Player, square: Property) -> None:
        if player.money < square.price:
            return
        player.money -= square.price
        self.owners[player.position] = player.id
        self.log.append(PropertyBought(player.id, player.position, square.price))

    def _pay_rent(self, payer: Player, owner: Player, square: Property) -> None:
        if payer.money < square.rent:
            self._bankrupt(payer, creditor=owner)
            return
        payer.money -= square.rent
        owner.money += square.rent
        self.log.append(RentPaid(payer.id, owner.id, payer.position, square.rent))

    def _bankrupt(self, player: Player, creditor: Player) -> None:
        creditor.money += player.money
        player.money = 0
        player.is_bankrupt = True
        self.owners = {
            position: owner for position, owner in self.owners.items() if owner != player.id
        }
        self.log.append(PlayerBankrupted(player.id, creditor.id))
        remaining = [p for p in self.players if not p.is_bankrupt]
        if len(remaining) == 1:
            self._finish(winner=remaining[0])

    def _finish(self, winner: Player) -> None:
        self.status = GameStatus.FINISHED
        self.winner_id = winner.id
        self.log.append(GameWon(winner.id))

    def _pass_turn(self) -> None:
        self._turn = (self._turn + 1) % len(self.players)
        while self.players[self._turn].is_bankrupt:
            self._turn = (self._turn + 1) % len(self.players)

    def _player(self, player_id: str) -> Player:
        return next(p for p in self.players if p.id == player_id)
