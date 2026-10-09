import type { GameEvent, GameState } from "../api/types";
import { formatMoney, playerName } from "./players";

export function describe(event: GameEvent, game: GameState): string {
  const name = (playerId: string) => playerName(game, playerId);
  const square = (position: number) => game.board[position]?.name ?? `square ${position}`;

  switch (event.type) {
    case "PlayerJoined":
      return `${name(event.playerId)} joined the game`;
    case "GameStarted":
      return "The game has started";
    case "Moved":
      return `${name(event.playerId)} rolled ${event.roll} and moved to ${square(event.position)}`;
    case "SalaryCollected":
      return `${name(event.playerId)} collected a ${formatMoney(event.amount)} salary`;
    case "PropertyBought":
      return `${name(event.playerId)} bought ${square(event.position)} for ${formatMoney(event.price)}`;
    case "RentPaid":
      return `${name(event.payerId)} paid ${formatMoney(event.amount)} rent to ${name(event.ownerId)}`;
    case "PlayerBankrupted":
      return `${name(event.playerId)} went bankrupt and is out of the game`;
    case "GameWon":
      return `${name(event.playerId)} wins the game!`;
  }
}
