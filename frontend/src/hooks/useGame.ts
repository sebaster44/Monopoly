import { useEffect, useState } from "react";
import { GameApi } from "../api/gameApi";
import type { GameState, Seat } from "../api/types";

// sessionStorage is per tab, so two tabs of one browser can play as two different players.
const SEAT_KEY = "monopoly.seat";

function loadSeat(): Seat | null {
  const saved = sessionStorage.getItem(SEAT_KEY);
  return saved === null ? null : (JSON.parse(saved) as Seat);
}

function saveSeat(seat: Seat | null): void {
  if (seat === null) sessionStorage.removeItem(SEAT_KEY);
  else sessionStorage.setItem(SEAT_KEY, JSON.stringify(seat));
}

function socketUrl(): string {
  const protocol = location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${location.host}/ws`;
}

export function useGame() {
  const [api, setApi] = useState<GameApi | null>(null);
  const [connection, setConnection] = useState(0);
  const [game, setGame] = useState<GameState | null>(null);
  const [seat, setSeat] = useState<Seat | null>(null);
  const [error, setError] = useState<string | null>(null);

  // A new connection per "session": the server binds a socket to at most one seat.
  useEffect(() => {
    const next = new GameApi(socketUrl(), () =>
      setError("Connection to the game server lost. Reload the page to reconnect."),
    );
    next.onUpdate(setGame);
    setApi(next);

    const saved = loadSeat();
    if (saved !== null) {
      next
        .reconnect(saved.gameCode, saved.token)
        .then(setSeat)
        .catch(() => saveSeat(null));
    }
    return () => next.close();
  }, [connection]);

  async function attempt(action: () => Promise<void>): Promise<void> {
    setError(null);
    try {
      await action();
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : String(failure));
    }
  }

  function takeSeat(request: (api: GameApi) => Promise<Seat>): Promise<void> {
    return attempt(async () => {
      if (api === null) return;
      const taken = await request(api);
      saveSeat(taken);
      setSeat(taken);
    });
  }

  return {
    game,
    seat,
    error,
    create: (playerName: string, seats: number) => takeSeat((api) => api.create(playerName, seats)),
    join: (gameCode: string, playerName: string) =>
      takeSeat((api) => api.join(gameCode, playerName)),
    rollDice: () => attempt(async () => api?.rollDice()),
    leave: () => {
      saveSeat(null);
      setSeat(null);
      setGame(null);
      setError(null);
      setConnection((count) => count + 1);
    },
  };
}
