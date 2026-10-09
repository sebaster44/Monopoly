import type { GameState } from "../api/types";

export function WaitingRoom({ game }: { game: GameState }) {
  const link = `${location.origin}/?game=${game.code}`;

  return (
    <section className="card waiting-room">
      <h2>Waiting for players</h2>
      <p>
        Game code: <strong className="code">{game.code}</strong>
      </p>
      <p>
        Invite link: <a href={link}>{link}</a>{" "}
        <button onClick={() => navigator.clipboard.writeText(link)}>Copy</button>
      </p>
      <p>
        {game.players.length} / {game.seats} players joined. The game starts when everyone is here.
      </p>
      <ul>
        {game.players.map((player) => (
          <li key={player.id}>{player.name}</li>
        ))}
      </ul>
    </section>
  );
}
