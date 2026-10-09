// Mirrors backend/app/views.py and the results in backend/app/handlers.py.

export type GameStatus = "waiting" | "playing" | "finished";

export type Square =
  | { kind: "empty"; name: string }
  | { kind: "property"; name: string; price: number; rent: number; ownerId: string | null };

export type Player = {
  id: string;
  name: string;
  money: number;
  position: number;
  isBankrupt: boolean;
};

export type GameEvent =
  | { type: "PlayerJoined"; playerId: string }
  | { type: "GameStarted" }
  | { type: "Moved"; playerId: string; roll: number; position: number }
  | { type: "SalaryCollected"; playerId: string; amount: number }
  | { type: "PropertyBought"; playerId: string; position: number; price: number }
  | { type: "RentPaid"; payerId: string; ownerId: string; position: number; amount: number }
  | { type: "PlayerBankrupted"; playerId: string; creditorId: string }
  | { type: "GameWon"; playerId: string };

export type GameState = {
  code: string;
  status: GameStatus;
  seats: number;
  board: Square[];
  players: Player[];
  currentPlayerId: string | null;
  winnerId: string | null;
  log: GameEvent[];
};

export type Seat = {
  gameCode: string;
  playerId: string;
  token: string;
};
