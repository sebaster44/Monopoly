import { RpcClient } from "./rpcClient";
import type { GameState, Seat } from "./types";

// Results are cast to their documented shapes: the server is the source of truth for them.
export class GameApi {
  private readonly rpc: RpcClient;

  constructor(url: string, onClose: () => void) {
    this.rpc = new RpcClient(url, onClose);
  }

  async create(playerName: string, seats: number): Promise<Seat> {
    return (await this.rpc.call("game.create", { playerName, seats })) as Seat;
  }

  async join(gameCode: string, playerName: string): Promise<Seat> {
    return (await this.rpc.call("game.join", { gameCode, playerName })) as Seat;
  }

  async reconnect(gameCode: string, token: string): Promise<Seat> {
    return (await this.rpc.call("game.reconnect", { gameCode, token })) as Seat;
  }

  async rollDice(): Promise<void> {
    await this.rpc.call("game.rollDice");
  }

  onUpdate(listener: (state: GameState) => void): void {
    this.rpc.onNotification("game.updated", (params) => listener(params as GameState));
  }

  close(): void {
    this.rpc.close();
  }
}
