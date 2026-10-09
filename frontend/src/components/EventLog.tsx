import type { GameState } from "../api/types";
import { describe } from "../game/describe";

export function EventLog({ game }: { game: GameState }) {
  const newestFirst = game.log.map((event) => describe(event, game)).reverse();

  return (
    <section className="card">
      <h2>Activity</h2>
      <ol className="event-log">
        {newestFirst.map((line, index) => (
          <li key={game.log.length - index}>{line}</li>
        ))}
      </ol>
    </section>
  );
}
