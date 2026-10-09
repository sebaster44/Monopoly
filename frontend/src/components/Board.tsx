import type { ReactNode } from "react";
import type { GameState, Square } from "../api/types";
import { cellOf, gridSize } from "../game/board";
import { formatMoney, playerColor } from "../game/players";

type Props = { game: GameState; children: ReactNode };

export function Board({ game, children }: Props) {
  const size = gridSize(game.board.length);

  return (
    <div className="board" style={{ gridTemplate: `repeat(${size}, 1fr) / repeat(${size}, 1fr)` }}>
      {game.board.map((square, position) => {
        const { row, column } = cellOf(position, size);
        return (
          <div key={position} className="square" style={{ gridRow: row, gridColumn: column }}>
            <SquareContent game={game} square={square} position={position} />
          </div>
        );
      })}
      <div className="board-center" style={{ gridRow: `2 / ${size}`, gridColumn: `2 / ${size}` }}>
        {children}
      </div>
    </div>
  );
}

function SquareContent({
  game,
  square,
  position,
}: {
  game: GameState;
  square: Square;
  position: number;
}) {
  const visitors = game.players.filter(
    (player) => player.position === position && !player.isBankrupt,
  );

  return (
    <>
      {square.kind === "property" && (
        <div
          className="owner-band"
          style={{
            background: square.ownerId === null ? "transparent" : playerColor(game, square.ownerId),
          }}
        />
      )}
      <div className="square-name">{square.name}</div>
      {square.kind === "property" && (
        <div className="square-prices">
          {formatMoney(square.price)} · rent {formatMoney(square.rent)}
        </div>
      )}
      <div className="tokens">
        {visitors.map((player) => (
          <span
            key={player.id}
            className="token"
            title={player.name}
            style={{ background: playerColor(game, player.id) }}
          />
        ))}
      </div>
    </>
  );
}
