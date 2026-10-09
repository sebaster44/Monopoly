import { useState, type FormEvent } from "react";

type Props = {
  onCreate: (playerName: string, seats: number) => void;
  onJoin: (gameCode: string, playerName: string) => void;
};

const SEAT_CHOICES = [2, 3, 4];

export function Lobby({ onCreate, onJoin }: Props) {
  const invitedCode = new URLSearchParams(location.search).get("game") ?? "";
  const [name, setName] = useState("");
  const [seats, setSeats] = useState(2);
  const [code, setCode] = useState(invitedCode);
  const hasName = name.trim() !== "";

  function submit(event: FormEvent, action: () => void) {
    event.preventDefault();
    action();
  }

  return (
    <section className="lobby">
      <label className="field">
        Your name
        <input
          value={name}
          maxLength={20}
          autoFocus
          onChange={(event) => setName(event.target.value)}
        />
      </label>

      <div className="lobby-choices">
        <form className="card" onSubmit={(event) => submit(event, () => onCreate(name, seats))}>
          <h2>New game</h2>
          <label className="field">
            Players
            <select value={seats} onChange={(event) => setSeats(Number(event.target.value))}>
              {SEAT_CHOICES.map((count) => (
                <option key={count} value={count}>
                  {count}
                </option>
              ))}
            </select>
          </label>
          <button disabled={!hasName}>Create game</button>
        </form>

        <form className="card" onSubmit={(event) => submit(event, () => onJoin(code, name))}>
          <h2>Join a game</h2>
          <label className="field">
            Game code
            <input
              value={code}
              maxLength={5}
              onChange={(event) => setCode(event.target.value.toUpperCase())}
            />
          </label>
          <button disabled={!hasName || code.trim() === ""}>Join game</button>
        </form>
      </div>
    </section>
  );
}
