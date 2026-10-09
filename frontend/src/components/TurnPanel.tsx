import type { GameState } from "../api/types";
import { describe } from "../game/describe";
import { playerName } from "../game/players";

type Props = {
  game: GameState;
  myId: string;
  onRoll: () => void;
  onLeave: () => void;
};

export function TurnPanel({ game, myId, onRoll, onLeave }: Props) {
  const lastEvent = game.log.at(-1);

  return (
    <div className="turn-panel">
      <p className="code">Game {game.code}</p>
      <h2>{headline(game, myId)}</h2>
      {game.status === "finished" ? (
        <button onClick={onLeave}>New game</button>
      ) : (
        <button className="roll" disabled={game.currentPlayerId !== myId} onClick={onRoll}>
          Roll the die
        </button>
      )}
      {lastEvent !== undefined && <p className="last-event">{describe(lastEvent, game)}</p>}
    </div>
  );
}

function headline(game: GameState, myId: string): string {
  if (game.winnerId !== null) {
    return game.winnerId === myId ? "You win!" : `${playerName(game, game.winnerId)} wins!`;
  }
  if (game.currentPlayerId === myId) return "Your turn";
  if (game.currentPlayerId !== null) return `${playerName(game, game.currentPlayerId)} is playing`;
  return "";
}
