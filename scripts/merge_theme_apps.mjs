/**
 * Merge similar theme applications across chapters.
 *
 * For each theme, this script:
 *   1. Strips boilerplate "In [setting], X is visible as ..." from point text.
 *   2. Computes pairwise text similarity between stripped points.
 *   3. Merges applications that exceed the similarity threshold into multi-chapter entries.
 *   4. Converts `chapter` (integer) → `chapters` (sorted array) in the output schema.
 *   5. Applies the same merge groupings to the Chinese data file for parity.
 *
 * Usage:  node scripts/merge_theme_apps.mjs
 */

import { readFileSync, writeFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");

// ---------- Config ----------

const SIM_THRESHOLD = 0.30;

// ---------- File I/O ----------

function parseBookData(filePath) {
  const content = readFileSync(filePath, "utf-8");
  const marker = "const BOOK_DATA = ";
  const start = content.indexOf(marker);
  if (start === -1) throw new Error(`Cannot find BOOK_DATA in ${filePath}`);
  const tail = content.indexOf("\nexport default BOOK_DATA;");
  if (tail === -1) throw new Error(`Cannot find export in ${filePath}`);
  // Extract the object literal (may end with ";")
  let objectLiteral = content.substring(start + marker.length, tail).trim();
  objectLiteral = objectLiteral.replace(/;\s*$/, "");
  return new Function(`return (${objectLiteral})`)();
}

function writeBookData(filePath, data) {
  const json = JSON.stringify(data, null, 2);
  const content = `const BOOK_DATA = ${json};\n\nexport default BOOK_DATA;\n`;
  writeFileSync(filePath, content, "utf-8");
}

// ---------- Text processing ----------

const STOP_WORDS = new Set([
  "the", "a", "an", "in", "on", "at", "to", "of", "and", "or", "is", "was",
  "were", "are", "as", "by", "for", "with", "that", "this", "it", "its",
  "from", "be", "been", "being", "had", "has", "have", "not", "but", "also",
  "then", "than", "more", "which", "who", "whom", "whose", "where", "when",
  "while", "into", "over", "under", "about", "after", "before", "between",
  "through", "during", "up", "out", "they", "their", "them", "he", "she",
  "his", "her", "its", "we", "our", "you", "your", "all", "each", "every",
  "both", "few", "many", "much", "most", "some", "any", "no", "other",
  "such", "only", "very", "can", "could", "would", "should", "will", "may",
  "might", "shall", "must", "do", "does", "did", "done", "just", "yet",
  "still", "so", "too", "if", "because", "since", "until", "unless",
  "visible", "chapter"
]);

function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/\([^)]*\)/g, " ") // remove parenthetical citations
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length > 2 && !STOP_WORDS.has(w));
}

function wordSet(text) {
  return new Set(tokenize(text));
}

function jaccard(setA, setB) {
  if (setA.size === 0 && setB.size === 0) return 0;
  let intersection = 0;
  for (const w of setA) if (setB.has(w)) intersection++;
  const union = setA.size + setB.size - intersection;
  return union === 0 ? 0 : intersection / union;
}

function overlapCoeff(setA, setB) {
  if (setA.size === 0 || setB.size === 0) return 0;
  let intersection = 0;
  for (const w of setA) if (setB.has(w)) intersection++;
  return intersection / Math.min(setA.size, setB.size);
}

function similarity(textA, textB) {
  const a = wordSet(textA);
  const b = wordSet(textB);
  return Math.max(jaccard(a, b), overlapCoeff(a, b));
}

// Also check evidence overlap for a second merge signal.
function evidenceOverlap(evA, evB) {
  const setA = new Set((evA || []).map((e) => e.toLowerCase().trim()));
  const setB = new Set((evB || []).map((e) => e.toLowerCase().trim()));
  if (setA.size === 0 || setB.size === 0) return 0;
  let intersection = 0;
  for (const e of setA) if (setB.has(e)) intersection++;
  return intersection / Math.min(setA.size, setB.size);
}

// ---------- Point text cleanup ----------

function stripEnglishPrefix(point) {
  // "In [setting], [theme] is visible as [content] ([time])."
  // The setting can contain commas, so anchor on "is visible as".
  let stripped = point.replace(/^.*?\bis visible as\b\s*/i, "");
  // Remove trailing parenthetical time/page reference
  stripped = stripped.replace(/\s*\([^)]*\)\s*\.?\s*$/, "");
  // Remove orphan trailing words (artifacts like "and a", "the")
  stripped = stripped.replace(/\s+(?:and\s+)?(?:a|an|the)\s*\.?\s*$/i, "");
  stripped = stripped.trim();
  if (!stripped || stripped.length < 10) return point; // fallback if stripping removed too much
  // Capitalize first letter
  stripped = stripped.charAt(0).toUpperCase() + stripped.slice(1);
  // Ensure ends with period
  if (!/[.!?]$/.test(stripped)) stripped += ".";
  return stripped;
}

function stripChinesePrefix(point) {
  // "在[setting]，[theme]体现在：[content]（[time]）。"
  // or "在[setting]，[theme]体现在[content]（[time]）。"
  // The setting can contain Chinese punctuation, so anchor on "体现在".
  let stripped = point.replace(/^.*?体现在[：:]?\s*/, "");
  // Remove trailing parenthetical time reference (Chinese brackets)
  stripped = stripped.replace(/\s*[（(][^）)]*[）)]\s*[。.]?\s*$/, "");
  stripped = stripped.trim();
  if (!stripped || stripped.length < 5) return point; // fallback
  // Ensure ends with 。
  if (!/[。！？.!?]$/.test(stripped)) stripped += "。";
  return stripped;
}

