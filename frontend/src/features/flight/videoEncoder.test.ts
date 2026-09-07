import { describe, expect, it } from "vitest";
import { VideoEncoderClient, abortable } from "./videoEncoder";

// WebCodecs and Worker are browser-only. Keep the real client and control only
// the worker transport, including a worker that never acknowledges its work.
class WorkerTransport extends EventTarget {
  sent: { id: number; type: string }[] = [];
  terminated = false;
  postMessage(message: { id: number; type: string }) {
    this.sent.push(message);
  }
  terminate() {
    this.terminated = true;
  }
  reply(data: unknown) {
    this.dispatchEvent(new MessageEvent("message", { data }));
  }
}

describe("export encoder lifetime", () => {
  it.each(["start", "add", "finalize"] as const)(
    "aborts while %s acknowledgement is pending",
    async (stage) => {
      const worker = new WorkerTransport();
      const controller = new AbortController();
      const encoder = new VideoEncoderClient(
        worker as unknown as Worker,
        controller.signal,
      );
      let bitmapClosed = false;
      const bitmap = {
        close() {
          bitmapClosed = true;
        },
      } as ImageBitmap;
      const pending =
        stage === "start"
          ? encoder.start(1920, 1080)
          : stage === "add"
            ? encoder.add(bitmap, 2 / 30, 1 / 30)
            : encoder.finalize();
      const rejected = expect(pending).rejects.toMatchObject({
        name: "AbortError",
      });
      controller.abort();
      await rejected;
      expect(worker.terminated).toBe(true);
      if (stage === "add") expect(bitmapClosed).toBe(true);
      // Late worker messages cannot restart or complete a canceled export.
      worker.reply({ id: worker.sent[0].id, buffer: new ArrayBuffer(3) });
      await expect(encoder.finalize()).rejects.toMatchObject({
        name: "AbortError",
      });
      expect(worker.sent).toHaveLength(1);
    },
  );

  it("waits for each acknowledgement and returns finalized MP4 bytes", async () => {
    const worker = new WorkerTransport();
    const controller = new AbortController();
    const encoder = new VideoEncoderClient(
      worker as unknown as Worker,
      controller.signal,
    );
    const start = encoder.start(1920, 1080);
    worker.reply({ id: worker.sent[0].id });
    await start;
    let acknowledged = false;
    const add = encoder
      .add({ close() {} } as ImageBitmap, 1 / 30, 1 / 30)
      .then(() => {
        acknowledged = true;
      });
    await Promise.resolve();
    expect(acknowledged).toBe(false);
    worker.reply({ id: worker.sent[1].id });
    await add;
    expect(acknowledged).toBe(true);
    const final = encoder.finalize();
    const buffer = new Uint8Array([1, 2, 3]).buffer;
    worker.reply({ id: worker.sent[2].id, buffer });
    expect(await final).toBe(buffer);
    encoder.dispose();
    expect(worker.terminated).toBe(true);
  });

  it("rejects worker failures and terminates the encoder", async () => {
    const worker = new WorkerTransport();
    const encoder = new VideoEncoderClient(
      worker as unknown as Worker,
      new AbortController().signal,
    );
    const pending = encoder.start(1920, 1080);
    worker.reply({
      id: worker.sent[0].id,
      error: "Encoder initialization failed",
    });
    await expect(pending).rejects.toThrow("Encoder initialization failed");
    expect(worker.terminated).toBe(true);
  });

  it("aborts capability/font initialization and observes its late rejection", async () => {
    const controller = new AbortController();
    let reject!: (reason: Error) => void;
    const initialization = new Promise<void>((_, fail) => {
      reject = fail;
    });
    const pending = abortable(initialization, controller.signal);
    const rejected = expect(pending).rejects.toMatchObject({
      name: "AbortError",
    });
    controller.abort();
    await rejected;
    reject(new Error("late initialization error"));
    await Promise.resolve();
  });
});
