import chapter01 from "./chapters/chapter-01.js";
import chapter02 from "./chapters/chapter-02.js";
import chapter03 from "./chapters/chapter-03.js";
import chapter04 from "./chapters/chapter-04.js";
import chapter05 from "./chapters/chapter-05.js";
import chapter06 from "./chapters/chapter-06.js";
import chapter07 from "./chapters/chapter-07.js";
import chapter08 from "./chapters/chapter-08.js";
import chapter09 from "./chapters/chapter-09.js";
import chapter10 from "./chapters/chapter-10.js";
import chapter11 from "./chapters/chapter-11.js";
import chapter12 from "./chapters/chapter-12.js";
import chapter13 from "./chapters/chapter-13.js";
import chapter14 from "./chapters/chapter-14.js";
import bookData from "./book-data.js";

const BOOK_DATA = {
  title: bookData.title,
  coreArgument: bookData.coreArgument,
  themes: bookData.themes,
  chapters: [
    chapter01,
    chapter02,
    chapter03,
    chapter04,
    chapter05,
    chapter06,
    chapter07,
    chapter08,
    chapter09,
    chapter10,
    chapter11,
    chapter12,
    chapter13,
    chapter14
  ],
  flow: bookData.flow
};

const state = {
  activeTheme: null,
  activeFlow: null
};

const THEME_GROUPS = [
  { id: "mechanisms", label: "Mechanisms" },
  { id: "institutions-actors", label: "Institutions & Actors" },
  { id: "places-regions", label: "Places & Regions" }
];

const chapterElements = new Map();
const flowElements = new Map();
const threadGrid = document.getElementById("threadGrid");
const chapterThemeIndex = buildChapterThemeIndex();

function normalizeText(value) {
  return String(value || "").replace(/\s+/g, " ").trim();
}

function ensureSentence(value) {
  const text = normalizeText(value);
  if (!text) {
    return "";
  }
  return /[.!?]$/.test(text) ? text : `${text}.`;
}

function compactApplicationPoint(point) {
  const source = normalizeText(point);
  if (!source) {
    return "";
  }

  const marker = /\bis visible as\b/i;
  const markerMatch = marker.exec(source);
  let compact = markerMatch
    ? source.slice(markerMatch.index + markerMatch[0].length).trim()
    : source;

  compact = compact.replace(/\s*\([^)]*\)\.?$/, "").trim();
  compact = compact.replace(/^[,;:\-\s]+/, "").trim();
  return ensureSentence(compact || source);
}

function summarizeApplication(application) {
  const point = compactApplicationPoint(application.point);
  const evidence = Array.isArray(application.evidence) && application.evidence.length
    ? ensureSentence(application.evidence[0])
    : "";

  if (point && evidence && point.toLowerCase() === evidence.toLowerCase()) {
    return point;
  }

  return [point, evidence].filter(Boolean).join(" ");
}

