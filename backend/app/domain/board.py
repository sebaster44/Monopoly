from dataclasses import dataclass


@dataclass(frozen=True)
class Property:
    name: str
    price: int
    rent: int


@dataclass(frozen=True)
class EmptySquare:
    name: str


type Square = Property | EmptySquare


# Index 0 is the starting square; the board wraps around after the last square.
BOARD: tuple[Square, ...] = (
    EmptySquare("Start"),
    Property("Maple Street", price=60, rent=90),
    Property("Cedar Lane", price=60, rent=90),
    EmptySquare("Rest Area"),
    Property("Birch Avenue", price=100, rent=150),
    Property("Oak Road", price=100, rent=150),
    Property("Pine Street", price=120, rent=180),
    EmptySquare("Park"),
    Property("Elm Street", price=140, rent=210),
    Property("Willow Way", price=160, rent=240),
    EmptySquare("Plaza"),
    Property("Ash Boulevard", price=180, rent=270),
    Property("Spruce Avenue", price=200, rent=300),
    Property("Poplar Place", price=220, rent=330),
    EmptySquare("Garden"),
    Property("Chestnut Drive", price=240, rent=360),
    Property("Walnut Square", price=260, rent=390),
    EmptySquare("Fountain"),
    Property("Sequoia Heights", price=300, rent=450),
    Property("Redwood Parkway", price=350, rent=525),
)
