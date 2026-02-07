import { writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import data from "../book-data.zh.js";

const __filename = fileURLToPath(import.meta.url);
const ROOT = path.resolve(path.dirname(__filename), "..");

const ID_KEYS = new Set(["id", "group"]);
const RAW_ID_ARRAY_KEYS = new Set(["aliases"]);

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

const idToLabel = new Map(
  (Array.isArray(data.themes) ? data.themes : [])
    .filter((theme) => theme && theme.id && theme.label)
    .map((theme) => [String(theme.id), String(theme.label)])
);

const idEntries = Array.from(idToLabel.entries()).sort((a, b) => b[0].length - a[0].length);

function normalizeChinese(text) {
  if (typeof text !== "string") {
    return text;
  }

  let output = text;

  idEntries.forEach(([id, label]) => {
    const pattern = new RegExp(`(?<![A-Za-z0-9-])${escapeRegExp(id)}(?![A-Za-z0-9-])`, "g");
    output = output.replace(pattern, label);
  });

  const replacements = [
    [/industrial capitalism/gi, "工业资本主义"],
    [/war capitalism/gi, "战争资本主义"],
    [/market integration/gi, "市场整合"],
    [/growers\/cultivators/gi, "种植者/耕作者"],
    [/slaves\/enslaved/gi, "奴隶/被奴役者"],
    [/american south/gi, "美国南方"],
    [/new york/gi, "纽约"],
    [/north america/gi, "北美"],
    [/united states/gi, "美国"],
    [/west 非洲/gi, "西非"],
    [/\bstate-power\b/gi, "国家权力"],
    [/\bimperialism\b/gi, "帝国主义"],
    [/\bcoercion\b/gi, "强制"],
    [/\bmechanization\b/gi, "机械化"],
    [/ 的踪影可见：/g, "体现在："],
    [/之所以清晰可见，是因为/g, "体现在："],
    [/之所以可见，是因为/g, "体现在："],
    [/是清晰可见的：/g, "体现在："],
    [/清晰可见：/g, "体现在："],
    [/的可见之处在于：/g, "体现在："],
    [/可见之处在于：/g, "体现在："],
    [/的存在体现在：/g, "体现在："],
    [/\bU\s*S\b/g, "美国"],
    [/putting-out/g, "外发制"],
    [/，以及一个（/g, "（"],
    [/并利用基础设施和（/g, "并利用基础设施与信贷机制（"]
  ];

  replacements.forEach(([pattern, replacement]) => {
    output = output.replace(pattern, replacement);
  });

  output = output
    .replace(/\s+([，。；：])/g, "$1")
    .replace(/（\s+/g, "（")
    .replace(/\s+）/g, "）")
    .replace(/。。+/g, "。")
    .replace(/，{2,}/g, "，")
    .replace(/：：+/g, "：");

  return output;
}

function transform(value, key = "") {
  if (typeof value === "string") {
    if (ID_KEYS.has(key)) {
      return value;
    }
    return normalizeChinese(value);
  }

  if (Array.isArray(value)) {
    if (RAW_ID_ARRAY_KEYS.has(key)) {
      return [...value];
    }
    if (key === "themes" && value.every((item) => typeof item === "string")) {
      return [...value];
    }
    return value.map((item) => transform(item, key));
  }

  if (value && typeof value === "object") {
    const result = {};
    Object.entries(value).forEach(([childKey, childValue]) => {
      result[childKey] = transform(childValue, childKey);
    });
    return result;
  }

  return value;
}

const polished = transform(data);
const outputPath = path.join(ROOT, "book-data.zh.js");
const content = `const BOOK_DATA = ${JSON.stringify(polished, null, 2)};\n\nexport default BOOK_DATA;\n`;
await writeFile(outputPath, content, "utf8");
console.log("Polished book-data.zh.js");
