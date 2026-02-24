let BOOK_DATA_BY_LANG;

const UI_TEXT = {
  en: {
    documentTitleSuffix: "Argument Atlas",
    mindmapHeading: "Chapter Argument Mindmap",
    mindmapIntro:
      "Expand a chapter to reveal its main argument and the evidence that supports it. Use the keywords to spotlight themes across the book.",
    expandAll: "Expand all",
    collapseAll: "Collapse all",
    clearHighlights: "Clear highlights",
    keywordsHeading: "Keywords",
    keywordsIntro:
      "Click a keyword to highlight where it appears in both the chapter map and the book flow.",
    synthesisHeading: "Book Synthesis Flow",
    chapterMapRootLabel: "Chapter Argument Map",
    thesisHeading: "Thesis",
    argumentFlowHeading: "Argument Flow",
    mainArgumentHeading: "Main Argument",
    evidenceHeading: "Evidence",
    noSummary: "No summary yet.",
    pagesLabel: "Pages",
    showDetails: "Show details",
    hideDetails: "Hide details",
    showKeywords: "Show keywords",
    hideKeywords: "Hide keywords",
    selectKeywordHint: "Select a keyword to see its definition and applications.",
    noApplications: "No applications listed yet.",
    applicationsHeading: "Applications",
    applicationLabel: "Application",
    chaptersLabel: "Chapters",
    mechanismLabel: "Mechanism",
    periodLabel: "Period",
    chapterChipPrefix: "Ch"
  },
  zh: {
    documentTitleSuffix: "论证图谱",
    mindmapHeading: "章节论证思维导图",
    mindmapIntro:
      "展开章节可查看其核心论点及支撑证据。点击关键词可聚焦全书中的跨章节主题。",
    expandAll: "展开全部",
    collapseAll: "收起全部",
    clearHighlights: "清除高亮",
    keywordsHeading: "关键词",
    keywordsIntro: "点击关键词，可在章节图谱与全书综合流程中高亮其出现位置。",
    synthesisHeading: "全书综合流程",
    chapterMapRootLabel: "章节论证图",
    thesisHeading: "论题",
    argumentFlowHeading: "论证流程",
    mainArgumentHeading: "核心论点",
    evidenceHeading: "证据",
    noSummary: "暂无摘要。",
    pagesLabel: "页码",
    showDetails: "显示详情",
    hideDetails: "隐藏详情",
    showKeywords: "显示关键词",
    hideKeywords: "隐藏关键词",
    selectKeywordHint: "请选择一个关键词以查看其定义与应用。",
    noApplications: "暂无应用条目。",
    applicationsHeading: "应用",
    applicationLabel: "应用",
    chaptersLabel: "章节",
    mechanismLabel: "机制",
    periodLabel: "时期",
    chapterChipPrefix: "第"
  }
};

const KEYWORD_GROUPS = [
  { id: "mechanisms", labels: { en: "Mechanisms", zh: "机制" } },
  {
    id: "institutions-actors",
    labels: { en: "Institutions & Actors", zh: "制度与行动者" }
  },
  { id: "places-regions", labels: { en: "Places & Regions", zh: "地点与区域" } }
];

function loadLanguagePreference() {
  try {
    const stored = localStorage.getItem("atlas-language");
    if (stored === "en" || stored === "zh") {
      return stored;
    }
  } catch {
    // Ignore storage errors.
  }
  return "en";
}

function saveLanguagePreference(language) {
  try {
    localStorage.setItem("atlas-language", language);
  } catch {
    // Ignore storage errors.
  }
}

const state = {
  language: loadLanguagePreference(),
  activeKeyword: null,
  activeFlow: null
};

let chapterKeywordIndex = new Map();
let controlsBound = false;
let languageBound = false;

const chapterElements = new Map();
const flowElements = new Map();
const threadGrid = document.getElementById("threadGrid");

function getBookData() {
  return BOOK_DATA_BY_LANG[state.language];
}

function getUI() {
  return UI_TEXT[state.language];
}

function getGroupLabel(group) {
  return group.labels[state.language] || group.labels.en;
}

function normalizeText(value) {
  return String(value || "").replace(/\s+/g, " ").trim();
}

function ensureSentence(value) {
  const text = normalizeText(value);
  if (!text) {
    return "";
  }
  return /[.!?。！？]$/.test(text) ? text : `${text}.`;
}

