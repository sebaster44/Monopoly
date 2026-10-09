# Monopoly

A simplified multiplayer Monopoly game played in the browser.

- **Backend:** Python + FastAPI. One WebSocket endpoint; every message is JSON-RPC 2.0.
- **Frontend:** React + TypeScript (strict mode), built with Vite.

## Running the app

Prerequisites: Python 3.12+ and Node.js 20.19+.

**Quick start:** from the repository root, run

```bash
python start.py
```

It installs the dependencies on first run, starts both servers, and stops both on Ctrl+C. Then open
http://localhost:5173. Set `BACKEND_PORT` if port 8000 is taken.

Or start each part manually:

**1. Backend** (from `backend/`):

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --port 8000
```

**2. Frontend** (from `frontend/`, in a second terminal):

```bash
npm install
npm run dev
```

Open http://localhost:5173. Vite forwards `/ws` to the backend. If port 8000 is taken, start
uvicorn on another port and run `BACKEND_PORT=<port> npm run dev`.

**3. Play:** enter a name, pick the number of players (2–4) and create a game. Share the invite
link (or the 5-letter code) with the other players. Each of them opens it in their own browser or
tab, enters a name and joins. The game starts as soon as the last seat is filled. You can test alone
with several tabs: each tab is a separate player.

## Rules

- The board is a fixed loop of 20 squares: 14 properties and 6 empty squares, including Start.
- Everyone starts with $800. On your turn you roll one six-sided die and move forward.
- Passing or landing on Start pays a $100 salary.
- An unowned property is bought automatically if you can afford it. A property owned by someone
  else costs you its rent. Nothing happens on your own property or on an empty square.
- If you cannot pay a rent, you go bankrupt: your remaining money goes to the owner, your
  properties go back to the bank, and you are out. The last player standing wins.

Rents are high (1.5× the price) on purpose. With only buying and rent, a lower rent lets the
salary outpace rents, and simulated games mostly never ended. With these numbers, a 2-player game
lasts about 20 turns and a 4-player game about 50.

## Architecture

```
backend/app/
  domain/        Pure game rules, no framework code
    board.py       Squares (Property, EmptySquare) and the default board
    rules.py       Starting money, salary, seat limits
    game.py        Game aggregate: seats players, plays turns, records events
    events.py      What happened (Moved, PropertyBought, RentPaid, ...)
    errors.py      Rule violations (NotYourTurn, GameFull, ...)
  rpc/           Generic JSON-RPC 2.0 layer
    protocol.py    Message shapes and error codes
    dispatcher.py  Parses a frame, validates params, calls the method, builds the reply
  handlers.py    The exposed methods and their parameter/result models
  session.py     One WebSocket connection and the seat it occupies
  room.py        One game plus its players' sockets; applies changes and broadcasts state
  lobby.py       In-memory registry of games by code
  views.py       Game -> JSON snapshot sent to clients
  main.py        FastAPI app and the /ws endpoint

frontend/src/
  api/           RpcClient (JSON-RPC over WebSocket), typed GameApi, shared types
  hooks/         useGame: connection, game state, and the player's seat
  game/          Pure helpers: board layout, player lookups, event descriptions
  components/    Lobby, WaitingRoom, GameScreen (Board, TurnPanel, Players, EventLog)
```

Key choices:

- **The domain knows nothing about the transport.** `Game` takes the die as a function
  (`roll_die`), so tests use a scripted die instead of mocks.
- **The server is authoritative and sends full snapshots.** After every change, each player in
  the room receives `game.updated` with the full state, including the event log. Clients only render
  it, so they cannot drift apart, and a reconnecting player is caught up by a single message.
- **One lock per room** keeps "apply change + broadcast" atomic, so every player receives the
  states in the same order.
- **Seat tokens.** Joining returns a secret token. The browser keeps it in `sessionStorage` and uses
  it to take the seat back after a page reload.

## Protocol

Connect to `ws://<host>/ws` and exchange JSON-RPC 2.0 messages. Parameters are passed by name.

| Method           | Params                   | Result                          |
| ---------------- | ------------------------ | ------------------------------- |
| `game.create`    | `{ playerName, seats }`  | `{ gameCode, playerId, token }` |
| `game.join`      | `{ gameCode, playerName }` | `{ gameCode, playerId, token }` |
| `game.reconnect` | `{ gameCode, token }`    | `{ gameCode, playerId, token }` |
| `game.rollDice`  | `{}`                     | `null`                          |

Server notification: `game.updated` with the full game state (see `frontend/src/api/types.ts`).

Errors use the standard codes (`-32700` parse error, `-32600` invalid request, `-32601` method not
found, `-32602` invalid params, `-32603` internal error). `-32000` means the request breaks a
game rule (not your turn, game full, unknown code, ...); its message can be shown to players.
Batch requests are not supported.

## Development

Backend (from `backend/`):

```bash
pytest                 # integration tests through the WebSocket API
ruff check .           # lint
ruff format .          # format
mypy                   # strict type checking
```

Frontend (from `frontend/`):

```bash
npm run typecheck      # tsc in strict mode
npm run format         # prettier --write
npm run format:check   # prettier --check
npm run build          # production build
```

## Limitations

- Games live in memory: restarting the backend ends them. Finished games are not cleaned up.
- A player who leaves keeps their seat. Their turn waits until they come back.


## What I would do with more time
- More system tests.
- Some unit tests.
- Remove the "New game" section in the loby for guests.

