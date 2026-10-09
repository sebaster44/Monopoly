import type { GameState } from "../api/types";
import { formatMoney, playerColor, propertiesOf } from "../game/players";

type Props = { game: GameState; myId: string };

export function Players({ game, myId }: Props) {
  return (
    <section className="card">
      <h2>Players</h2>
      <ul className="players">
        {game.players.map((player) => {
          const properties = propertiesOf(game, player);
          const classes = [
            "player",
            player.id === game.currentPlayerId ? "current" : "",
            player.isBankrupt ? "bankrupt" : "",
          ];
          return (
            <li key={player.id} className={classes.join(" ")}>
              <div className="player-header">
                <span className="token" style={{ background: playerColor(game, player.id) }} />
                <strong>{player.name}</strong>
                {player.id === myId && <span className="tag">you</span>}
                {player.isBankrupt && <span className="tag">bankrupt</span>}
                <span className="money">{formatMoney(player.money)}</span>
              </div>
              <div className="properties">
                {properties.length === 0 ? "No properties" : properties.join(", ")}
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