// ---------- Merging logic ----------

function computeMergeGroups(apps) {
  if (apps.length <= 1) return apps.map((_, i) => [i]);

  // Pre-compute stripped points for similarity
  const stripped = apps.map((a) => stripEnglishPrefix(a.point));

  // Greedy clustering
  const assigned = new Set();
  const groups = [];

  for (let i = 0; i < apps.length; i++) {
    if (assigned.has(i)) continue;
    const group = [i];
    assigned.add(i);

    for (let j = i + 1; j < apps.length; j++) {
      if (assigned.has(j)) continue;
      // Check if j is similar to ANY member of the current group
      const isSimilar = group.some((k) => {
        const textSim = similarity(stripped[k], stripped[j]);
        const evSim = evidenceOverlap(apps[k].evidence, apps[j].evidence);
        // Boost similarity if settings match
        const sameSettingBoost =
          apps[k].setting &&
          apps[j].setting &&
          apps[k].setting.toLowerCase() === apps[j].setting.toLowerCase()
            ? 0.10
            : 0;
        return (textSim + sameSettingBoost) >= SIM_THRESHOLD || evSim >= 0.5;
      });
      if (isSimilar) {
        group.push(j);
        assigned.add(j);
      }
    }

    groups.push(group);
  }

  return groups;
}

function mergeAppGroup(apps, stripFn) {
  // Collect all chapter numbers
  const allChapters = [];
  for (const a of apps) {
    if (Number.isInteger(a.chapter)) allChapters.push(a.chapter);
    if (Array.isArray(a.chapters)) allChapters.push(...a.chapters);
  }
  const chapters = [...new Set(allChapters)].sort((a, b) => a - b);

  // Pick the "best" application for the point (most evidence, then longest point)
  const sorted = [...apps].sort(
    (a, b) =>
      (b.evidence?.length || 0) - (a.evidence?.length || 0) ||
      b.point.length - a.point.length
  );
  const point = stripFn(sorted[0].point);

  // Combine evidence (deduplicated, preserving order)
  const seen = new Set();
  const evidence = [];
  for (const a of apps) {
    for (const e of a.evidence || []) {
      const key = e.trim().toLowerCase();
      if (!seen.has(key)) {
        seen.add(key);
        evidence.push(e);
      }
    }
  }

  // Combine settings
  const settings = [...new Set(apps.map((a) => a.setting).filter(Boolean))];
  const setting = settings.join("; ");

  // Combine time ranges
  const times = [...new Set(apps.map((a) => a.time).filter(Boolean))];
  const time = times.join("; ");

  return { chapters, setting, time, point, evidence };
}

// ---------- Main ----------

console.log("Reading data files...");
const enData = parseBookData(join(ROOT, "book-data.js"));
const zhData = parseBookData(join(ROOT, "book-data.zh.js"));

console.log(
  `Found ${enData.themes.length} EN themes, ${zhData.themes.length} ZH themes.`
);

// Verify parity: same theme IDs in same order
for (let i = 0; i < enData.themes.length; i++) {
  const enId = enData.themes[i].id;
  const zhId = zhData.themes[i]?.id;
  if (enId !== zhId) {
    console.error(`Theme parity mismatch at index ${i}: EN=${enId}, ZH=${zhId}`);
    process.exit(1);
  }
  const enAppCount = (enData.themes[i].applications || []).length;
  const zhAppCount = (zhData.themes[i]?.applications || []).length;
  if (enAppCount !== zhAppCount) {
    console.error(
      `Application count mismatch for theme "${enId}": EN=${enAppCount}, ZH=${zhAppCount}`
    );
    process.exit(1);
  }
}

let totalBefore = 0;
let totalAfter = 0;

// Determine merge groups from EN data, apply to both
for (let i = 0; i < enData.themes.length; i++) {
  const enTheme = enData.themes[i];
  const zhTheme = zhData.themes[i];
  const enApps = enTheme.applications || [];
  const zhApps = zhTheme.applications || [];

  const groups = computeMergeGroups(enApps);

  totalBefore += enApps.length;
  totalAfter += groups.length;

  // Apply merge groups to EN
  enTheme.applications = groups.map((group) => {
    const apps = group.map((idx) => enApps[idx]);
    return mergeAppGroup(apps, stripEnglishPrefix);
  });

  // Apply same groups to ZH
  zhTheme.applications = groups.map((group) => {
    const apps = group.map((idx) => zhApps[idx]);
    return mergeAppGroup(apps, stripChinesePrefix);
  });

  if (enApps.length !== groups.length) {
    console.log(
      `  ${enTheme.id}: ${enApps.length} → ${groups.length} applications`
    );
  }
}

console.log(`\nTotal: ${totalBefore} → ${totalAfter} applications`);

// Write back
console.log("\nWriting book-data.js...");
writeBookData(join(ROOT, "book-data.js"), enData);
console.log("Writing book-data.zh.js...");
writeBookData(join(ROOT, "book-data.zh.js"), zhData);
console.log("Done!");