function compactApplicationPoint(point) {
  const source = normalizeText(point);
  if (!source) {
    return "";
  }

  const markers = state.language === "zh"
    ? [/\bis visible as\b/i, /体现在[:：]/]
    : [/\bis visible as\b/i];
  const markerMatch = markers
    .map((marker) => marker.exec(source))
    .find((match) => Boolean(match));
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

  if (state.language === "zh") {
    if (items.length === 2) {
      return `${items[0]}和${items[1]}`;
    }
    return `${items.slice(0, -1).join("、")}以及${items[items.length - 1]}`;
  }

  if (items.length === 2) {
    return `${items[0]} and ${items[1]}`;
  }
  return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`;
}

function buildKeywordCitation(keywordId, index) {
  return `<sup><a href="#keyword-${keywordId}-application-${index + 1}">${index + 1}</a></sup>`;
}

function buildDefinitionApplicationClause(keywordId, application, index) {
  const compactPoint = compactApplicationPoint(application.point).replace(/[.!?。！？]$/, "");
  const context = normalizeText(application.setting);
  const citation = buildKeywordCitation(keywordId, index);

  if (compactPoint && context) {
    if (state.language === "zh") {
      return `${compactPoint}（${context}）${citation}`;
    }
    return `${compactPoint} (${context})${citation}`;
  }
  if (compactPoint) {
    return `${compactPoint}${citation}`;
  }
  if (context) {
    return `${context}${citation}`;
  }
  return state.language === "zh"
    ? `已记录的应用${citation}`
    : `documented application${citation}`;
}

function buildKeywordDefinition(keyword, applications) {
  const baseDefinition = String(keyword.definition || "").trim();
  if (!baseDefinition) {
    return "";
  }

  const hasEmbeddedLinks = /href=["']#keyword-[^"']+-application-\d+["']/.test(baseDefinition);
  if (hasEmbeddedLinks || !applications.length) {
    return baseDefinition;
  }

  const clauses = applications
    .map((application, index) =>
      buildDefinitionApplicationClause(keyword.id, application, index)
    )
    .filter(Boolean);

  if (!clauses.length) {
    return baseDefinition;
  }

  const chunkSize = 3;
  const supportSentences = [];
  for (let i = 0; i < clauses.length; i += chunkSize) {
    const chunk = clauses.slice(i, i + chunkSize);
    if (state.language === "zh") {
      const intro = i === 0 ? "其可见于" : "其还可见于";
      supportSentences.push(`${intro}${joinWithAnd(chunk)}。`);
    } else {
      const intro = i === 0 ? "It appears in" : "It also appears in";
      supportSentences.push(`${intro} ${joinWithAnd(chunk)}.`);
    }
  }

  const punctuatedBase = /[.!?。！？](\s*<\/[^>]+>\s*)*$/.test(baseDefinition)
    ? baseDefinition
    : `${baseDefinition}${state.language === "zh" ? "。" : "."}`;

  return `${punctuatedBase} ${supportSentences.join(" ")}`.trim();
}

function bindSectionToggles(container) {
  if (!container) {
    return;
  }

  const ui = getUI();
  container.querySelectorAll(".section-toggle").forEach((toggle) => {
    const section = toggle.closest(".flow-section");
    if (section) {
      toggle.textContent = section.classList.contains("is-collapsed")
        ? ui.showDetails
        : ui.hideDetails;
    }

    toggle.addEventListener("click", () => {
      const sectionNode = toggle.closest(".flow-section");
      if (!sectionNode) {
        return;
      }
      const collapsed = sectionNode.classList.toggle("is-collapsed");
      toggle.textContent = collapsed ? ui.showDetails : ui.hideDetails;
    });
  });
}

function buildChapterKeywordIndex(bookData) {
  const index = new Map();
  bookData.keywords.forEach((keyword) => {
    const applications = Array.isArray(keyword.applications)
      ? keyword.applications
      : [];
    applications.forEach((application) => {
      const chapters = Array.isArray(application.chapters)
        ? application.chapters
        : [];
      chapters.forEach((chapterId) => {
        if (!Number.isInteger(chapterId)) {
          return;
        }
        if (!index.has(chapterId)) {
          index.set(chapterId, new Set());
        }
        index.get(chapterId).add(keyword.id);
      });
    });
  });
  return index;
}

function chapterChipText(chapterId) {
  const ui = getUI();
  if (state.language === "zh") {
    return `${ui.chapterChipPrefix}${chapterId}章`;
  }
  return `${ui.chapterChipPrefix} ${chapterId}`;
}

function formatChapterLabel(chapter) {
  if (state.language === "zh") {
    return `第${chapter.id}章：${chapter.title}`;
  }
  return `Ch ${chapter.id}: ${chapter.title}`;
}

function combineSectionTitle(section) {
  if (!section.note) {
    return section.title;
  }
  return state.language === "zh"
    ? `${section.title}：${section.note}`
    : `${section.title} - ${section.note}`;
}

function renderChapters() {
  const bookData = getBookData();
  const ui = getUI();
  const container = document.getElementById("chapterMindmap");
  container.innerHTML = "";
  chapterElements.clear();

  const root = document.createElement("details");
  root.className = "node root";
  root.open = true;

  const summary = document.createElement("summary");
  summary.textContent = `${bookData.title}: ${ui.chapterMapRootLabel}`;
  root.appendChild(summary);

  const branch = document.createElement("div");
  branch.className = "branch";

  bookData.chapters.forEach((chapter) => {
    const node = document.createElement("details");
    node.className = "node chapter";
    node.dataset.id = chapter.id;
    const chapterKeywords = chapterKeywordIndex.get(chapter.id) || new Set();
    node.dataset.keywords = Array.from(chapterKeywords).join(" ");

    const nodeSummary = document.createElement("summary");
    nodeSummary.innerHTML = `<span class="chip">${chapterChipText(chapter.id)}</span><span>${chapter.title}</span>`;

    const body = document.createElement("div");
    body.className = "node-body";

    if (chapter.flowSections && chapter.flowSections.length) {
      body.innerHTML = `
        ${chapter.thesis ? `<h4>${ui.thesisHeading}</h4><p>${chapter.thesis}</p>` : ""}
        <h4>${ui.argumentFlowHeading}</h4>
        <div class="flow-sections">
          ${chapter.flowSections
          .map(
            (section, sectionIndex) => `
            <div class="flow-section is-collapsed" id="chapter-${chapter.id}-section-${sectionIndex + 1}">
              <div class="flow-section-header">
                <div class="flow-section-title">${combineSectionTitle(section)}</div>
                <button class="section-toggle" type="button">${ui.showDetails}</button>
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
        <p class="muted">${ui.pagesLabel}: ${chapter.pages}</p>
      `;
    } else if (chapter.flow && chapter.flow.length) {
      body.innerHTML = `
        ${chapter.thesis ? `<h4>${ui.thesisHeading}</h4><p>${chapter.thesis}</p>` : ""}
        <h4>${ui.argumentFlowHeading}</h4>
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
        <p class="muted">${ui.pagesLabel}: ${chapter.pages}</p>
      `;
    } else {
      const hasArgument = Boolean(chapter.argument);
      const evidenceItems = Array.isArray(chapter.evidence) ? chapter.evidence : [];
      const hasEvidence = evidenceItems.length > 0;
      const argumentBlock = hasArgument
        ? `<h4>${ui.mainArgumentHeading}</h4><p>${chapter.argument}</p>`
        : `<p class="muted">${ui.noSummary}</p>`;
      const evidenceBlock = hasEvidence
        ? `<h4>${ui.evidenceHeading}</h4><ul>${evidenceItems.map((item) => `<li>${item}</li>`).join("")}</ul>`
        : "";

      body.innerHTML = `
        ${argumentBlock}
        ${evidenceBlock}
        <p class="muted">${ui.pagesLabel}: ${chapter.pages}</p>
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
      toggle.textContent = getUI().hideDetails;
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
    /^keyword-[a-z0-9-]+-application-\d+$/.test(sectionId)
  ) {
    expandSectionById(sectionId);
  }
});

function renderThreads() {
  const bookData = getBookData();
  const ui = getUI();
  threadGrid.innerHTML = "";
  const groupedKeywords = new Map(
    KEYWORD_GROUPS.map((group) => [group.id, []])
  );

  bookData.keywords.forEach((keyword) => {
    if (!groupedKeywords.has(keyword.group)) {
      groupedKeywords.set(keyword.group, []);
    }
    groupedKeywords.get(keyword.group).push(keyword);
  });

  KEYWORD_GROUPS.forEach((group) => {
    const keywords = groupedKeywords.get(group.id) || [];
    if (!keywords.length) {
      return;
    }

    const section = document.createElement("section");
    section.className = "thread-group";
    section.dataset.group = group.id;

    const heading = document.createElement("button");
    heading.type = "button";
    heading.className = "thread-group-toggle";
    heading.innerHTML = `
      <span class="thread-group-title">${getGroupLabel(group)}</span>
      <span class="thread-group-toggle-meta">${ui.showKeywords}</span>
    `;
    heading.addEventListener("click", () => {
      const collapsed = section.classList.contains("is-collapsed");
      setThreadGroupCollapsed(section, !collapsed);
    });
    section.appendChild(heading);

    const list = document.createElement("div");
    list.className = "thread-group-list";

    keywords.forEach((keyword) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "thread";
      button.dataset.keyword = keyword.id;
      button.innerHTML = `
        <div class="label">${keyword.label}</div>
        <div class="desc">${keyword.description}</div>
      `;
      button.addEventListener("click", () => toggleKeyword(keyword.id));
      list.appendChild(button);
    });

    section.appendChild(list);
    threadGrid.appendChild(section);
  });

  collapseAllThreadGroups();
  updateThreadGroupVisibility();
}

function renderFlow() {
  const bookData = getBookData();
  const flow = document.getElementById("bookFlow");
  flow.innerHTML = "";
  flowElements.clear();

  bookData.flow.forEach((step, index) => {
    const item = document.createElement("div");
    item.className = "flow-item";

    const node = document.createElement("button");
    node.type = "button";
    node.className = "flow-node";
    node.dataset.id = step.id;
    node.dataset.chapters = step.chapters.join(",");
    const baseKeywords = Array.isArray(step.keywords) ? step.keywords : [];
    const flowKeywords = new Set(baseKeywords);
    step.chapters.forEach((chapterId) => {
      const extraKeywords = chapterKeywordIndex.get(chapterId);
      if (extraKeywords) {
        extraKeywords.forEach((keywordId) => flowKeywords.add(keywordId));
      }
    });
    node.dataset.keywords = Array.from(flowKeywords).join(" ");
    node.innerHTML = `
      <div>${step.title}</div>
      <div class="muted" style="font-size:12px; margin-top:6px;">${step.mechanism}</div>
      <div class="flow-period">${step.period}</div>
    `;
    node.addEventListener("click", () => setActiveFlow(step.id));

    item.appendChild(node);

    if (index < bookData.flow.length - 1) {
      const arrow = document.createElement("div");
      arrow.className = "flow-arrow";
      item.appendChild(arrow);
    }

    flow.appendChild(item);
    flowElements.set(step.id, node);
  });
}

function updateFlowDetail(step) {
  const ui = getUI();
  const bookData = getBookData();
  const detail = document.getElementById("flowDetail");
  const chapterLabels = step.chapters
    .map((id) => {
      const chapter = bookData.chapters.find((c) => c.id === id);
      return chapter ? formatChapterLabel(chapter) : "";
    })
    .filter(Boolean)
    .join(state.language === "zh" ? "，" : ", ");

  detail.innerHTML = `
    <h3>${step.title}</h3>
    <p>${step.summary}</p>
    <p class="muted"><strong>${ui.chaptersLabel}:</strong> ${chapterLabels}</p>
    <p class="muted"><strong>${ui.mechanismLabel}:</strong> ${step.mechanism}</p>
    <p class="muted"><strong>${ui.periodLabel}:</strong> ${step.period}</p>
  `;
}

function updateKeywordDetail(keyword) {
  const ui = getUI();
  const detail = document.getElementById("keywordDetail");
  if (!detail) {
    return;
  }
  if (!keyword) {
    detail.classList.remove("is-visible");
    detail.innerHTML = `
      <p class="muted">${ui.selectKeywordHint}</p>
    `;
    return;
  }

  const applications = Array.isArray(keyword.applications) ? keyword.applications : [];
  const definition = buildKeywordDefinition(keyword, applications);

  const applicationBlocks = applications.length
    ? applications
      .map((application, index) => {
        const appId = `keyword-${keyword.id}-application-${index + 1}`;
        const chapters = Array.isArray(application.chapters)
          ? application.chapters
          : [];
        const chapterLabel = chapters.length
          ? state.language === "zh"
            ? chapters.map((c) => `第${c}章`).join("、")
            : chapters.length === 1
              ? `Chapter ${chapters[0]}`
              : `Chapters ${chapters.join(", ")}`
          : ui.applicationLabel;
        const context = normalizeText(application.setting);
        const evidenceItems = Array.isArray(application.evidence) && application.evidence.length
          ? application.evidence.map((e) => `<li>${e}</li>`).join("")
          : "";
        const point = compactApplicationPoint(application.point);
        return `
            <div class="flow-section is-collapsed" id="${appId}">
              <div class="flow-section-header">
                <div class="flow-section-title">${chapterLabel}</div>
                <button class="section-toggle" type="button">${ui.showDetails}</button>
              </div>
              ${context ? `<div class="flow-section-note">${context}</div>` : ""}
              <ol class="flow-list">
                <li>
                  <div class="flow-point">${point}</div>
                  ${evidenceItems ? `<ul class="evidence-list">${evidenceItems}</ul>` : ""}
                </li>
              </ol>
            </div>
          `;
      })
      .join("")
    : `<p class="muted">${ui.noApplications}</p>`;

  detail.classList.add("is-visible");
  detail.innerHTML = `
    <div class="node-body">
      <p class="keyword-definition">${definition}</p>
      <h4>${ui.applicationsHeading}</h4>
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
    node.classList.toggle("active", node.dataset.id === String(flowId));
  });

  const step = getBookData().flow.find((item) => item.id === flowId);
  if (step) {
    updateFlowDetail(step);
  }

  updateHighlights();
}

