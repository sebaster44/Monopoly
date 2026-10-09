import type { GameState } from "../api/types";
import { Board } from "./Board";
import { EventLog } from "./EventLog";
import { Players } from "./Players";
import { TurnPanel } from "./TurnPanel";
import { WaitingRoom } from "./WaitingRoom";

type Props = {
  game: GameState;
  myId: string;
  onRoll: () => void;
  onLeave: () => void;
};

export function GameScreen({ game, myId, onRoll, onLeave }: Props) {
  if (game.status === "waiting") return <WaitingRoom game={game} />;

  return (
    <div className="game-screen">
      <Board game={game}>
        <TurnPanel game={game} myId={myId} onRoll={onRoll} onLeave={onLeave} />
      </Board>
      <aside className="sidebar">
        <Players game={game} myId={myId} />
        <EventLog game={game} />
      </aside>
    </div>
  );
}
