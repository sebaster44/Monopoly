type RequestId = number;

type Response =
  | { jsonrpc: "2.0"; id: RequestId; result: unknown }
  | { jsonrpc: "2.0"; id: RequestId | null; error: { code: number; message: string } };

type Notification = { jsonrpc: "2.0"; method: string; params: unknown };

type Pending = { resolve: (result: unknown) => void; reject: (error: Error) => void };

export class RpcError extends Error {
  readonly code: number;

  constructor(code: number, message: string) {
    super(message);
    this.code = code;
  }
}

/** JSON-RPC 2.0 client over a single WebSocket. */
export class RpcClient {
  private readonly socket: WebSocket;
  private readonly opened: Promise<void>;
  private readonly pending = new Map<RequestId, Pending>();
  private readonly listeners = new Map<string, (params: unknown) => void>();
  private nextId = 1;

  constructor(url: string, onClose: () => void) {
    this.socket = new WebSocket(url);
    this.opened = new Promise((resolve, reject) => {
      this.socket.onopen = () => resolve();
      this.socket.onerror = () => reject(new Error("Cannot reach the game server"));
    });
    this.socket.onmessage = (event: MessageEvent<string>) => this.receive(JSON.parse(event.data));
    this.socket.onclose = () => {
      this.rejectPending(new Error("Connection to the game server lost"));
      onClose();
    };
  }

  async call(method: string, params: object = {}): Promise<unknown> {
    await this.opened;
    const id = this.nextId++;
    const result = new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }));
    this.socket.send(JSON.stringify({ jsonrpc: "2.0", id, method, params }));
    return result;
  }

  onNotification(method: string, listener: (params: unknown) => void): void {
    this.listeners.set(method, listener);
  }

  /** Closes on purpose: handlers are detached first so no callback outlives the caller. */
  close(): void {
    this.socket.onopen = this.socket.onerror = this.socket.onmessage = this.socket.onclose = null;
    this.socket.close();
  }

  private receive(message: Response | Notification): void {
    if ("method" in message) {
      this.listeners.get(message.method)?.(message.params);
      return;
    }
    // A null id answers a frame the server could not parse; no call is waiting for it.
    if (message.id === null) return;
    const pending = this.pending.get(message.id);
    if (pending === undefined) return;
    this.pending.delete(message.id);
    if ("error" in message) pending.reject(new RpcError(message.error.code, message.error.message));
    else pending.resolve(message.result);
  }

  private rejectPending(error: Error): void {
    this.pending.forEach((pending) => pending.reject(error));
    this.pending.clear();
  }
}