function syncActiveKeywordButtons() {
  document.querySelectorAll(".thread").forEach((thread) => {
    thread.classList.toggle("active", thread.dataset.keyword === state.activeKeyword);
  });

  threadGrid.classList.toggle("has-active-keyword", Boolean(state.activeKeyword));
  updateThreadGroupVisibility();

  const keyword = state.activeKeyword
    ? getBookData().keywords.find((item) => item.id === state.activeKeyword)
    : null;

  if (!keyword && state.activeKeyword) {
    state.activeKeyword = null;
  }

  updateKeywordDetail(keyword || null);
}

function toggleKeyword(keywordId) {
  state.activeKeyword = state.activeKeyword === keywordId ? null : keywordId;
  syncActiveKeywordButtons();
  updateHighlights();
}

function updateHighlights() {
  const bookData = getBookData();
  const hasKeyword = Boolean(state.activeKeyword);
  const flowStep = state.activeFlow
    ? bookData.flow.find((item) => item.id === state.activeFlow)
    : null;
  const flowChapters = flowStep ? new Set(flowStep.chapters) : null;

  chapterElements.forEach((node, id) => {
    const keywords = node.dataset.keywords.split(" ").filter(Boolean);
    const matchesKeyword = !hasKeyword || keywords.includes(state.activeKeyword);
    const matchesFlow = !flowChapters || flowChapters.has(id);
    const highlight = (hasKeyword || flowChapters) && matchesKeyword && matchesFlow;

    node.classList.toggle("is-highlighted", highlight);
    node.classList.toggle("is-dimmed", (hasKeyword || flowChapters) && !highlight);
  });

  flowElements.forEach((node) => {
    const keywords = node.dataset.keywords.split(" ").filter(Boolean);
    const matchesKeyword = !hasKeyword || keywords.includes(state.activeKeyword);
    node.classList.toggle("is-dimmed", hasKeyword && !matchesKeyword);
  });
}

