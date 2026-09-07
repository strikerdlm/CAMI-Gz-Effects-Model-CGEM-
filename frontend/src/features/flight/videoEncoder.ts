export type EncoderRequest =
  | { id: number; type: "start"; width: number; height: number }
  | {
      id: number;
      type: "add";
      bitmap: ImageBitmap;
      timestamp: number;
      duration: number;
    }
  | { id: number; type: "finalize" };
type EncoderReply = { id: number; buffer?: ArrayBuffer; error?: string };

/** Observe the original promise even after abort, including late rejections. */
export function abortable<T>(
  promise: PromiseLike<T>,
  signal: AbortSignal,
): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const abort = () => reject(signal.reason);
    signal.addEventListener("abort", abort, { once: true });
    if (signal.aborted) abort();
    Promise.resolve(promise)
      .then(resolve, reject)
      .finally(() => signal.removeEventListener("abort", abort));
  });
}

/** One worker owns every encoder resource, including pending native flushes.
 * Termination is independent of Mediabunny's non-cancelable finalize promise.
 */
export class VideoEncoderClient {
  private nextId = 0;
  private pending = new Map<
    number,
    {
      resolve: (buffer?: ArrayBuffer) => void;
      reject: (reason: unknown) => void;
    }
  >();
  private disposed = false;
  private failure: unknown = new Error("Video encoder is closed.");
  private worker: Worker;
  private signal: AbortSignal;

  constructor(worker: Worker, signal: AbortSignal) {
    this.worker = worker;
    this.signal = signal;
    worker.addEventListener("message", this.onMessage);
    worker.addEventListener("error", this.onError);
    worker.addEventListener("messageerror", this.onMessageError);
    signal.addEventListener("abort", this.onAbort, { once: true });
    if (signal.aborted) this.onAbort();
  }
  private onAbort = () => this.dispose(this.signal.reason);
  private onError = (event: ErrorEvent) =>
    this.dispose(new Error(event.message || "Video encoder worker failed."));
  private onMessageError = () =>
    this.dispose(new Error("Video encoder reply could not be read."));
  private onMessage = (event: MessageEvent<EncoderReply>) => {
    const reply = event.data;
    if (reply.error) {
      this.dispose(new Error(reply.error));
      return;
    }
    const pending = this.pending.get(reply.id);
    this.pending.delete(reply.id);
    pending?.resolve(reply.buffer);
  };
  private request(
    message: EncoderRequest,
    transfer: Transferable[] = [],
  ): Promise<ArrayBuffer | undefined> {
    if (this.disposed) return Promise.reject(this.failure);
    return new Promise((resolve, reject) => {
      this.pending.set(message.id, { resolve, reject });
      try {
        this.worker.postMessage(message, transfer);
      } catch (error) {
        this.dispose(error);
      }
    });
  }
  async start(width: number, height: number) {
    await this.request({ id: this.nextId++, type: "start", width, height });
  }
  async add(bitmap: ImageBitmap, timestamp: number, duration: number) {
    try {
      await this.request(
        { id: this.nextId++, type: "add", bitmap, timestamp, duration },
        [bitmap],
      );
    } finally {
      // Safe for transferred (detached) bitmaps; also closes untransferred ones on abort.
      bitmap.close();
    }
  }
  async finalize(): Promise<ArrayBuffer> {
    const buffer = await this.request({ id: this.nextId++, type: "finalize" });
    if (!buffer) throw new Error("The encoder produced no MP4 data.");
    return buffer;
  }
  dispose(reason: unknown = this.failure) {
    if (this.disposed) return;
    this.disposed = true;
    this.failure = reason;
    this.signal.removeEventListener("abort", this.onAbort);
    this.worker.removeEventListener("message", this.onMessage);
    this.worker.removeEventListener("error", this.onError);
    this.worker.removeEventListener("messageerror", this.onMessageError);
    this.worker.terminate();
    for (const pending of this.pending.values()) pending.reject(reason);
    this.pending.clear();
  }
}
