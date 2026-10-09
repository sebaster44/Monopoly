class GameError(Exception):
    """A request that the game rules refuse. The message is safe to show to players."""


class InvalidSeatCount(GameError):
    def __init__(self, minimum: int, maximum: int) -> None:
        super().__init__(f"A game needs between {minimum} and {maximum} players")


class GameFull(GameError):
    def __init__(self) -> None:
        super().__init__("This game is already full")


class GameNotInProgress(GameError):
    def __init__(self) -> None:
        super().__init__("The game is not in progress")


class NotYourTurn(GameError):
    def __init__(self) -> None:
        super().__init__("It is not your turn")