function joinWithAnd(items) {
  if (!items.length) {
    return "";
  }
  if (items.length === 1) {
    return items[0];
  }
  if (items.length === 2) {
    return `${items[0]} and ${items[1]}`;
  }
  return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`;
}

function buildThemeCitation(themeId, index) {
  return `<sup><a href="#theme-${themeId}-application-${index + 1}">${index + 1}</a></sup>`;
}

function buildDefinitionApplicationClause(themeId, application, index) {
  const compactPoint = compactApplicationPoint(application.point).replace(/[.!?]$/, "");
  const context = [normalizeText(application.setting), normalizeText(application.time)]
    .filter(Boolean)
    .join(", ");
  const citation = buildThemeCitation(themeId, index);

  if (compactPoint && context) {
    return `${compactPoint} (${context})${citation}`;
  }
  if (compactPoint) {
    return `${compactPoint}${citation}`;
  }
  if (context) {
    return `${context}${citation}`;
  }
  return `documented application${citation}`;
}

function buildThemeDefinition(theme, applications) {
  const baseDefinition = String(theme.definition || "").trim();
  if (!baseDefinition) {
    return "";
  }

  const hasEmbeddedLinks = /href=["']#theme-[^"']+-application-\d+["']/.test(baseDefinition);
  if (hasEmbeddedLinks || !applications.length) {
    return baseDefinition;
  }

  const clauses = applications
    .map((application, index) =>
      buildDefinitionApplicationClause(theme.id, application, index)
    )
    .filter(Boolean);

  if (!clauses.length) {
    return baseDefinition;
  }

  const chunkSize = 3;
  const supportSentences = [];
  for (let i = 0; i < clauses.length; i += chunkSize) {
    const chunk = clauses.slice(i, i + chunkSize);
    const intro = i === 0 ? "It appears in" : "It also appears in";
    supportSentences.push(`${intro} ${joinWithAnd(chunk)}.`);
  }

  const punctuatedBase = /[.!?](\s*<\/[^>]+>\s*)*$/.test(baseDefinition)
    ? baseDefinition
    : `${baseDefinition}.`;

  return `${punctuatedBase} ${supportSentences.join(" ")}`.trim();
}

function bindSectionToggles(container) {
  if (!container) {
    return;
  }

  container.querySelectorAll(".section-toggle").forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const section = toggle.closest(".flow-section");
      if (!section) {
        return;
      }
      const collapsed = section.classList.toggle("is-collapsed");
      toggle.textContent = collapsed ? "Show details" : "Hide details";
    });
  });
}

function buildChapterThemeIndex() {
  const index = new Map();
  BOOK_DATA.themes.forEach((theme) => {
    const applications = Array.isArray(theme.applications)
      ? theme.applications
      : [];
    applications.forEach((application) => {
      const chapterId = application.chapter;
      if (!Number.isInteger(chapterId)) {
        return;
      }
      if (!index.has(chapterId)) {
        index.set(chapterId, new Set());
      }
      index.get(chapterId).add(theme.id);
    });
  });
  return index;
}

function renderChapters() {
  const container = document.getElementById("chapterMindmap");
  container.innerHTML = "";

  const root = document.createElement("details");
  root.className = "node root";
  root.open = true;

  const summary = document.createElement("summary");
  summary.textContent = `${BOOK_DATA.title}: Chapter Argument Map`;
  root.appendChild(summary);

  const branch = document.createElement("div");
  branch.className = "branch";

  BOOK_DATA.chapters.forEach((chapter) => {
    const node = document.createElement("details");
    node.className = "node chapter";
    node.dataset.id = chapter.id;
    const baseThemes = Array.isArray(chapter.themes) ? chapter.themes : [];
    const extraThemes = chapterThemeIndex.get(chapter.id) || new Set();
    const allThemes = new Set([...baseThemes, ...extraThemes]);
    node.dataset.themes = Array.from(allThemes).join(" ");

    const nodeSummary = document.createElement("summary");
    nodeSummary.innerHTML = `<span class="chip">Ch ${chapter.id}</span><span>${chapter.title}</span>`;

    const body = document.createElement("div");
    body.className = "node-body";

    if (chapter.flowSections && chapter.flowSections.length) {
      body.innerHTML = `
        ${chapter.thesis ? `<h4>Thesis</h4><p>${chapter.thesis}</p>` : ''}
        <h4>Argument Flow</h4>
        <div class="flow-sections">
          ${chapter.flowSections
            .map(
              (section, sectionIndex) => `
            <div class="flow-section is-collapsed" id="chapter-${chapter.id}-section-${sectionIndex + 1}">
              <div class="flow-section-header">
                <div class="flow-section-title">${section.note ? `${section.title} - ${section.note}` : section.title}</div>
                <button class="section-toggle" type="button">Show details</button>
              </div>
              <ol class="flow-list">
                ${section.steps
                  .map(
                    (step) => `
                  <li>
                    <div class="flow-point">${step.point}</div>
                    <ul class="evidence-list">
                      ${step.evidence.map((item) => `<li>${item}</li>`).join("")}
                    </ul>
                  </li>
                `
                  )
                  .join("")}
              </ol>
            </div>
          `
            )
            .join("")}
        </div>
        <p class="muted">Pages: ${chapter.pages}</p>
      `;
    } else if (chapter.flow && chapter.flow.length) {
      body.innerHTML = `
        ${chapter.thesis ? `<h4>Thesis</h4><p>${chapter.thesis}</p>` : ''}
        <h4>Argument Flow</h4>
        <ol class="flow-list">
          ${chapter.flow
            .map(
              (step) => `
            <li>
              <div class="flow-point">${step.point}</div>
              <ul class="evidence-list">
                ${step.evidence.map((item) => `<li>${item}</li>`).join("")}
              </ul>
            </li>
          `
            )
            .join("")}
        </ol>
        <p class="muted">Pages: ${chapter.pages}</p>
      `;
    } else {
      const hasArgument = Boolean(chapter.argument);
      const evidenceItems = Array.isArray(chapter.evidence) ? chapter.evidence : [];
      const hasEvidence = evidenceItems.length > 0;
      const argumentBlock = hasArgument
        ? `<h4>Main Argument</h4><p>${chapter.argument}</p>`
        : `<p class="muted">No summary yet.</p>`;
      const evidenceBlock = hasEvidence
        ? `<h4>Evidence</h4><ul>${evidenceItems.map((item) => `<li>${item}</li>`).join("")}</ul>`
        : "";

      body.innerHTML = `
        ${argumentBlock}
        ${evidenceBlock}
        <p class="muted">Pages: ${chapter.pages}</p>
      `;
    }

    node.appendChild(nodeSummary);
    node.appendChild(body);
    branch.appendChild(node);

    chapterElements.set(chapter.id, node);

    bindSectionToggles(body);
  });

  root.appendChild(branch);
  container.appendChild(root);
}

function expandSectionById(sectionId) {
  const section = document.getElementById(sectionId);
  if (!section) {
    return;
  }
  if (section.classList.contains("is-collapsed")) {
    section.classList.remove("is-collapsed");
    const toggle = section.querySelector(".section-toggle");
    if (toggle) {
      toggle.textContent = "Hide details";
    }
  }
}

document.addEventListener("click", (event) => {
  const link = event.target.closest("a[href^='#']");
  if (!link) {
    return;
  }
  const href = link.getAttribute("href");
  if (!href) {
    return;
  }
  const sectionId = href.slice(1);
  if (
    /^chapter-\d+-section-\d+$/.test(sectionId) ||
    /^theme-[a-z0-9-]+-application-\d+$/.test(sectionId)
  ) {
    expandSectionById(sectionId);
  }
});

function renderThreads() {
  threadGrid.innerHTML = "";
  const groupedThemes = new Map(
    THEME_GROUPS.map((group) => [group.id, []])
  );

  BOOK_DATA.themes.forEach((theme) => {
    if (!groupedThemes.has(theme.group)) {
      groupedThemes.set(theme.group, []);
    }
    groupedThemes.get(theme.group).push(theme);
  });

  THEME_GROUPS.forEach((group) => {
    const themes = groupedThemes.get(group.id) || [];
    if (!themes.length) {
      return;
    }

    const section = document.createElement("section");
    section.className = "thread-group";
    section.dataset.group = group.id;

    const heading = document.createElement("button");
    heading.type = "button";
    heading.className = "thread-group-toggle";
    heading.innerHTML = `
      <span class="thread-group-title">${group.label}</span>
      <span class="thread-group-toggle-meta">Show keywords</span>
    `;
    heading.addEventListener("click", () => {
      const collapsed = section.classList.contains("is-collapsed");
      setThreadGroupCollapsed(section, !collapsed);
    });
    section.appendChild(heading);

    const list = document.createElement("div");
    list.className = "thread-group-list";

    themes.forEach((theme) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "thread";
      button.dataset.theme = theme.id;
      button.innerHTML = `
        <div class="label">${theme.label}</div>
        <div class="desc">${theme.description}</div>
      `;
      button.addEventListener("click", () => toggleTheme(theme.id));
      list.appendChild(button);
    });

    section.appendChild(list);
    threadGrid.appendChild(section);
  });

  collapseAllThreadGroups();
  updateThreadGroupVisibility();
}

function renderFlow() {
  const flow = document.getElementById("bookFlow");
  flow.innerHTML = "";

  BOOK_DATA.flow.forEach((step, index) => {
    const item = document.createElement("div");
    item.className = "flow-item";

    const node = document.createElement("button");
    node.type = "button";
    node.className = "flow-node";
    node.dataset.id = step.id;
    node.dataset.chapters = step.chapters.join(",");
    const baseThemes = Array.isArray(step.themes) ? step.themes : [];
    const flowThemes = new Set(baseThemes);
    step.chapters.forEach((chapterId) => {
      const extraThemes = chapterThemeIndex.get(chapterId);
      if (extraThemes) {
        extraThemes.forEach((themeId) => flowThemes.add(themeId));
      }
    });
    node.dataset.themes = Array.from(flowThemes).join(" ");
    node.innerHTML = `
      <div>${step.title}</div>
      <div class="muted" style="font-size:12px; margin-top:6px;">${step.mechanism}</div>
      <div class="flow-period">${step.period}</div>
    `;
    node.addEventListener("click", () => setActiveFlow(step.id));

    item.appendChild(node);

    if (index < BOOK_DATA.flow.length - 1) {
      const arrow = document.createElement("div");
      arrow.className = "flow-arrow";
      item.appendChild(arrow);
    }

    flow.appendChild(item);
    flowElements.set(step.id, node);
  });
}

function updateFlowDetail(step) {
  const detail = document.getElementById("flowDetail");
  const chapterLabels = step.chapters
    .map((id) => {
      const chapter = BOOK_DATA.chapters.find((c) => c.id === id);
      return `Ch ${chapter.id}: ${chapter.title}`;
    })
    .join(", ");

  detail.innerHTML = `
    <h3>${step.title}</h3>
    <p>${step.summary}</p>
    <p class="muted"><strong>Chapters:</strong> ${chapterLabels}</p>
    <p class="muted"><strong>Mechanism:</strong> ${step.mechanism}</p>
    <p class="muted"><strong>Period:</strong> ${step.period}</p>
  `;
}

function updateThemeDetail(theme) {
  const detail = document.getElementById("themeDetail");
  if (!detail) {
    return;
  }
  if (!theme) {
    detail.classList.remove("is-visible");
    detail.innerHTML = `
      <p class="muted">Select a keyword to see its definition and applications.</p>
    `;
    return;
  }

  const applications = Array.isArray(theme.applications) ? theme.applications : [];
  const definition = buildThemeDefinition(theme, applications);

  const applicationBlocks = applications.length
    ? applications
        .map((application, index) => {
          const appId = `theme-${theme.id}-application-${index + 1}`;
          const chapterSup = Number.isInteger(application.chapter)
            ? `<sup>${application.chapter}</sup>`
            : "";
          const context = [normalizeText(application.setting), normalizeText(application.time)]
            .filter(Boolean)
            .join(" • ");
          const summary = summarizeApplication(application);
          return `
            <div class="flow-section is-collapsed" id="${appId}">
              <div class="flow-section-header">
                <div class="flow-section-title">Application${chapterSup}</div>
                <button class="section-toggle" type="button">Show details</button>
              </div>
              ${context ? `<div class="flow-section-note">${context}</div>` : ""}
              <ol class="flow-list">
                <li>
                  <div class="flow-point">${summary}</div>
                </li>
              </ol>
            </div>
          `;
        })
        .join("")
    : `<p class="muted">No applications listed yet.</p>`;

  detail.classList.add("is-visible");
  detail.innerHTML = `
    <div class="node-body">
      <p class="theme-definition">${definition}</p>
      <h4>Applications</h4>
      <div class="flow-sections">
        ${applicationBlocks}
      </div>
    </div>
  `;

  bindSectionToggles(detail);
}

function setActiveFlow(flowId) {
  state.activeFlow = flowId;

  flowElements.forEach((node) => {
    node.classList.toggle("active", node.dataset.id === flowId);
  });

  const step = BOOK_DATA.flow.find((item) => item.id === flowId);
  if (step) {
    updateFlowDetail(step);
  }

  updateHighlights();
}

function toggleTheme(themeId) {
  state.activeTheme = state.activeTheme === themeId ? null : themeId;

  document.querySelectorAll(".thread").forEach((thread) => {
    thread.classList.toggle("active", thread.dataset.theme === state.activeTheme);
  });

  threadGrid.classList.toggle("has-active-theme", Boolean(state.activeTheme));
  updateThreadGroupVisibility();

  const theme = state.activeTheme
    ? BOOK_DATA.themes.find((item) => item.id === state.activeTheme)
    : null;
  updateThemeDetail(theme);

  updateHighlights();
}

function updateHighlights() {
  const hasTheme = Boolean(state.activeTheme);
  const flowStep = state.activeFlow
    ? BOOK_DATA.flow.find((item) => item.id === state.activeFlow)
    : null;
  const flowChapters = flowStep ? new Set(flowStep.chapters) : null;

  chapterElements.forEach((node, id) => {
    const themes = node.dataset.themes.split(" ");
    const matchesTheme = !hasTheme || themes.includes(state.activeTheme);
    const matchesFlow = !flowChapters || flowChapters.has(id);
    const highlight = (hasTheme || flowChapters) && matchesTheme && matchesFlow;

    node.classList.toggle("is-highlighted", highlight);
    node.classList.toggle("is-dimmed", (hasTheme || flowChapters) && !highlight);
  });

  flowElements.forEach((node) => {
    const themes = node.dataset.themes.split(" ");
    const matchesTheme = !hasTheme || themes.includes(state.activeTheme);
    node.classList.toggle("is-dimmed", hasTheme && !matchesTheme);
  });
}

function updateThreadGroupVisibility() {
  const hasActiveTheme = Boolean(state.activeTheme);
  document.querySelectorAll(".thread-group").forEach((group) => {
    if (!hasActiveTheme) {
      group.classList.remove("is-hidden");
      return;
    }
    const activeThread = group.querySelector(".thread.active");
    group.classList.toggle("is-hidden", !activeThread);
    if (activeThread) {
      setThreadGroupCollapsed(group, false);
    }
  });
}

function setThreadGroupCollapsed(group, collapsed) {
  if (!group) {
    return;
  }
  group.classList.toggle("is-collapsed", collapsed);
  const toggleMeta = group.querySelector(".thread-group-toggle-meta");
  if (toggleMeta) {
    toggleMeta.textContent = collapsed ? "Show keywords" : "Hide keywords";
  }
}

function collapseAllThreadGroups() {
  document.querySelectorAll(".thread-group").forEach((group) => {
    setThreadGroupCollapsed(group, true);
  });
}

function bindControls() {
  const toggleAllBtn = document.getElementById("toggleAll");
  
  toggleAllBtn.addEventListener("click", () => {
    const chapterNodes = document.querySelectorAll(".node.chapter");
    const allExpanded = Array.from(chapterNodes).every((node) => node.open);
    
    chapterNodes.forEach((node) => {
      node.open = !allExpanded;
    });
    
    toggleAllBtn.textContent = allExpanded ? "Expand all" : "Collapse all";
  });

  document.getElementById("clearFilters").addEventListener("click", () => {
    state.activeTheme = null;
    state.activeFlow = null;

    document.querySelectorAll(".thread").forEach((thread) => {
      thread.classList.remove("active");
    });

    threadGrid.classList.remove("has-active-theme");
    collapseAllThreadGroups();
    updateThreadGroupVisibility();
    updateThemeDetail(null);

    flowElements.forEach((node) => {
      node.classList.remove("active", "is-dimmed");
    });

    updateHighlights();
  });
}

function init() {
  document.getElementById("coreArgument").textContent = BOOK_DATA.coreArgument;

  renderChapters();
  renderThreads();
  renderFlow();
  bindControls();
  updateThemeDetail(null);

  const firstStep = BOOK_DATA.flow[0];
  updateFlowDetail(firstStep);
  const firstNode = flowElements.get(firstStep.id);
  if (firstNode) {
    firstNode.classList.add("active");
  }
}

init();
