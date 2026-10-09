import type { GameState, Player } from "../api/types";

const COLORS = ["#e4572e", "#2e86ab", "#3bb273", "#a23b72"];

export function playerColor(game: GameState, playerId: string): string {
  const index = game.players.findIndex((player) => player.id === playerId);
  return COLORS[index] ?? "gray";
}

export function playerName(game: GameState, playerId: string): string {
  return game.players.find((player) => player.id === playerId)?.name ?? "Unknown player";
}

export function propertiesOf(game: GameState, player: Player): string[] {
  return game.board.flatMap((square) =>
    square.kind === "property" && square.ownerId === player.id ? [square.name] : [],
  );
}

export function formatMoney(amount: number): string {
  return `$${amount.toLocaleString("en-US")}`;
}
