import { readdir, readFile, stat } from "node:fs/promises";
import { extname, join, resolve } from "node:path";

const root = resolve(process.argv[2] || "_site");
const htmlFiles = [];

async function walk(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) await walk(path);
    else if (entry.isFile() && extname(entry.name) === ".html") htmlFiles.push(path);
  }
}

async function exists(path) {
  try { await stat(path); return true; } catch { return false; }
}

function candidates(fromFile, raw) {
  const clean = decodeURIComponent(raw.split("#")[0].split("?")[0]);
  const base = clean.startsWith("/") ? join(root, clean) : resolve(fromFile, "..", clean);
  if (clean.endsWith("/")) return [join(base, "index.html")];
  if (extname(base)) return [base];
  return [base, base + ".html", join(base, "index.html")];
}

await walk(root);
const broken = [];

for (const file of htmlFiles) {
  const html = await readFile(file, "utf8");
  const matches = html.matchAll(/(?:href|src)=["']([^"']+)["']/g);
  for (const [, value] of matches) {
    if (!value || value.startsWith("#") || /^(?:https?:|mailto:|tel:|data:|javascript:|\/\/)/i.test(value) || value.includes("{{")) continue;
    const options = candidates(file, value);
    if (!(await Promise.all(options.map(exists))).some(Boolean)) {
      broken.push({ file: file.slice(root.length + 1), target: value });
    }
  }
}

if (broken.length) {
  console.error("Broken internal references:");
  for (const item of broken) console.error(`- ${item.file}: ${item.target}`);
  process.exit(1);
}

console.log(`Checked ${htmlFiles.length} HTML files: no broken internal references.`);
