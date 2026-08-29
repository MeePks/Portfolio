import { mkdir, writeFile } from "node:fs/promises";

const clientId = (process.env.ADSENSE_CLIENT_ID || "").trim();
const valid = clientId === "" || /^ca-pub-\d+$/.test(clientId);

if (!valid) {
  throw new Error("ADSENSE_CLIENT_ID must be empty or use the ca-pub-1234567890 format.");
}

await mkdir("_data", { recursive: true });
await writeFile(
  "_data/runtime.json",
  JSON.stringify({ adsense_client_id: clientId }, null, 2) + "\n",
  "utf8"
);

console.log(clientId ? "AdSense client ID configured for this build." : "AdSense remains disabled.");
