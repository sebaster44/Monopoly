import { GameScreen } from "./components/GameScreen";
import { Lobby } from "./components/Lobby";
import { useGame } from "./hooks/useGame";

export function App() {
  const { game, seat, error, create, join, rollDice, leave } = useGame();

  return (
    <main className="app">
      <h1>Monopoly</h1>
      {error !== null && <p className="error">{error}</p>}
      {game !== null && seat !== null ? (
        <GameScreen game={game} myId={seat.playerId} onRoll={rollDice} onLeave={leave} />
      ) : (
        <Lobby onCreate={create} onJoin={join} />
      )}
    </main>
  );
}