function updateThreadGroupVisibility() {
  const hasActiveKeyword = Boolean(state.activeKeyword);
  document.querySelectorAll(".thread-group").forEach((group) => {
    if (!hasActiveKeyword) {
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
    toggleMeta.textContent = collapsed ? getUI().showKeywords : getUI().hideKeywords;
  }
}

function collapseAllThreadGroups() {
  document.querySelectorAll(".thread-group").forEach((group) => {
    setThreadGroupCollapsed(group, true);
  });
}

function updateLanguageSwitchButtons() {
  const enBtn = document.getElementById("langEn");
  const zhBtn = document.getElementById("langZh");
  if (!enBtn || !zhBtn) {
    return;
  }

  const isEn = state.language === "en";
  enBtn.classList.toggle("is-active", isEn);
  enBtn.setAttribute("aria-pressed", String(isEn));
  zhBtn.classList.toggle("is-active", !isEn);
  zhBtn.setAttribute("aria-pressed", String(!isEn));
}

function updateToggleAllLabel() {
  const toggleAllBtn = document.getElementById("toggleAll");
  if (!toggleAllBtn) {
    return;
  }
  const chapterNodes = document.querySelectorAll(".node.chapter");
  const allExpanded = chapterNodes.length > 0 && Array.from(chapterNodes).every((node) => node.open);
  toggleAllBtn.textContent = allExpanded ? getUI().collapseAll : getUI().expandAll;
}

function updateStaticChrome() {
  const ui = getUI();
  const bookData = getBookData();

  document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
  document.title = `${bookData.title} - ${ui.documentTitleSuffix}`;

  const bookTitle = document.getElementById("bookTitle");
  const mindmapHeading = document.getElementById("mindmapHeading");
  const mindmapIntro = document.getElementById("mindmapIntro");
  const keywordsHeading = document.getElementById("keywordsHeading");
  const keywordsIntro = document.getElementById("keywordsIntro");
  const synthesisHeading = document.getElementById("synthesisHeading");
  const coreArgument = document.getElementById("coreArgument");
  const clearFilters = document.getElementById("clearFilters");

  if (bookTitle) {
    bookTitle.textContent = bookData.title;
  }
  if (mindmapHeading) {
    mindmapHeading.textContent = ui.mindmapHeading;
  }
  if (mindmapIntro) {
    mindmapIntro.textContent = ui.mindmapIntro;
  }
  if (keywordsHeading) {
    keywordsHeading.textContent = ui.keywordsHeading;
  }
  if (keywordsIntro) {
    keywordsIntro.textContent = ui.keywordsIntro;
  }
  if (synthesisHeading) {
    synthesisHeading.textContent = ui.synthesisHeading;
  }
  if (coreArgument) {
    coreArgument.textContent = bookData.coreArgument;
  }
  if (clearFilters) {
    clearFilters.textContent = ui.clearHighlights;
  }

  updateLanguageSwitchButtons();
  updateToggleAllLabel();
}

function bindControls() {
  if (controlsBound) {
    return;
  }

  const toggleAllBtn = document.getElementById("toggleAll");
  const clearBtn = document.getElementById("clearFilters");

  toggleAllBtn.addEventListener("click", () => {
    const chapterNodes = document.querySelectorAll(".node.chapter");
    const allExpanded = Array.from(chapterNodes).every((node) => node.open);

    chapterNodes.forEach((node) => {
      node.open = !allExpanded;
    });

    updateToggleAllLabel();
  });

  clearBtn.addEventListener("click", () => {
    state.activeKeyword = null;
    state.activeFlow = null;

    document.querySelectorAll(".thread").forEach((thread) => {
      thread.classList.remove("active");
    });

    threadGrid.classList.remove("has-active-keyword");
    collapseAllThreadGroups();
    updateThreadGroupVisibility();
    updateKeywordDetail(null);

    flowElements.forEach((node) => {
      node.classList.remove("active", "is-dimmed");
    });

    updateHighlights();
  });

  controlsBound = true;
}

function setLanguage(language) {
  if (language !== "en" && language !== "zh") {
    return;
  }
  if (state.language === language) {
    return;
  }

  state.language = language;
  saveLanguagePreference(language);
  renderAll();
}

function bindLanguageSwitch() {
  if (languageBound) {
    return;
  }

  const enBtn = document.getElementById("langEn");
  const zhBtn = document.getElementById("langZh");

  if (enBtn) {
    enBtn.addEventListener("click", () => setLanguage("en"));
  }
  if (zhBtn) {
    zhBtn.addEventListener("click", () => setLanguage("zh"));
  }

  languageBound = true;
}

function renderAll() {
  const bookData = getBookData();
  chapterKeywordIndex = buildChapterKeywordIndex(bookData);

  renderChapters();
  renderThreads();
  renderFlow();
  updateStaticChrome();

  const flowIds = new Set(bookData.flow.map((step) => step.id));
  if (!flowIds.has(state.activeFlow)) {
    state.activeFlow = bookData.flow[0] ? bookData.flow[0].id : null;
  }

  if (state.activeFlow !== null) {
    setActiveFlow(state.activeFlow);
  }

  const keywordIds = new Set(bookData.keywords.map((keyword) => keyword.id));
  if (!keywordIds.has(state.activeKeyword)) {
    state.activeKeyword = null;
  }

  syncActiveKeywordButtons();
  updateHighlights();
  updateToggleAllLabel();
}

function init() {
  bindControls();
  bindLanguageSwitch();
  renderAll();
}

export function initBook(data) {
  BOOK_DATA_BY_LANG = data;
  init();
}
