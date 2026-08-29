import { readFile, stat } from "node:fs/promises";

const failures = [];
const required = [
  "about.md", "contact.md", "privacy.md", "cookies.md", "terms.md", "disclaimer.md",
  "404.html", "robots.txt", "ads.txt", "_includes/ad-slot.html", "_includes/adsense-head.html",
  "assets/img/favicon.svg"
];

async function exists(path) {
  try { await stat(path); return true; } catch { return false; }
}

for (const path of required) {
  if (!(await exists(path))) failures.push(`Missing required file: ${path}`);
}

const index = await readFile("index.html", "utf8");
const blogLayout = await readFile("_layouts/blog.html", "utf8");
const pageLayout = await readFile("_layouts/page.html", "utf8");
const config = await readFile("_config.yml", "utf8");
const ads = await readFile("ads.txt", "utf8");
const mainCss = await readFile("assets/css/main.css", "utf8");
const blogCss = await readFile("assets/css/blog.css", "utf8");
const sharedCss = await readFile("assets/css/shared.css", "utf8");

const allText = [index, blogLayout, pageLayout, config, ads].join("\n");
if (/ca-pub-\d+/.test(allText)) failures.push("A hard-coded AdSense publisher ID remains.");
if (!index.includes("{% include adsense-head.html %}")) failures.push("Portfolio does not load configurable AdSense head include.");
if (!blogLayout.includes("{% include adsense-head.html %}")) failures.push("Blog does not load configurable AdSense head include.");
if (!index.includes('"@type": "Person"')) failures.push("Portfolio Person structured data is missing.");
if (!config.includes("jekyll-sitemap")) failures.push("jekyll-sitemap is not configured.");
if (!ads.includes("AdSense is not active")) failures.push("ads.txt is not clearly marked inactive.");
if (/Lorem ipsum|>Dropdown<|forms\/contact\.php|service-details\.html|portfolio-details\.html/i.test(allText)) failures.push("Obsolete template or broken-form content remains.");
if (blogLayout.includes("my-profile-img.jpg")) failures.push("Blog header still downloads the large profile image.");

function equalCount(label, text, open, close) {
  const a = (text.match(open) || []).length;
  const b = (text.match(close) || []).length;
  if (a !== b) failures.push(`${label} is unbalanced: ${a} / ${b}`);
}
equalCount("Portfolio div tags", index, /<div\b/g, /<\/div>/g);
equalCount("Portfolio section tags", index, /<section\b/g, /<\/section>/g);
for (const [name, css] of [["main.css", mainCss], ["blog.css", blogCss], ["shared.css", sharedCss]]) {
  equalCount(name + " braces", css, /\{/g, /\}/g);
}

const localRefs = [...index.matchAll(/(?:href|src)=["']([^"'{}]+)["']/g)]
  .map((match) => match[1])
  .filter((value) => !/^(?:https?:|mailto:|tel:|#|\/\/)/i.test(value));
for (const value of localRefs) {
  const path = value.split(/[?#]/)[0].replace(/^\//, "");
  if (path && !(await exists(path)) && !(await exists(path + ".html")) && !(await exists(path + "/index.html"))) {
    failures.push(`Missing portfolio reference: ${value}`);
  }
}

if (failures.length) {
  console.error(failures.map((item) => "- " + item).join("\n"));
  process.exit(1);
}
console.log("Source audit passed.");
