from dataclasses import dataclass

from app.domain.board import BOARD, Square

MIN_SEATS = 2
MAX_SEATS = 4


# Rents are high relative to money and salary on purpose: with only buying and rent, the
# salary otherwise outpaces rents and games rarely end.
@dataclass(frozen=True)
class Rules:
    board: tuple[Square, ...] = BOARD
    starting_money: int = 800
    start_salary: int = 100
