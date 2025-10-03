import { fal } from "@fal-ai/client";
import dotenv from "dotenv";

dotenv.config();

const result = await fal.subscribe("fal-ai/hunyuan-image/v3/text-to-image", {
  input: {
    prompt: "200mm telephoto through crowd gaps; subject laughing, candid; creamy background compression, color pop from a single bold garment, catchlight in eyes."
  },
  logs: true,
  onQueueUpdate: (update) => {
    if (update.status === "IN_PROGRESS") {
      update.logs.map((log) => log.message).forEach(console.log);
    }
  },
});
console.log(result.data);
console.log(result.requestId);
