import {
  BufferTarget,
  CanvasSource,
  Mp4OutputFormat,
  Output,
  Quality,
} from "mediabunny";
import type { EncoderRequest } from "./videoEncoder";

let canvas: OffscreenCanvas;
let context: OffscreenCanvasRenderingContext2D;
let output: Output;
let source: CanvasSource;
let target: BufferTarget;

// The client sends the next frame only after the previous acknowledgement.
// All native encoder/flush state stays in this disposable worker.
self.onmessage = async (event: MessageEvent<EncoderRequest>) => {
  const request = event.data;
  try {
    if (request.type === "start") {
      canvas = new OffscreenCanvas(request.width, request.height);
      const ctx = canvas.getContext("2d", { alpha: false });
      if (!ctx) throw new Error("Video encoding canvas is unavailable.");
      context = ctx;
      target = new BufferTarget();
      output = new Output({ format: new Mp4OutputFormat(), target });
      source = new CanvasSource(canvas, {
        codec: "avc",
        quality: new Quality({ bitrate: 8_000_000 }),
        keyFrameInterval: 2,
      });
      output.addVideoTrack(source, { frameRate: 30 });
      await output.start();
    } else if (request.type === "add") {
      try {
        context.drawImage(request.bitmap, 0, 0);
      } finally {
        request.bitmap.close();
      }
      await source.add(request.timestamp, request.duration);
    } else {
      await output.finalize();
      if (!target.buffer) throw new Error("The encoder produced no MP4 data.");
      self.postMessage(
        { id: request.id, buffer: target.buffer },
        { transfer: [target.buffer] },
      );
      return;
    }
    self.postMessage({ id: request.id });
  } catch (error) {
    // Report immediately; the client terminates this worker even if cancel would
    // wait forever on native encoder backpressure or finalization.
    self.postMessage({
      id: request.id,
      error: error instanceof Error ? error.message : "Video encoding failed.",
    });
  }
};
