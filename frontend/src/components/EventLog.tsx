import { useEffect, useRef } from "react";
import type { GameState } from "../api/types";
import { describe } from "../game/describe";

export function EventLog({ game }: { game: GameState }) {
  const list = useRef<HTMLOListElement>(null);

  // Oldest first, like a chat: keep the latest event in view as new ones arrive.
  useEffect(() => {
    list.current?.scrollTo({ top: list.current.scrollHeight });
  }, [game.log.length]);

  return (
    <section className="card">
      <h2>Activity</h2>
      <ol ref={list} className="event-log">
        {game.log.map((event, index) => (
          <li key={index}>{describe(event, game)}</li>
        ))}
      </ol>
    </section>
  );
}
