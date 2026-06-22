const countries = [
  {
    name: "UAE 阿联酋",
    rank: "第一优先级",
    cities: "Dubai / Abu Dhabi",
    reason: "公开资料显示 AITO 已进入 UAE，豪华车消费强，适合问界 M9、尊界 S800。",
    targets: "豪华车展厅、进口商、Jebel Ali 贸易商"
  },
  {
    name: "Saudi Arabia 沙特",
    rank: "第一优先级",
    cities: "Riyadh / Jeddah",
    reason: "购买力强，豪华 SUV 需求大，新能源正在起步，适合提前开发经销商。",
    targets: "高端车商、集团经销商、政府/企业采购"
  },
  {
    name: "Kazakhstan 哈萨克斯坦",
    rank: "第一优先级",
    cities: "Almaty / Astana",
    reason: "中亚进口车市场活跃，离中国近，适合问界 M8/M9 和高端 SUV。",
    targets: "汽车进口商、平行进口商、豪华车商"
  },
  {
    name: "Russia 俄罗斯",
    rank: "第一优先级",
    cities: "Moscow / St. Petersburg",
    reason: "中国车接受度高，高端 SUV 有机会，但需要注意付款、政策和合规风险。",
    targets: "大型经销商、豪华车进口商、平行进口商"
  },
  {
    name: "Qatar 卡塔尔",
    rank: "第二优先级",
    cities: "Doha",
    reason: "高端车购买力强，适合尊界 S800、问界 M9 等展示型车型。",
    targets: "豪车展厅、租赁公司、商务接待车队"
  },
  {
    name: "Kuwait 科威特",
    rank: "第二优先级",
    cities: "Kuwait City",
    reason: "豪华车文化明显，适合寻找高端展厅和多品牌进口商。",
    targets: "豪车经销商、汽车贸易公司"
  },
  {
    name: "Uzbekistan 乌兹别克斯坦",
    rank: "第二优先级",
    cities: "Tashkent",
    reason: "中亚增长市场，适合先找进口商和区域代理。",
    targets: "进口商、批发商、区域代理"
  },
  {
    name: "Azerbaijan 阿塞拜疆",
    rank: "第二优先级",
    cities: "Baku",
    reason: "高加索进口车需求存在，可作为中亚与东欧之间的机会市场。",
    targets: "汽车贸易公司、豪华车展厅"
  }
];

const salesStages = ["准备联系", "已联系", "有回复", "报价中", "谈判中", "已成交", "暂缓", "已流失"];

const destinationByCountry = {
  UAE: "Jebel Ali, UAE",
  "Saudi Arabia": "Dammam, Saudi Arabia",
  Kazakhstan: "Aktau, Kazakhstan",
  Russia: "Vladivostok, Russia",
  Qatar: "Doha, Qatar",
  Kuwait: "Kuwait City, Kuwait",
  Uzbekistan: "Poti, Georgia (transit to Uzbekistan)",
  Azerbaijan: "Alat Port, Azerbaijan"
};

const riskProfiles = {
  UAE: {
    certification: "向当地清关代理确认 GCC 规格、车型年份、排放及上牌资料是否满足当前要求，不要仅凭其他批次成功案例判断。",
    cockpit: "交车前逐项测试英文界面、导航、网络、远程 App、语音和智驾功能；无法在当地使用的功能要写进销售确认书。",
    logistics: "确认 Jebel Ali 到港费用、港口仓储免费期、保险责任和客户提车方式，报价中单列目的港外费用。",
    service: "确认当地维修合作方、诊断设备、常用易损件和质保责任边界，再承诺售后周期。"
  },
  "Saudi Arabia": {
    certification: "成交前让进口商核实 SABER、车辆合规和当地上牌文件要求，并确认中国版配置是否可以注册。",
    cockpit: "检查阿拉伯语/英语显示、地图联网和高温环境适配，不能使用的在线功能需提前披露。",
    logistics: "确认 Dammam 或 Jeddah 的实际到港方案、内陆运输和港杂费承担方。",
    service: "高温与沙尘环境下重点准备空调、滤芯、轮胎及电子系统售后方案。"
  },
  Kazakhstan: {
    certification: "让进口商或认证代理确认 EAEU/EAC 文件、车辆年份和上牌路径，避免先发车后补认证。",
    cockpit: "核对俄语/英语界面、地图与网络服务，并向客户说明中国区账号和远程功能限制。",
    logistics: "确认铁路或公路运输路线、边境换装、清关城市和最终交付地点。",
    service: "低温环境重点确认电池、热管理、冬季轮胎、备件和远程诊断支持。"
  },
  Russia: {
    certification: "在收款和发车前核查当前进口、认证、支付及制裁合规要求，保留书面确认和交易凭证。",
    cockpit: "核实俄语界面、通信模块、地图、账号和在线服务可用性，不承诺无法验证的智驾功能。",
    logistics: "根据客户城市确认海运、铁路或陆运路线，并单独评估支付、保险和转运风险。",
    service: "先确认诊断、软件升级、关键备件和质保执行主体，再进入批量订单。"
  },
  Qatar: {
    certification: "让当地进口商确认车辆合规、上牌和经销资质要求，豪华接待用车还需确认保险用途。",
    cockpit: "重点验证英语/阿拉伯语、空调、高温表现及本地网络服务。",
    logistics: "确认 Hamad/Doha 到港后的港杂、清关和本地交付费用，避免把本地税费误算进 CIF。",
    service: "提前确定豪华客户的上门服务、备件和故障响应方式。"
  },
  Kuwait: {
    certification: "由当地清关代理确认车型准入、上牌和海湾规格要求，书面核对 VIN、年份和配置。",
    cockpit: "检查高温环境、英文/阿拉伯语显示以及联网功能。",
    logistics: "确认 Kuwait City/Shuwaikh 港口费用、仓储和本地运输责任。",
    service: "明确质保范围、备件库存和当地维修合作方。"
  },
  Uzbekistan: {
    certification: "确认进口主体、认证、关税和上牌资料；内陆国运输必须先确认过境方案及责任划分。",
    cockpit: "核实俄语/英语界面、网络和地图服务，避免把中国区在线功能当作当地标准配置。",
    logistics: "Poti 等仅为参考中转点，实际路线应由货代按交付城市确认铁路、公路、过境和保险方案。",
    service: "优先确认当地维修资源、备件运输时效和低温使用需求。"
  },
  Azerbaijan: {
    certification: "让当地代理确认进口、认证和注册资料，核对车辆年份、排放和配置要求。",
    cockpit: "测试英语/俄语界面、地图、网络和远程功能的当地可用性。",
    logistics: "确认 Alat/Baku 到港、清关及最终交付费用和责任边界。",
    service: "明确当地维修点、备件、质保和远程技术支持流程。"
  }
};

const STORAGE_KEY = "huawei-ev-export-workbench-v3";
const SOCIAL_CAPTURE_SEEN_KEY = "huawei-ev-social-capture-seen-v1";

const savedState = loadSavedState();
let reviewLeads = savedState.reviewLeads;
let customers = savedState.customers;
let rejectedLeads = savedState.rejectedLeads;
let quoteHistory = savedState.quotes;
let lastQuote = null;
let cloudStateReady = false;
let cloudStateVersion = Number(savedState._cloudVersion || 0);
let localStateDirty = Boolean(savedState._cloudDirty);
let cloudHydrating = false;
let cloudSaveTimer = null;
let cloudSaveChain = Promise.resolve();
let discoveryJobs = [];
let discoveryJobsTimer = null;
let discoveryJobsExpanded = false;

const productProfiles = {
  "问界 M9": {
    english: "AITO M9",
    pitch: "a flagship luxury smart SUV with HarmonyOS cockpit, Huawei ADS intelligent driving features, premium space and long-range EREV/EV options",
    chinese: "旗舰豪华智慧 SUV，主打鸿蒙座舱、华为智驾、高端空间和长续航"
  },
  "尊界 S800": {
    english: "Maextro S800",
    pitch: "an ultra-luxury executive EV/EREV sedan for VIP reception, business travel and top-tier showrooms",
    chinese: "超豪华行政车型，适合老板用车、政商接待和高端展厅"
  },
  "享界 S9": {
    english: "Stelato S9",
    pitch: "a premium smart executive sedan with luxury comfort, intelligent cockpit and strong business-use appeal",
    chinese: "高端智慧行政轿车，适合商务客户和高端轿车市场"
  },
  "问界 M8": {
    english: "AITO M8",
    pitch: "a large smart SUV suitable for families and dealers looking for a more accessible premium model",
    chinese: "大型智慧 SUV，比 M9 更适合走量的中高端家庭市场"
  },
  "智界 R7": {
    english: "Luxeed R7",
    pitch: "a smart electric coupe SUV for younger premium EV buyers and technology-focused showrooms",
    chinese: "智能纯电轿跑 SUV，适合年轻高端新能源客户"
  }
};

const modelReferencePrices = {
  "问界 M9": 68000,
  "问界 M8": 56000,
  "尊界 S800": 128000,
  "享界 S9": 62000,
  "智界 R7": 48000
};

const defaultKeywords = [
  "UAE automotive importer vehicle distributor",
  "Dubai car dealer showroom auto trading",
  "UAE parallel import car dealer",
  "UAE vehicle procurement RFQ fleet purchase",
  "UAE new brand dealership opportunity",
  "UAE Chinese EV importer distributor"
];

function $(selector) {
  return document.querySelector(selector);
}

function $$(selector) {
  return Array.from(document.querySelectorAll(selector));
}

function money(value) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[char]);
}

function safeHttpUrl(value) {
  try {
    const url = new URL(String(value || ""));
    return ["http:", "https:"].includes(url.protocol) ? url.href : "";
  } catch {
    return "";
  }
}

function renderEmailEvidence(lead) {
  const records = (Array.isArray(lead.emailSources) ? lead.emailSources : [])
    .map((record) => ({
      ...record,
      sources: (record.sources || []).filter((source) => source.verified === true)
    }))
    .filter((record) => record.sources.length);
  if (!records.length) return `<span class="email-empty">公开页面未发现</span>`;
  return `<div class="email-evidence-list">${records.map((record) => {
    const sources = Array.isArray(record.sources) ? record.sources : [];
    return `
      <div class="email-evidence-item">
        <a class="email-address" href="mailto:${escapeHtml(record.email)}">${escapeHtml(record.email)}</a>
        <span class="verified-badge">已核验</span>
        <span class="email-source-links">
          ${sources.length ? sources.map((source, sourceIndex) => {
            const url = safeHttpUrl(source.url);
            return url
              ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" title="${escapeHtml(source.excerpt || `此页面公开显示邮箱 ${record.email}`)}">来源${sources.length > 1 ? sourceIndex + 1 : ""}：${escapeHtml(source.name || "公开页面")}</a>`
              : "";
          }).join("") : `<span>来源链接未记录</span>`}
        </span>
      </div>
    `;
  }).join("")}</div>`;
}

function renderValueEvidence(records, fallback, emptyText = "公开页面未发现") {
  const normalized = Array.isArray(records) && records.length
    ? records
    : fallback
      ? [{ value: fallback, sources: [] }]
      : [];
  if (!normalized.length) return `<span class="email-empty">${emptyText}</span>`;
  return `<div class="field-evidence-list">${normalized.map((record) => `
    <div class="field-evidence-item">
      <strong>${escapeHtml(record.value)}</strong>
      <span class="email-source-links">
        ${(record.sources || []).length ? record.sources.map((source, index) => {
          const url = safeHttpUrl(source.url);
          return url
            ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">来源${record.sources.length > 1 ? index + 1 : ""}：${escapeHtml(source.name || "公开页面")}</a>`
            : "";
        }).join("") : `<span>来源链接未记录</span>`}
      </span>
    </div>
  `).join("")}</div>`;
}

function mergeEmailSources(...groups) {
  const merged = [];
  groups.flat().filter(Boolean).forEach((record) => {
    if (!record?.email) return;
    const email = String(record.email).trim();
    let target = merged.find((item) => item.email.toLowerCase() === email.toLowerCase());
    if (!target) {
      target = { email, sources: [] };
      merged.push(target);
    }
    (record.sources || []).forEach((source) => {
      if (!source?.url) return;
      if (!target.sources.some((item) =>
        String(item.url).toLowerCase().replace(/\/$/, "") ===
        String(source.url).toLowerCase().replace(/\/$/, "")
      )) {
        target.sources.push(source);
      }
    });
  });
  return merged;
}

function downloadFile(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

function csvCell(value) {
  let text = String(value ?? "").replace(/\r?\n/g, " ").trim();
  if (/^[=+\-@]/.test(text)) text = `'${text}`;
  return `"${text.replace(/"/g, '""')}"`;
}

function exportCustomersCsv() {
  const button = $("#exportCustomerTable");
  if (!customers.length) {
    button.textContent = "客户池暂无数据";
    setTimeout(() => { button.textContent = "导出客户表格 CSV"; }, 1500);
    return;
  }
  const columns = [
    ["公司名称", (lead) => lead.company],
    ["国家", (lead) => lead.country],
    ["城市", (lead) => lead.city],
    ["客户类型", (lead) => lead.type],
    ["联系人", (lead) => lead.contactName],
    ["职位", (lead) => lead.contactRole],
    ["全部已核验邮箱", (lead) => (lead.emailSources || []).filter((item) =>
      (item.sources || []).some((source) => source.verified === true)
    ).map((item) => item.email).filter(Boolean).join(" ; ")],
    ["已核验邮箱来源", (lead) => (lead.emailSources || []).flatMap((item) =>
      (item.sources || []).filter((source) => source.verified === true)
        .map((source) => `${item.email} ← ${source.name || "公开来源"}: ${source.url}`)
    ).join(" ; ")],
    ["全部电话", (lead) => (lead.phoneSources || []).map((item) => item.value).filter(Boolean).join(" ; ") || lead.phone],
    ["电话来源", (lead) => (lead.phoneSources || []).flatMap((item) =>
      (item.sources || []).map((source) => `${item.value} ← ${source.name || "公开来源"}: ${source.url}`)
    ).join(" ; ")],
    ["全部 WhatsApp", (lead) => (lead.whatsappSources || []).map((item) => item.value).filter(Boolean).join(" ; ") || lead.whatsapp],
    ["WhatsApp 来源", (lead) => (lead.whatsappSources || []).flatMap((item) =>
      (item.sources || []).map((source) => `${item.value} ← ${source.name || "公开来源"}: ${source.url}`)
    ).join(" ; ")],
    ["客户官网", (lead) => lead.customerWebsite || lead.source],
    ["原始线索来源", (lead) => lead.sourceUrl],
    ["其他来源证据", (lead) => (lead.evidenceSources || []).map((item) => item.url).filter(Boolean).join(" ; ")],
    ["公司社媒账号", (lead) => (lead.socialProfiles || []).filter((item) => !String(item.accountType || "").includes("个人")).map((item) => `${item.platform}: ${item.url}`).join(" ; ")],
    ["个人/经营者账号", (lead) => (lead.socialProfiles || []).filter((item) => String(item.accountType || "").includes("个人")).map((item) => `${item.title}: ${item.url}`).join(" ; ")],
    ["客户评分", (lead) => lead.score],
    ["系统原始评分", (lead) => lead.baseScore],
    ["客户等级", (lead) => lead.scoreTier],
    ["人工校准", (lead) => lead.manualScoreAdjustment || 0],
    ["进出口资质分", (lead) => lead.scoreDimensions?.tradeQualification || 0],
    ["客户匹配分", (lead) => lead.scoreDimensions?.customerFit || 0],
    ["采购意向分", (lead) => lead.scoreDimensions?.purchaseIntent || 0],
    ["经营能力分", (lead) => lead.scoreDimensions?.businessCapacity || 0],
    ["车型匹配分", (lead) => lead.scoreDimensions?.modelFit || 0],
    ["可触达性分", (lead) => lead.scoreDimensions?.contactability || 0],
    ["风险扣分", (lead) => lead.scoreDimensions?.penalty || 0],
    ["信息可信度", (lead) => `${lead.confidenceLabel || ""} ${lead.confidence || 0}%`.trim()],
    ["推荐车型", (lead) => (lead.recommendedModels || [lead.model]).join("、")],
    ["主推车型", (lead) => lead.model],
    ["销售阶段", (lead) => lead.stage],
    ["下一步动作", (lead) => lead.next],
    ["计划跟进日期", (lead) => lead.nextFollowAt],
    ["是否疑似同行", (lead) => lead.isCompetitor ? "是" : "否"],
    ["尽调时间", (lead) => lead.researchAt],
    ["尽调摘要", (lead) => lead.researchSummary],
    ["系统建议", (lead) => lead.sourceCoverage?.decision],
    ["仍缺字段", (lead) => (lead.sourceCoverage?.missingFields || []).join("、")]
  ];
  const rows = [
    columns.map(([label]) => csvCell(label)).join(","),
    ...customers.map((lead) => columns.map(([, getter]) => csvCell(getter(lead))).join(","))
  ];
  const date = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  }).format(new Date());
  downloadFile(
    `\uFEFF${rows.join("\r\n")}`,
    `海外客户池-${date}.csv`,
    "text/csv;charset=utf-8"
  );
}

function loadSavedState() {
  const fallback = {
    reviewLeads: [],
    customers: [],
    rejectedLeads: [],
    quotes: [],
    _cloudVersion: 0,
    _cloudDirty: false
  };
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw);
    return {
      reviewLeads: Array.isArray(parsed.reviewLeads) ? parsed.reviewLeads : [],
      customers: Array.isArray(parsed.customers) ? parsed.customers : [],
      rejectedLeads: Array.isArray(parsed.rejectedLeads) ? parsed.rejectedLeads : [],
      quotes: Array.isArray(parsed.quotes) ? parsed.quotes : [],
      _cloudVersion: Number(parsed._cloudVersion || 0),
      _cloudDirty: Boolean(parsed._cloudDirty)
    };
  } catch {
    return fallback;
  }
}

function workspaceStateSnapshot() {
  return {
    reviewLeads,
    customers,
    rejectedLeads,
    quotes: quoteHistory
  };
}

function persistLocalState(dirty = localStateDirty) {
  localStateDirty = dirty;
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    ...workspaceStateSnapshot(),
    _cloudVersion: cloudStateVersion,
    _cloudDirty: localStateDirty
  }));
}

function recordIdentity(record, type) {
  if (type === "quotes") {
    if (record?.id) return `quotes:id:${record.id}`;
    return `${type}:${record?.customer || ""}|${record?.model || ""}|${record?.createdAt || ""}`;
  }
  if (record?.id) return `lead:id:${record.id}`;
  return `lead:${record?.company || ""}|${record?.country || ""}|${
    record?.customerWebsite || record?.sourceUrl || record?.source || ""
  }`.toLowerCase();
}

function mergeRecordLists(remoteList, localList, type) {
  const merged = new Map();
  (Array.isArray(remoteList) ? remoteList : []).forEach((record) => {
    merged.set(recordIdentity(record, type), record);
  });
  (Array.isArray(localList) ? localList : []).forEach((record) => {
    merged.set(recordIdentity(record, type), record);
  });
  return Array.from(merged.values()).slice(0, 5000);
}

function mergeWorkspaceStates(remoteState, localState) {
  const merged = {
    reviewLeads: mergeRecordLists(remoteState?.reviewLeads, localState?.reviewLeads, "reviewLeads"),
    customers: mergeRecordLists(remoteState?.customers, localState?.customers, "customers"),
    rejectedLeads: mergeRecordLists(remoteState?.rejectedLeads, localState?.rejectedLeads, "rejectedLeads"),
    quotes: mergeRecordLists(remoteState?.quotes, localState?.quotes, "quotes")
  };
  const localBuckets = new Map();
  ["reviewLeads", "customers", "rejectedLeads"].forEach((bucket) => {
    (Array.isArray(localState?.[bucket]) ? localState[bucket] : []).forEach((record) => {
      localBuckets.set(recordIdentity(record, bucket), bucket);
    });
  });
  ["reviewLeads", "customers", "rejectedLeads"].forEach((bucket) => {
    merged[bucket] = merged[bucket].filter((record) => {
      const localBucket = localBuckets.get(recordIdentity(record, bucket));
      return !localBucket || localBucket === bucket;
    });
  });
  return merged;
}

function applyWorkspaceState(state, render = false) {
  reviewLeads = Array.isArray(state?.reviewLeads) ? state.reviewLeads.map(normalizeLead) : [];
  customers = Array.isArray(state?.customers) ? state.customers.map(normalizeLead) : [];
  rejectedLeads = Array.isArray(state?.rejectedLeads) ? state.rejectedLeads.map(normalizeLead) : [];
  quoteHistory = Array.isArray(state?.quotes) ? state.quotes : [];
  persistLocalState(localStateDirty);
  if (render) {
    renderLeads();
    renderReview();
    renderCrm();
    renderFollowTasks();
    renderKpis();
    renderQuoteHistory();
    renderQuoteCustomerSelect();
  }
}

function setCloudSyncStatus(text, state = "syncing") {
  const status = $("#cloudSyncStatus");
  if (!status) return;
  status.dataset.syncState = state;
  const label = status.querySelector("span");
  if (label) label.textContent = text;
}

async function pushCloudState(state = workspaceStateSnapshot(), mergeAttempts = 0) {
  setCloudSyncStatus("正在同步云端数据", "syncing");
  const response = await fetch("/api/workspace-state", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state, expectedVersion: cloudStateVersion })
  });
  const result = await response.json().catch(() => ({}));
  if (response.status === 409 && result.conflict && result.current && mergeAttempts < 2) {
    const merged = mergeWorkspaceStates(result.current.state, state);
    cloudStateVersion = Number(result.current.version || 0);
    localStateDirty = true;
    applyWorkspaceState(merged, true);
    setCloudSyncStatus("检测到多端修改，正在安全合并", "conflict");
    return pushCloudState(merged, mergeAttempts + 1);
  }
  if (!response.ok || !result.ok) {
    throw new Error(result.error || `HTTP ${response.status}`);
  }
  cloudStateVersion = Number(result.version || cloudStateVersion);
  persistLocalState(false);
  setCloudSyncStatus("云端数据已同步", "synced");
  return result;
}

function scheduleCloudStateSave() {
  if (!cloudStateReady) return;
  window.clearTimeout(cloudSaveTimer);
  cloudSaveTimer = window.setTimeout(() => {
    const state = workspaceStateSnapshot();
    cloudSaveChain = cloudSaveChain
      .catch(() => undefined)
      .then(() => pushCloudState(state))
      .catch((error) => {
        setCloudSyncStatus("云端同步失败，已保留本地副本", "error");
        console.error("Cloud workspace sync failed:", error);
      });
  }, 650);
}

async function hydrateCloudState(render = false) {
  if (cloudHydrating) return;
  cloudHydrating = true;
  setCloudSyncStatus("正在读取云端数据", "syncing");
  try {
    const response = await fetch("/api/workspace-state", { cache: "no-store" });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    cloudStateVersion = Number(result.version || 0);
    if (result.exists) {
      if (localStateDirty) {
        const merged = mergeWorkspaceStates(result.state || {}, workspaceStateSnapshot());
        applyWorkspaceState(merged, render);
        cloudStateReady = true;
        setCloudSyncStatus("正在补传离线修改", "conflict");
        await pushCloudState(merged);
      } else {
        localStateDirty = false;
        applyWorkspaceState(result.state || {}, render);
        persistLocalState(false);
        setCloudSyncStatus("云端数据已同步", "synced");
      }
    } else {
      await pushCloudState(workspaceStateSnapshot());
    }
    cloudStateReady = true;
  } catch (error) {
    cloudStateReady = false;
    setCloudSyncStatus("云端不可用，当前使用本地副本", "error");
    console.error("Cloud workspace load failed:", error);
  } finally {
    cloudHydrating = false;
  }
}

function saveState() {
  persistLocalState(true);
  scheduleCloudStateSave();
}

function evaluateLeadScore(text, options = {}) {
  const value = String(text || "").toLowerCase();
  const dimensions = {
    tradeQualification: /import.{0,8}(license|licence|permit)|export.{0,8}(license|licence|permit)|licensed importer|customs (registration|registered|code)|trade license|commercial registration|进出口资质|进出口许可证|进口许可证|出口许可证|海关注册|海关备案|报关资质|贸易许可证|授权进口商/.test(value)
      ? 30
      : /vehicle importer|car importer|parallel import|import and export|汽车进口|平行进口/.test(value) ? 16 : 0,
    customerFit: /import|distributor|进口|分销|平行进口/.test(value)
      ? 25
      : /dealer|showroom|trading|经销|展厅|贸易/.test(value)
        ? 20
        : /fleet|rental|procurement|车队|租赁|采购/.test(value)
          ? 18
          : /automotive|vehicle|cars|汽车/.test(value) ? 10 : 0,
    purchaseIntent: /rfq|looking to buy|supplier wanted|dealer wanted|bulk order|询价|求购|招募经销商|批量采购/.test(value)
      ? 18
      : /procurement|wholesale|fleet purchase|采购|批发|车队/.test(value) ? 13 : 0,
    businessCapacity: /branches|locations|regional network|集团|分店|区域网络/.test(value)
      ? 11
      : /multi-brand|brand portfolio|多品牌/.test(value)
        ? 9
        : /luxury|premium|supercar|豪华|高端/.test(value) ? 6 : 0,
    modelFit: /electric|hybrid|new energy|chinese car|新能源|电动|混动|中国汽车/.test(value)
      ? 6
      : options.model ? 3 : 0,
    contactability: /owner|founder|director|procurement manager|老板|创始人|采购经理/.test(value)
      ? 5
      : /@|whatsapp|phone|contact|邮箱|电话|联系/.test(value) ? 4 : 0,
    penalty: 0
  };
  if (/repair|workshop|spare parts|car wash|detailing|维修|配件|洗车|美容/.test(value) &&
      !/import|distributor|dealer|showroom|vehicle sales|进口|分销|经销|展厅/.test(value)) {
    dimensions.penalty -= 45;
  }
  if (/classified|marketplace|individual seller|private seller|分类信息|个人卖家/.test(value)) {
    dimensions.penalty -= 55;
  }
  if (/china car exporter|vehicle export from china|中国汽车出口商/.test(value)) {
    dimensions.penalty -= 70;
  }
  const score = Math.max(0, Math.min(100, Object.values(dimensions).reduce((sum, points) => sum + points, 0)));
  return {
    score,
    dimensions,
    tier: score >= 80 ? "A" : score >= 65 ? "B" : score >= 50 ? "C" : "D"
  };
}

function scoreLeadFromText(text, options = {}) {
  return evaluateLeadScore(text, options).score;
}

function scoreTierLabel(tier) {
  return {
    A: "A级 · 高优先",
    B: "B级 · 值得跟进",
    C: "C级 · 继续核验",
    D: "D级 · 低优先"
  }[tier] || "待评级";
}

function scoreVisualClass(score) {
  return Number(score) >= 80 ? "excellent" : Number(score) >= 65 ? "good" : Number(score) >= 50 ? "mid" : "low";
}

function summarizeLead(lead) {
  if (lead.reason) return lead.reason;
  const grade = lead.score >= 75 ? "适合优先联系" : "需要人工复核";
  return `${lead.city || lead.country} 的${lead.type}，${grade}。建议结合官网信息推荐${lead.model}。`;
}

function renderCountries() {
  $("#countryGrid").innerHTML = countries.map((country) => `
    <article class="country-card" data-country="${escapeHtml(country.name)}" tabindex="0" role="button">
      <div class="country-rank">
        <span class="tag">${country.rank}</span>
        <span>${country.cities}</span>
      </div>
      <h3>${country.name}</h3>
      <p>${country.reason}</p>
      <p><strong>重点客户：</strong>${country.targets}</p>
      <span class="country-action">选择这个市场 →</span>
    </article>
  `).join("");
  const select = $("#finderCountry");
  const current = select.value;
  select.innerHTML = countries.map((country) =>
    `<option value="${escapeHtml(country.name)}">${escapeHtml(country.name)}</option>`
  ).join("");
  if (countries.some((country) => country.name === current)) select.value = current;
}

function chooseMarket(countryName) {
  const country = countries.find((item) => item.name === countryName);
  if (!country) return;
  $("#finderCountry").value = country.name;
  const form = $("#finderForm");
  form.goal.value = `寻找${country.cities.split(" / ")[0]}及周边的${country.targets}，适合销售华为系新能源汽车。`;
  const words = generateKeywords(form.goal.value, country.name, form.model.value);
  renderKeywords(words);
  updateSocialProspectingQueries();
  showSection("lead-finder");
}

function countryKey(value) {
  return String(value || "").split(" ")[0] === "Saudi" ? "Saudi Arabia" : String(value || "").split(" ")[0];
}

function renderRiskProfile(selected = "") {
  const select = $("#riskCountry");
  if (!select) return;
  const current = selected || select.value || countries[0].name;
  select.innerHTML = countries.map((country) =>
    `<option value="${escapeHtml(country.name)}">${escapeHtml(country.name)}</option>`
  ).join("");
  select.value = countries.some((country) => country.name === current) ? current : countries[0].name;
  const key = countryKey(select.value);
  const profile = riskProfiles[key] || riskProfiles.UAE;
  const items = [
    ["认证与上牌", profile.certification, "成交前"],
    ["语言与车机", profile.cockpit, "交车前"],
    ["物流与费用", profile.logistics, "报价前"],
    ["售后与备件", profile.service, "承诺前"]
  ];
  $("#riskGrid").innerHTML = items.map(([title, text, timing]) => `
    <article>
      <span class="risk-timing">${timing}</span>
      <h3>${title}</h3>
      <p>${text}</p>
    </article>
  `).join("");
}

function renderKeywords(words = defaultKeywords) {
  $("#keywords").innerHTML = words.map((word) => `<span>${word}</span>`).join("");
}

function renderLeads() {
  $("#leadList").innerHTML = reviewLeads.length ? reviewLeads.map((lead) => `
    <article class="lead-card">
      <h3>${escapeHtml(lead.company)}</h3>
      <div class="lead-meta">
        <span>${escapeHtml(lead.country)} / ${escapeHtml(lead.city)}</span>
        <span>${escapeHtml(lead.type)}</span>
        <span>${escapeHtml(lead.origin || "公开网页")}</span>
        <span>${escapeHtml(lead.sourceType || "公开商业网站")}</span>
      </div>
      <p>${escapeHtml(lead.reason)}</p>
      <strong class="score ${scoreVisualClass(lead.score)}">${lead.score} 分 · ${escapeHtml(lead.scoreTier || "D")}级</strong>
    </article>
  `).join("") : `<p class="empty">暂无待审核线索。请先点击“一键获客到待审核”。</p>`;
}

const finderStageOrder = ["search", "extract", "verify", "done"];

function setFinderProgress({ percent, stage, title, message, elapsed, state = "running" }) {
  const safePercent = Math.max(0, Math.min(100, Math.round(Number(percent) || 0)));
  const box = $("#finderStatus")?.closest(".insight-box");
  const bar = $("#finderProgressBar");
  const track = bar?.parentElement;
  if (box) box.dataset.progressState = state;
  if (bar) bar.style.width = `${safePercent}%`;
  if (track) track.setAttribute("aria-valuenow", String(safePercent));
  if ($("#finderProgressPercent")) $("#finderProgressPercent").textContent = `${safePercent}%`;
  if ($("#finderProgressTitle")) $("#finderProgressTitle").textContent = title || "正在处理";
  if ($("#finderElapsed") && elapsed !== undefined) $("#finderElapsed").textContent = elapsed;
  if ($("#finderStatus") && message) $("#finderStatus").textContent = message;

  const activeIndex = finderStageOrder.indexOf(stage);
  document.querySelectorAll("[data-progress-stage]").forEach((step) => {
    const index = finderStageOrder.indexOf(step.dataset.progressStage);
    step.classList.toggle("complete", activeIndex > index || (stage === "done" && safePercent === 100 && index <= activeIndex));
    step.classList.toggle("active", index === activeIndex && !(stage === "done" && safePercent === 100));
    const marker = step.querySelector("i");
    if (marker) marker.textContent = step.classList.contains("complete") ? "✓" : String(index + 1);
  });
}

function setFinderStatus(message) {
  const el = $("#finderStatus");
  if (el) el.textContent = message;
}

function startFinderSearchProgress() {
  const startedAt = Date.now();
  let percent = 6;
  const update = () => {
    const seconds = Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
    percent = Math.min(56, percent + (percent < 28 ? 4 : percent < 44 ? 2 : 1));
    const stage = percent < 34 ? "search" : "extract";
    setFinderProgress({
      percent,
      stage,
      title: stage === "search" ? "正在搜索公开来源" : "正在提取候选企业",
      elapsed: `已用时 ${seconds} 秒`,
      message: stage === "search"
        ? "正在查询地图、企业官网、行业目录与公开社媒主页。"
        : "正在从搜索结果中提取企业名称、官网、联系方式及原始来源。"
    });
  };
  update();
  const timer = window.setInterval(update, 900);
  return {
    startedAt,
    stop() {
      window.clearInterval(timer);
      return Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
    }
  };
}

function renderReview() {
  const rankedLeads = reviewLeads
    .map((lead, index) => ({ lead, index }))
    .sort((a, b) => Number(b.lead.score || 0) - Number(a.lead.score || 0));
  $("#reviewGrid").innerHTML = rankedLeads.length ? rankedLeads.map(({ lead, index }, rankIndex) => `
    <article class="review-card">
      <div class="review-title-row">
        <div>
          <span class="tag">#${rankIndex + 1} · ${lead.researchAt ? "已完成公开信息尽调" : "待全网补全"}</span>
          <h3>${escapeHtml(lead.company)}</h3>
          <p>${escapeHtml(lead.researchSummary || "当前只有原始发现来源，请先执行全网补全。")}</p>
        </div>
        <button class="research-button" type="button" data-research-index="${index}">
          ${lead.researching ? "正在检索…" : lead.researchAt ? "重新全网核验" : "全网补全信息"}
        </button>
      </div>
      <div class="review-decision">
        <div class="decision-main">
          <span>系统建议</span>
          <strong>${escapeHtml(lead.sourceCoverage?.decision || (lead.researchAt ? "建议人工复核" : "等待自动尽调"))}</strong>
        </div>
        <div class="decision-score"><span>商业机会评分</span><strong>${escapeHtml(lead.score)} 分 · ${escapeHtml(scoreTierLabel(lead.scoreTier))}</strong></div>
        <div><span>公开来源</span><strong>${escapeHtml(lead.sourceCoverage?.total || lead.evidenceSources?.length || 0)}</strong></div>
        <div><span>官方来源</span><strong>${escapeHtml(lead.sourceCoverage?.official || 0)}</strong></div>
        <div><span>独立域名</span><strong>${escapeHtml(lead.sourceCoverage?.independentDomains || 0)}</strong></div>
        <div class="decision-missing">
          <span>仍缺少</span>
          <strong>${escapeHtml((lead.sourceCoverage?.missingFields || []).join("、") || "关键字段齐全")}</strong>
        </div>
      </div>
      <dl class="review-key-info">
        <div>
          <dt>客户官网</dt>
          <dd>${safeHttpUrl(lead.customerWebsite) ? `<a href="${escapeHtml(safeHttpUrl(lead.customerWebsite))}" target="_blank" rel="noopener noreferrer">${escapeHtml(lead.customerWebsite)}</a>` : escapeHtml(lead.customerWebsite || "未发现")}</dd>
        </div>
        <div>
          <dt>联系人</dt>
          <dd>${escapeHtml([lead.contactName, lead.contactRole].filter(Boolean).join(" · ") || "未发现")}</dd>
        </div>
        <div class="key-email">
          <dt>已核验邮箱</dt>
          <dd>${renderEmailEvidence(lead)}</dd>
        </div>
        <div>
          <dt>电话 / WhatsApp</dt>
          <dd>${escapeHtml([lead.phone, lead.whatsapp].filter(Boolean).join(" · ") || "未发现")}</dd>
        </div>
        <div>
          <dt>可信度</dt>
          <dd><strong>${escapeHtml(lead.confidenceLabel || "待确认")} · ${escapeHtml(lead.confidence || 0)}%</strong></dd>
        </div>
        <div>
          <dt>推荐车型</dt>
          <dd>${escapeHtml((lead.recommendedModels || [lead.model]).join("、"))}</dd>
        </div>
        <div>
          <dt>机会信号</dt>
          <dd>${escapeHtml([...(lead.intentSignals || []), ...(lead.businessSignals || [])].join("、") || "汽车业务匹配，待进一步确认采购意向")}</dd>
        </div>
      </dl>
      <p class="review-recommendation"><strong>推荐联系理由：</strong>${escapeHtml(lead.contactReason || lead.reason)}</p>
      <div class="score-breakdown">
        <span>评分依据${lead.manualScoreAdjustment ? ` · 人工校准 ${lead.manualScoreAdjustment > 0 ? "+" : ""}${escapeHtml(lead.manualScoreAdjustment)}` : ""}</span>
        <div class="score-dimensions">
          <span>进出口资质 <strong>${escapeHtml(lead.scoreDimensions?.tradeQualification || 0)}/30</strong></span>
          <span>客户匹配 <strong>${escapeHtml(lead.scoreDimensions?.customerFit || 0)}/25</strong></span>
          <span>采购意向 <strong>${escapeHtml(lead.scoreDimensions?.purchaseIntent || 0)}/18</strong></span>
          <span>经营能力 <strong>${escapeHtml(lead.scoreDimensions?.businessCapacity || 0)}/12</strong></span>
          <span>车型匹配 <strong>${escapeHtml(lead.scoreDimensions?.modelFit || 0)}/10</strong></span>
          <span>可触达性 <strong>${escapeHtml(lead.scoreDimensions?.contactability || 0)}/5</strong></span>
          ${Number(lead.scoreDimensions?.penalty || 0) < 0
            ? `<span class="penalty">风险扣分 <strong>${escapeHtml(lead.scoreDimensions.penalty)}</strong></span>`
            : ""}
        </div>
        <div>${(lead.scoreBreakdown || []).length
          ? lead.scoreBreakdown.map((item) => `<b class="${Number(item.points) < 0 ? "negative" : ""}">${escapeHtml(item.label)} ${Number(item.points) > 0 ? "+" : ""}${escapeHtml(item.points)}</b>`).join("")
          : `<b>${escapeHtml(lead.scoreBasis || "等待官网核验")}</b>`}
        </div>
        <div class="score-calibration">
          <span>人工校准</span>
          <button type="button" data-score-adjust="-5" data-index="${index}">-5</button>
          <button type="button" data-score-adjust="5" data-index="${index}">+5</button>
          <button type="button" data-score-reset data-index="${index}">恢复系统分</button>
        </div>
      </div>
      <details class="review-more">
        <summary>
          <span>查看全部来源与核验详情</span>
          <small>${lead.sourceCoverage?.total || lead.evidenceSources?.length || 0} 个来源 · ${(lead.socialProfiles || []).length} 个社媒账号</small>
        </summary>
        <div class="review-more-content">
      <dl class="source-evidence">
        <div><dt>来源网站</dt><dd>${escapeHtml(lead.origin || "公开网页")}</dd></div>
        <div><dt>网站类型</dt><dd>${escapeHtml(lead.sourceType || "公开商业网站")}</dd></div>
        ${lead.googleRating ? `<div><dt>地图评分</dt><dd>${escapeHtml(lead.googleRating)} / 5 · ${escapeHtml(lead.googleReviews || 0)} 条评价</dd></div>` : ""}
        ${lead.businessStatus ? `<div><dt>营业状态</dt><dd>${escapeHtml(lead.businessStatus)}</dd></div>` : ""}
        <div><dt>发布日期</dt><dd>${escapeHtml(lead.publishedAt || "未识别日期")}</dd></div>
        <div><dt>时间范围</dt><dd>${lead.freshnessDays ? `最近 ${escapeHtml(lead.freshnessDays)} 天` : "不限时间"}</dd></div>
        <div><dt>线索标题</dt><dd>${escapeHtml(lead.sourceTitle || lead.company)}</dd></div>
        <div><dt>客户官网</dt><dd>${escapeHtml(lead.customerWebsite || "原线索未提供")}</dd></div>
        <div><dt>联系人</dt><dd>${renderValueEvidence(lead.contactNameSources, lead.contactName)}</dd></div>
        <div><dt>职位</dt><dd>${renderValueEvidence(lead.contactRoleSources, lead.contactRole)}</dd></div>
        <div class="email-evidence-row"><dt>邮箱</dt><dd>${renderEmailEvidence(lead)}</dd></div>
        ${(lead.unverifiedEmailCandidates || []).length ? `
          <div class="unverified-email-row">
            <dt>已排除邮箱</dt>
            <dd>${escapeHtml((lead.unverifiedEmailCandidates || []).map((item) => item.email).join("、"))}
              <small>未能在可回查的原始页面中确认，不作为可联系邮箱。</small>
            </dd>
          </div>
        ` : ""}
        <div><dt>电话</dt><dd>${renderValueEvidence(lead.phoneSources, lead.phone)}</dd></div>
        <div><dt>WhatsApp</dt><dd>${renderValueEvidence(lead.whatsappSources, lead.whatsapp)}</dd></div>
        <div><dt>社媒账号</dt><dd>${(lead.socialProfiles || []).length || (lead.socialAccounts || []).length || "公开页面未发现"}</dd></div>
        <div><dt>是否重复</dt><dd>${lead.isDuplicate ? "是，需要合并" : "否（已自动去重）"}</dd></div>
        <div><dt>是否同行</dt><dd>${lead.isCompetitor ? "疑似同行，谨慎联系" : "未发现明显同行特征"}</dd></div>
        <div><dt>信息可信度</dt><dd>${escapeHtml(lead.confidenceLabel || "待人工确认")} · ${escapeHtml(lead.confidence || 0)}%</dd></div>
        <div><dt>适合车型</dt><dd>${escapeHtml((lead.recommendedModels || [lead.model]).join("、"))}</dd></div>
      </dl>
      <div class="social-profile-section">
        <div class="evidence-heading">
          <div><strong>Facebook / Instagram / TikTok / YouTube / LinkedIn</strong><span>${(lead.socialProfiles || []).length} 个已识别公开账号</span></div>
          <small>区分公司账号与个人决策人；平台未公开的字段不会推测</small>
        </div>
        <div class="social-profile-grid">
          ${(lead.socialProfiles || []).length ? lead.socialProfiles.map((profile) => `
            <article>
              <div class="social-profile-top">
                <span class="social-platform">${escapeHtml(profile.platform || "社交媒体")}</span>
                <span class="social-kind ${String(profile.accountType || "").includes("个人") ? "person" : ""}">${escapeHtml(profile.accountType || "公司账号")}</span>
              </div>
              <h4>${escapeHtml(profile.title || profile.handle || lead.company)}</h4>
              <p>${escapeHtml(profile.description || "平台未返回公开简介，请打开主页核验。")}</p>
              ${(profile.businessSignals || []).length || (profile.intentSignals || []).length || profile.decisionRole ? `
                <div class="social-business-signals">
                  ${(profile.businessSignals || []).map((signal) => `<b>${escapeHtml(signal)}</b>`).join("")}
                  ${(profile.intentSignals || []).map((signal) => `<b class="intent">${escapeHtml(signal)}</b>`).join("")}
                  ${profile.decisionRole ? `<b class="person">${escapeHtml(profile.decisionRole)}</b>` : ""}
                </div>
              ` : ""}
              ${profile.businessConfidence ? `<small>商业账号识别置信度：${escapeHtml(profile.businessConfidence)}%</small>` : ""}
              <small>关联依据：${escapeHtml(profile.relationship || "公开搜索")}</small>
              ${safeHttpUrl(profile.url) ? `<a href="${escapeHtml(safeHttpUrl(profile.url))}" target="_blank" rel="noopener noreferrer">打开公开主页 ↗</a>` : ""}
            </article>
          `).join("") : `
            <div class="social-empty">
              <strong>暂未识别到公开社媒账号</strong>
              <p>点击“全网补全信息”后，系统会检索公司官方账号和公开个人决策人账号。</p>
            </div>
          `}
        </div>
      </div>
      <div class="evidence-section">
        <div class="evidence-heading">
          <div><strong>真实来源与证据</strong><span>${(lead.evidenceSources || []).length} 个公开来源</span></div>
          <small>每条信息均保留原始网址，不以系统推断代替来源</small>
        </div>
        <div class="evidence-list">
          ${(lead.evidenceSources || []).length ? lead.evidenceSources.map((source) => `
            <article>
              <div>
                <span>${escapeHtml(source.sourceType || "公开网页")} · ${escapeHtml(source.reliability || "C")}级</span>
                <strong>${escapeHtml(source.sourceName || "公开来源")}</strong>
              </div>
              <h4>${escapeHtml(source.title || lead.company)}</h4>
              <p>${escapeHtml(source.excerpt || "该来源未提供可提取的文字摘要，请打开原文核验。")}</p>
              <small class="source-reliability">${escapeHtml(source.reliabilityReason || "公开来源，建议人工核验")}</small>
              ${safeHttpUrl(source.url) ? `<a href="${escapeHtml(safeHttpUrl(source.url))}" target="_blank" rel="noopener noreferrer">打开来源原文 ↗</a>` : ""}
            </article>
          `).join("") : `<p class="empty">尚未建立证据链，请点击“全网补全信息”。</p>`}
        </div>
      </div>
      <div class="source-original">
        <strong>原始线索摘要</strong>
        <p>${escapeHtml(lead.sourceExcerpt || lead.website || "暂无可提取的原文内容，请点击原文链接核实。")}</p>
      </div>
      <p><strong>中文判断：</strong>${escapeHtml(lead.reason)}</p>
      <p><strong>审核作用：</strong>确认这是可联系的商业客户，不把文章页、重复客户或无授权线索放进客户池。</p>
        </div>
      </details>
      <div class="split-actions">
        ${safeHttpUrl(lead.sourceUrl || lead.source) ? `<a class="button-link ghost" href="${escapeHtml(safeHttpUrl(lead.sourceUrl || lead.source))}" target="_blank" rel="noopener noreferrer">查看线索原文</a>` : ""}
        <button class="primary" type="button" data-review-action="approve" data-index="${index}"
          ${!lead.researchAt || lead.confidence < 50 || lead.isCompetitor ? "disabled" : ""}>
          ${lead.isCompetitor ? "疑似同行，不建议入池" : !lead.researchAt ? "先完成全网补全" : lead.confidence < 50 ? "证据不足，暂不能通过" : "通过，进入客户池"}
        </button>
        <button class="ghost" type="button" data-review-action="reject" data-index="${index}">拒绝</button>
      </div>
    </article>
  `).join("") : `<p class="empty">暂无待审核线索。一键获客抓到的客户会先出现在这里。</p>`;
}

function renderCrm() {
  $("#crmRows").innerHTML = customers.length ? customers.map((lead, index) => `
    <tr>
      <td><strong>${escapeHtml(lead.company)}</strong><br><span>${escapeHtml(lead.contactName || lead.email || lead.phone || "暂无联系人")}</span></td>
      <td>${escapeHtml(lead.country)}<br>${escapeHtml(lead.city)}</td>
      <td>${escapeHtml(lead.type)}</td>
      <td>${escapeHtml(lead.model)}</td>
      <td><span class="score ${scoreVisualClass(lead.score)}">${lead.score} · ${escapeHtml(lead.scoreTier || "D")}级</span></td>
      <td>
        <select class="crm-stage" data-crm-stage="${index}">
          ${salesStages.map((stage) => `<option ${stage === lead.stage ? "selected" : ""}>${stage}</option>`).join("")}
        </select>
      </td>
      <td><input class="crm-next" data-crm-next="${index}" value="${escapeHtml(lead.next || "")}" aria-label="下一步动作"></td>
      <td>
        <div class="crm-actions">
          <button type="button" data-crm-action="email" data-index="${index}">写开发信</button>
          <button type="button" data-crm-action="quote" data-index="${index}">去报价</button>
        </div>
      </td>
    </tr>
  `).join("") : `<tr><td colspan="8">暂无正式客户。请先完成全网核验，再在线索审核中点击“通过”。</td></tr>`;
  $("#heroPending").textContent = reviewLeads.length;
  $("#heroCustomers").textContent = customers.length;
  $("#heroGradeA").textContent = customers.filter((lead) => lead.score >= 75).length;
  renderLeadSelect();
}

function renderLeadSelect() {
  const select = $("#leadSelect");
  if (!select) return;
  select.innerHTML = customers.length ? customers.map((lead, index) => `<option value="${index}">${lead.company} · ${lead.country} · ${lead.model}</option>`).join("") : `<option value="">客户池暂无客户</option>`;
}

function renderQuoteCustomerSelect() {
  const select = $("#quoteCustomer");
  if (!select) return;
  const current = select.value;
  select.innerHTML = `<option value="">未选择客户</option>${customers.map((lead, index) =>
    `<option value="${index}">${escapeHtml(lead.company)} · ${escapeHtml(lead.country)}</option>`
  ).join("")}`;
  if ([...select.options].some((option) => option.value === current)) select.value = current;
}

function openCustomerInEmail(index) {
  const lead = customers[index];
  if (!lead) return;
  const form = $("#emailForm");
  $("#leadSelect").value = String(index);
  form.company.value = lead.company;
  form.contactName.value = lead.contactName || "";
  form.website.value = lead.customerWebsite || lead.sourceUrl || lead.source || "";
  form.websiteText.value = [
    lead.sourceExcerpt,
    lead.researchSummary,
    (lead.evidenceSources || []).slice(0, 4).map((item) => item.excerpt).join(" ")
  ].filter(Boolean).join(" ").slice(0, 2400);
  form.model.value = String(lead.model || "问界 M9").split("/")[0].trim();
  showSection("email");
}

function applyCustomerToQuote(index) {
  const lead = customers[index];
  if (!lead) return;
  $("#quoteCustomer").value = String(index);
  $("#quoteModel").value = String(lead.model || "问界 M9").split("/")[0].trim();
  $("#quotePrice").value = modelReferencePrices[$("#quoteModel").value] || 0;
  const destination = destinationByCountry[countryKey(lead.country)];
  if (destination && [...$("#quoteForm").destination.options].some((option) => option.value === destination)) {
    $("#quoteForm").destination.value = destination;
  }
  renderQuote(Object.fromEntries(new FormData($("#quoteForm")).entries()));
}

function openCustomerInQuote(index) {
  if (!customers[index]) return;
  showSection("quote");
  applyCustomerToQuote(index);
}

function defaultNextAction(stage) {
  return {
    "准备联系": "生成开发信并人工确认",
    "已联系": "等待客户回复，3 天后再次跟进",
    "有回复": "确认需求、数量、配置和目的港",
    "报价中": "发送正式报价并确认有效期",
    "谈判中": "记录价格异议和成交条件",
    "已成交": "确认收款、合同、排产与物流",
    "暂缓": "记录暂缓原因和重新联系日期",
    "已流失": "记录流失原因，停止自动跟进"
  }[stage] || "";
}

function updateCustomerStage(index, stage) {
  const lead = customers[index];
  if (!lead) return;
  lead.stage = stage;
  lead.next = defaultNextAction(stage);
  lead.nextFollowAt = stage === "已联系"
    ? new Date(Date.now() + 3 * 86400000).toLocaleDateString("zh-CN")
    : lead.nextFollowAt || "";
  refreshAllLeadViews();
}

function refreshAllLeadViews() {
  renderLeads();
  renderReview();
  renderCrm();
  renderFollowTasks();
  renderKpis();
  renderQuoteHistory();
  renderQuoteCustomerSelect();
  saveState();
}

function normalizeLead(raw) {
  const website = raw.website || raw.reason || `${raw.company || "Unknown"} ${raw.type || ""}`;
  const fallbackEvaluation = evaluateLeadScore(
    `${raw.company} ${raw.type} ${raw.country} ${website}`,
    { model: raw.model }
  );
  const scoreModelVersion = Number(raw.scoreModelVersion || 0);
  const baseScore = scoreModelVersion >= 6
    ? Number(raw.baseScore ?? raw.score ?? fallbackEvaluation.score)
    : fallbackEvaluation.score;
  const manualScoreAdjustment = Math.max(-20, Math.min(20, Number(raw.manualScoreAdjustment || 0)));
  const score = Math.max(0, Math.min(100, baseScore + manualScoreAdjustment));
  const scoreTier = score >= 80 ? "A" : score >= 65 ? "B" : score >= 50 ? "C" : "D";
  const fallbackBreakdown = Object.entries(fallbackEvaluation.dimensions)
    .filter(([, points]) => points)
    .map(([category, points]) => ({
      category,
      label: {
        tradeQualification: "进出口资质",
        customerFit: "客户类型匹配",
        purchaseIntent: "采购意向信号",
        businessCapacity: "经营能力信号",
        modelFit: "目标车型匹配",
        contactability: "公开可触达性",
        penalty: "风险扣分"
      }[category],
      points
    }));
  return {
    id: raw.id || recordIdentity(raw, "lead"),
    company: raw.company || "未命名客户",
    country: raw.country || "",
    city: raw.city || "",
    type: raw.type || "Auto business",
    source: raw.source || "Website",
    origin: raw.origin || "公开网页",
    sourceType: raw.sourceType || "公开商业网站",
    sourceTitle: raw.sourceTitle || raw.company || "未命名线索",
    sourceUrl: raw.sourceUrl || raw.source || "",
    sourceExcerpt: raw.sourceExcerpt || raw.website || raw.reason || "",
    evidenceSources: Array.isArray(raw.evidenceSources) ? raw.evidenceSources : (
      raw.sourceUrl || raw.source ? [{
        title: raw.sourceTitle || raw.company || "原始线索",
        url: raw.sourceUrl || raw.source,
        excerpt: raw.sourceExcerpt || raw.website || raw.reason || "",
        sourceName: raw.origin || "公开网页",
        sourceType: raw.sourceType || "公开商业网站"
      }] : []
    ),
    researchAt: raw.researchAt || "",
    researchSummary: raw.researchSummary || "",
    researching: false,
    publishedAt: raw.publishedAt || "",
    freshnessDays: raw.freshnessDays || null,
    customerWebsite: raw.customerWebsite || "",
    contactName: raw.contactName || "",
    contactRole: raw.contactRole || "",
    email: raw.email || "",
    emailSources: Array.isArray(raw.emailSources) && raw.emailSources.length
      ? raw.emailSources
      : raw.email
        ? [{
            email: raw.email,
            sources: raw.sourceUrl || raw.source
              ? [{ url: raw.sourceUrl || raw.source, name: raw.origin || "原始来源" }]
              : []
          }]
        : [],
    unverifiedEmailCandidates: Array.isArray(raw.unverifiedEmailCandidates) ? raw.unverifiedEmailCandidates : [],
    phone: raw.phone || "",
    phoneSources: Array.isArray(raw.phoneSources) ? raw.phoneSources : [],
    whatsapp: raw.whatsapp || "",
    whatsappSources: Array.isArray(raw.whatsappSources) ? raw.whatsappSources : [],
    contactNameSources: Array.isArray(raw.contactNameSources) ? raw.contactNameSources : [],
    contactRoleSources: Array.isArray(raw.contactRoleSources) ? raw.contactRoleSources : [],
    socialAccounts: Array.isArray(raw.socialAccounts) ? raw.socialAccounts : [],
    socialProfiles: Array.isArray(raw.socialProfiles) ? raw.socialProfiles : [],
    socialBusinessSignals: Array.isArray(raw.socialBusinessSignals) ? raw.socialBusinessSignals : [],
    socialIntentSignals: Array.isArray(raw.socialIntentSignals) ? raw.socialIntentSignals : [],
    socialDecisionRole: raw.socialDecisionRole || "",
    socialBusinessConfidence: Number(raw.socialBusinessConfidence || 0),
    accountType: raw.accountType || "公司客户",
    isDuplicate: Boolean(raw.isDuplicate),
    isCompetitor: Boolean(raw.isCompetitor),
    confidence: Number(raw.confidence || 0),
    confidenceLabel: raw.confidenceLabel || "待人工确认",
    sourceCoverage: raw.sourceCoverage || {
      total: Array.isArray(raw.evidenceSources) ? raw.evidenceSources.length : 0,
      official: 0,
      independentDomains: 0,
      contactable: Boolean(raw.email || raw.phone || raw.whatsapp),
      missingFields: [],
      decision: raw.researchAt ? "建议人工复核" : "待全网核验"
    },
    recommendedModels: Array.isArray(raw.recommendedModels) ? raw.recommendedModels : [raw.model || "问界 M9"],
    businessSignals: Array.isArray(raw.businessSignals) ? raw.businessSignals : [],
    intentSignals: Array.isArray(raw.intentSignals) ? raw.intentSignals : [],
    contactReason: raw.contactReason || "",
    sourceTranslation: raw.sourceTranslation || "",
    googleRating: Number(raw.googleRating || 0),
    googleReviews: Number(raw.googleReviews || 0),
    businessStatus: raw.businessStatus || "",
    baseScore,
    scoreModelVersion: 6,
    manualScoreAdjustment,
    scoreTier,
    scoreDimensions: scoreModelVersion >= 6 && raw.scoreDimensions
      ? raw.scoreDimensions
      : fallbackEvaluation.dimensions,
    scoreBreakdown: scoreModelVersion >= 6 && Array.isArray(raw.scoreBreakdown) && raw.scoreBreakdown.length
      ? raw.scoreBreakdown
      : fallbackBreakdown,
    scoreBasis: scoreModelVersion >= 6 && raw.scoreBasis
      ? raw.scoreBasis
      : "100分机会模型：进出口资质30、客户匹配25、采购意向18、经营能力12、车型匹配10、可触达性5",
    model: raw.model || "问界 M9",
    score,
    stage: raw.stage || "待审核",
    next: raw.next || "审核通过后生成英文开发信",
    nextFollowAt: raw.nextFollowAt || "",
    website,
    reason: raw.reason || `${raw.city || raw.country} 的${raw.type || "汽车相关客户"}，建议人工审核后再联系。`
  };
}

function approveLead(index) {
  const candidate = reviewLeads[index];
  if (!candidate || !candidate.researchAt || candidate.confidence < 50 || candidate.isCompetitor) return;
  const lead = reviewLeads.splice(index, 1)[0];
  if (!lead) return;
  customers.unshift({
    ...lead,
    stage: "准备联系",
    next: "生成英文开发信并人工确认",
    nextFollowAt: ""
  });
  refreshAllLeadViews();
}

function calibrateLeadScore(index, delta = 0, reset = false) {
  const lead = reviewLeads[index];
  if (!lead) return;
  lead.manualScoreAdjustment = reset
    ? 0
    : Math.max(-20, Math.min(20, Number(lead.manualScoreAdjustment || 0) + Number(delta || 0)));
  lead.score = Math.max(0, Math.min(100, Number(lead.baseScore || 0) + lead.manualScoreAdjustment));
  lead.scoreTier = lead.score >= 80 ? "A" : lead.score >= 65 ? "B" : lead.score >= 50 ? "C" : "D";
  refreshAllLeadViews();
}

function rejectLead(index) {
  const lead = reviewLeads.splice(index, 1)[0];
  if (!lead) return;
  rejectedLeads.unshift({ ...lead, stage: "已拒绝" });
  refreshAllLeadViews();
}

async function researchLead(index) {
  const lead = reviewLeads[index];
  if (!lead || lead.researching) return;
  lead.researching = true;
  renderReview();
  try {
    const response = await fetch(`/api/research?${new URLSearchParams({
      company: lead.company,
      country: [lead.city, lead.country].filter(Boolean).join(", "),
      website: lead.customerWebsite || "",
      sourceUrl: lead.sourceUrl || lead.source || "",
      model: lead.model || "",
      type: lead.type || ""
    })}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const result = await response.json();
    if (!result.ok) throw new Error(result.error || "检索失败");
    const verifiedPriority = result.isCompetitor
      ? Math.min(45, Number(result.score || lead.baseScore || lead.score || 0))
      : Number(result.score || lead.baseScore || lead.score || 0);
    reviewLeads[index] = normalizeLead({
      ...lead,
      ...result,
      score: verifiedPriority,
      baseScore: verifiedPriority,
      manualScoreAdjustment: lead.manualScoreAdjustment || 0,
      scoreTier: result.scoreTier,
      scoreDimensions: result.scoreDimensions,
      evidenceSources: result.evidenceSources || lead.evidenceSources,
      contactName: result.contactName || lead.contactName,
      contactRole: result.contactRole || lead.contactRole,
      email: result.email || lead.email,
      emailSources: mergeEmailSources(lead.emailSources || [], result.emailSources || []),
      unverifiedEmailCandidates: result.unverifiedEmailCandidates || [],
      phone: result.phone || lead.phone,
      phoneSources: result.phoneSources || lead.phoneSources || [],
      whatsapp: result.whatsapp || lead.whatsapp,
      whatsappSources: result.whatsappSources || lead.whatsappSources || [],
      contactNameSources: result.contactNameSources || lead.contactNameSources || [],
      contactRoleSources: result.contactRoleSources || lead.contactRoleSources || [],
      sourceCoverage: result.sourceCoverage || lead.sourceCoverage,
      scoreBreakdown: result.scoreBreakdown || lead.scoreBreakdown || [],
      scoreBasis: result.scoreBasis || lead.scoreBasis,
      businessSignals: result.businessSignals || lead.businessSignals || [],
      intentSignals: result.intentSignals || lead.intentSignals || [],
      socialAccounts: [...new Set([...(lead.socialAccounts || []), ...(result.socialAccounts || [])])],
      socialProfiles: result.socialProfiles || lead.socialProfiles || [],
      socialBusinessSignals: result.socialBusinessSignals || lead.socialBusinessSignals || [],
      socialIntentSignals: result.socialIntentSignals || lead.socialIntentSignals || [],
      socialDecisionRole: result.socialDecisionRole || lead.socialDecisionRole || "",
      socialBusinessConfidence: result.socialBusinessConfidence || lead.socialBusinessConfidence || 0,
      researching: false
    });
    refreshAllLeadViews();
  } catch (error) {
    lead.researching = false;
    lead.researchSummary = `全网补全失败：${error.message}。请确认本地服务可联网后重试。`;
    renderReview();
  }
}

async function researchAllLeads() {
  const button = $("#researchAllLeads");
  const pending = reviewLeads
    .map((lead, index) => ({ lead, index }))
    .filter(({ lead }) => !lead.researchAt);
  if (!pending.length) {
    button.textContent = "全部已完成核验";
    setTimeout(() => { button.textContent = "全网补全全部线索"; }, 1600);
    return;
  }
  button.disabled = true;
  for (let offset = 0; offset < pending.length; offset += 3) {
    button.textContent = `正在补全 ${Math.min(offset + 3, pending.length)} / ${pending.length}`;
    await Promise.all(pending.slice(offset, offset + 3).map(({ index }) => researchLead(index)));
  }
  button.disabled = false;
  button.textContent = "全网补全全部线索";
}

async function autoResearchNewLeads(count, sourceLabel, freshnessLabel) {
  if (!count) return;
  for (let offset = 0; offset < count; offset += 2) {
    const end = Math.min(offset + 2, count);
    setFinderProgress({
      percent: 62 + (end / count) * 32,
      stage: "verify",
      title: `正在核验 ${end} / ${count}`,
      message: `${sourceLabel} · ${freshnessLabel}：正在逐条核对官网、联系方式与来源证据。`
    });
    await Promise.all(
      Array.from({ length: end - offset }, (_, index) => researchLead(offset + index))
    );
  }
  const verified = reviewLeads.slice(0, count).filter((lead) => lead.researchAt).length;
  const contactable = reviewLeads.slice(0, count).filter((lead) => lead.sourceCoverage?.contactable).length;
  const recommended = reviewLeads.slice(0, count).filter(
    (lead) => lead.sourceCoverage?.decision === "建议优先联系"
  ).length;
  setFinderProgress({
    percent: 100,
    stage: "done",
    state: "complete",
    title: "获客流程已完成",
    message: `${sourceLabel} · ${freshnessLabel}：${count} 条新线索已自动核验。` +
      `${verified} 条完成证据链，${contactable} 条有公开联系方式，${recommended} 条建议优先联系。`
  });
}

function generateKeywords(goal, country, model, options = {}) {
  const modelName = productProfiles[model]?.english || model;
  const place = country.split(" ")[0];
  const city = String(options.cityFocus || "").trim();
  const customerTypes = String(options.customerTypes || "").trim();
  const exclusions = String(options.exclusions || "").trim();
  const goalText = String(goal || "");
  let targetTerms = ["automotive importer", "car dealer showroom", "vehicle distributor"];
  if (/租赁|车队|fleet|rental/i.test(goalText)) targetTerms = ["car rental company", "fleet operator", "chauffeur fleet"];
  if (/政府|项目|招标|government|tender/i.test(goalText)) targetTerms = ["government vehicle tender", "public fleet procurement", "official vehicle project"];
  if (/企业|采购|corporate|procurement/i.test(goalText)) targetTerms = ["corporate fleet procurement", "company vehicle buyer", "business car tender"];
  if (/求购|正在购买|个人买家|wanted|rfq/i.test(goalText)) targetTerms = ["vehicle buying request", "car RFQ", "wanted electric SUV"];
  return [
    `${city || place} automotive importer vehicle distributor`,
    `${city || place} car dealer showroom auto trading`,
    `${place} parallel import car dealer`,
    `${place} vehicle procurement RFQ fleet purchase`,
    `${place} new brand dealership distribution opportunity`,
    `${place} Chinese EV importer distributor`,
    `${modelName} market fit ${city || place}`
  ];
}

function updateSocialProspectingQueries() {
  const form = $("#finderForm");
  if (!form || !$("#socialSearchQuery")) return;
  const country = countries.find((item) => item.name === form.country.value);
  const place = country?.cities?.split(" / ")[0] || String(form.country.value || "UAE").split(" ")[0];
  const countryName = String(form.country.value || "UAE").split(" ")[0];
  const goal = String(form.goal.value || "");
  let facebookQueries = [
    `${place} car dealer`,
    `${place} car showroom`,
    `${countryName} car importer`,
    `${place} automotive trading`
  ];
  let instagramTags = [
    `${place}cars`,
    `${place}carshowroom`,
    `${countryName}cars`,
    `${place}cardealer`
  ];
  let businessTerms = ["car importer", "car dealer", "vehicle distributor"];
  let roleTerms = ["dealership owner", "import manager", "procurement manager"];
  if (/租赁|车队|fleet|rental/i.test(goal)) {
    facebookQueries = [`${place} car rental`, `${place} fleet company`, `${countryName} fleet`, `${place} chauffeur cars`];
    instagramTags = [`${place}carrental`, `${place}fleet`, `${countryName}carrental`, `${place}chauffeur`];
    businessTerms = ["fleet company", "car rental", "vehicle procurement"];
    roleTerms = ["fleet manager", "procurement manager", "rental owner"];
  } else if (/平行进口|parallel/i.test(goal)) {
    facebookQueries = [`${place} imported cars`, `${place} car importer`, `${countryName} auto trading`, `${place} used luxury cars`];
    instagramTags = [`${place}importedcars`, `${place}carimport`, `${countryName}autotrading`, `${place}luxurycars`];
    businessTerms = ["parallel import cars", "car importer", "auto trading"];
    roleTerms = ["import manager", "dealership owner", "general manager"];
  } else if (/豪华|高端|luxury|premium/i.test(goal)) {
    facebookQueries = [`${place} luxury cars`, `${place} luxury car dealer`, `${place} car showroom`, `${countryName} car importer`];
    instagramTags = [`${place}luxurycars`, `${place}supercars`, `${place}carshowroom`, `${countryName}cars`];
    businessTerms = ["luxury car dealer", "premium showroom", "car importer"];
    roleTerms = ["showroom owner", "sales director", "import manager"];
  }
  const cleanTag = (value) => value.toLowerCase().replace(/[^a-z0-9]/g, "");
  $("#socialSearchQuery").textContent = `${place}：五个平台公开商业账号搜索包`;
  $("#facebookSearchLinks").innerHTML = facebookQueries.map((query) =>
    `<a href="https://www.facebook.com/search/pages/?q=${encodeURIComponent(query)}" target="_blank" rel="noopener noreferrer" data-social-platform="Facebook">${escapeHtml(query)} ↗</a>`
  ).join("");
  $("#instagramSearchLinks").innerHTML = instagramTags.map((tag) => {
    const clean = cleanTag(tag);
    return `<a href="https://www.instagram.com/explore/tags/${encodeURIComponent(clean)}/" target="_blank" rel="noopener noreferrer" data-social-platform="Instagram">#${escapeHtml(clean)} ↗</a>`;
  }).join("");
  $("#tiktokSearchLinks").innerHTML = businessTerms.map((term) => {
    const query = `${place} ${term}`;
    return `<a href="https://www.tiktok.com/search/user?q=${encodeURIComponent(query)}" target="_blank" rel="noopener noreferrer" data-social-platform="TikTok">${escapeHtml(query)} ↗</a>`;
  }).join("");
  $("#youtubeSearchLinks").innerHTML = businessTerms.map((term) => {
    const query = `${place} ${term}`;
    return `<a href="https://www.youtube.com/results?search_query=${encodeURIComponent(query)}" target="_blank" rel="noopener noreferrer" data-social-platform="YouTube">${escapeHtml(query)} ↗</a>`;
  }).join("");
  $("#linkedinSearchLinks").innerHTML = [
    ...businessTerms.map((term) => `${place} ${term}`),
    ...roleTerms.map((term) => `${place} ${term}`)
  ].map((query) =>
    `<a href="https://www.linkedin.com/search/results/all/?keywords=${encodeURIComponent(query)}" target="_blank" rel="noopener noreferrer" data-social-platform="LinkedIn">${escapeHtml(query)} ↗</a>`
  ).join("");
}

function socialPlatformFromUrl(url) {
  const domain = (() => {
    try { return new URL(url).hostname.toLowerCase(); } catch { return ""; }
  })();
  if (domain.includes("youtube")) return "YouTube";
  if (domain.includes("facebook")) return "Facebook";
  if (domain.includes("instagram")) return "Instagram";
  if (domain.includes("tiktok")) return "TikTok";
  if (domain.includes("linkedin")) return "LinkedIn";
  if (domain.includes("threads")) return "Threads";
  if (domain.includes("pinterest")) return "Pinterest";
  return "官网";
}

function analyzeSocialBusinessText(text, accountType = "") {
  const value = String(text || "").toLowerCase();
  const signalRules = {
    "汽车进口": /vehicle importer|car importer|automotive importer|parallel import|汽车进口|平行进口/,
    "汽车经销": /car dealer|dealership|showroom|auto trading|motors|汽车经销|展厅|汽车贸易/,
    "品牌分销": /distributor|authorized dealer|brand partner|品牌分销|授权经销/,
    "新能源业务": /electric vehicle|electric cars|hybrid|new energy|chinese cars|新能源|电动车|混动/,
    "车队采购": /fleet|procurement|corporate sales|rental|chauffeur|车队|采购|租赁/,
    "批发贸易": /wholesale|bulk sales|import export|trading company|批发|进出口贸易/
  };
  const intentRules = {
    "公开询价": /rfq|request for quotation|公开询价/,
    "正在采购": /looking to buy|want to buy|vehicle procurement|sourcing vehicles|正在采购|求购/,
    "寻找供应商": /supplier wanted|looking for supplier|seeking supplier|寻找供应商/,
    "招募经销商": /dealer wanted|distributor wanted|seeking distributor|招募经销商|招募分销商/,
    "寻求品牌合作": /brand partnership|new brand|distribution opportunity|品牌合作|引入新品牌/,
    "批量采购": /bulk order|fleet purchase|wholesale order|批量采购/
  };
  const roleRules = {
    "老板/创始人": /owner|founder|co-founder|proprietor|ceo|老板|创始人/,
    "总经理": /general manager|managing director|总经理/,
    "采购负责人": /procurement manager|purchasing manager|buyer|sourcing manager|采购经理/,
    "进口负责人": /import manager|import director|进口经理/,
    "销售负责人": /sales director|sales manager|business development manager|销售总监|销售经理/,
    "车队负责人": /fleet manager|fleet director|车队经理/
  };
  const businessSignals = Object.entries(signalRules).filter(([, rule]) => rule.test(value)).map(([label]) => label);
  const intentSignals = Object.entries(intentRules).filter(([, rule]) => rule.test(value)).map(([label]) => label);
  const decisionRole = Object.entries(roleRules).find(([, rule]) => rule.test(value))?.[0] || "";
  const detectedType = decisionRole || String(accountType).includes("个人")
    ? "个人决策人"
    : businessSignals.length || intentSignals.length ? "公司商业账号" : "账号类型待核验";
  return {
    businessSignals,
    intentSignals,
    decisionRole,
    accountType: detectedType,
    isCommercial: Boolean(businessSignals.length || intentSignals.length),
    businessConfidence: Math.min(
      96,
      15 + businessSignals.length * 12 + intentSignals.length * 12 + (decisionRole ? 12 : 0)
    )
  };
}

function captureToLead(capture) {
  const finderData = Object.fromEntries(new FormData($("#finderForm")).entries());
  const country = countries.find((item) => item.name === finderData.country);
  const city = country?.cities?.split(" / ")[0] || "";
  const platformDomains = ["youtube.com", "youtu.be", "facebook.com", "instagram.com", "tiktok.com", "linkedin.com", "threads.net", "pinterest.com"];
  const links = (capture.links || []).filter((item) => safeHttpUrl(item.url));
  const externalWebsite = links.find((item) => {
    try {
      const domain = new URL(item.url).hostname.toLowerCase();
      return !platformDomains.some((platformDomain) => domain.includes(platformDomain));
    } catch {
      return false;
    }
  });
  const socialLinks = links.filter((item) => socialPlatformFromUrl(item.url) !== "官网");
  const sourceUrl = safeHttpUrl(capture.url) || "";
  const screenshotUrl = safeHttpUrl(capture.screenshotUrl) || "";
  const title = String(capture.title || "社媒登录态采集线索")
    .replace(/\s*[-|·]\s*(YouTube|Facebook|Instagram|TikTok|LinkedIn).*$/i, "")
    .trim();
  const socialAnalysis = analyzeSocialBusinessText(
    `${title} ${capture.text || ""}`,
    capture.accountType || ""
  );
  const sourceRecords = [
    sourceUrl ? {
      title: `${title} · ${capture.platform || "社媒页面"}`,
      url: sourceUrl,
      excerpt: String(capture.text || "").slice(0, 700),
      sourceName: `${capture.platform || "社媒"} 登录态页面`,
      sourceType: "登录态当前页面采集",
      reliability: "B",
      reliabilityReason: "由销售人员在已登录页面中主动采集，可回查当前绝对网址"
    } : null,
    screenshotUrl ? {
      title: `${title} · 采集截图`,
      url: screenshotUrl,
      excerpt: "采集时当前浏览器可见区域截图，用于证明弹窗中公开显示的邮箱和链接。",
      sourceName: "本地采集截图",
      sourceType: "登录态可见证据",
      reliability: "B",
      reliabilityReason: "截图由本地Chrome采集器在用户点击时生成"
    } : null
  ].filter(Boolean);
  const emailSources = (capture.emails || []).map((email) => ({
    email,
    sources: [
      sourceUrl ? {
        url: sourceUrl,
        name: `${capture.platform || "社媒"}当前页面`,
        verified: true,
        excerpt: `采集器在当前可见页面中识别到邮箱 ${email}`
      } : null,
      screenshotUrl ? {
        url: screenshotUrl,
        name: "采集截图",
        verified: true,
        excerpt: `采集截图中显示邮箱 ${email}`
      } : null
    ].filter(Boolean)
  }));
  return normalizeLead({
    company: title || "未命名社媒客户",
    country: String(finderData.country || "").split(" ")[0],
    city,
    type: "登录态社媒发现的汽车潜在客户",
    source: sourceUrl,
    origin: capture.platform || "社媒登录态采集",
    sourceType: "Chrome登录态当前页面采集",
    sourceTitle: title,
    sourceUrl,
    sourceExcerpt: String(capture.text || "").slice(0, 1200),
    evidenceSources: sourceRecords,
    customerWebsite: externalWebsite?.url || "",
    email: capture.emails?.[0] || "",
    emailSources,
    phone: capture.phones?.[0] || "",
    phoneSources: (capture.phones || []).map((value) => ({
      value,
      sources: sourceUrl ? [{ url: sourceUrl, name: `${capture.platform || "社媒"}当前页面` }] : []
    })),
    socialAccounts: socialLinks.map((item) => item.url),
    socialProfiles: socialLinks.map((item) => ({
      platform: socialPlatformFromUrl(item.url),
      accountType: socialAnalysis.accountType,
      relationship: "当前登录态页面公开链接",
      title: item.text || title,
      description: "由当前页面公开链接识别",
      url: item.url,
      businessSignals: socialAnalysis.businessSignals,
      intentSignals: socialAnalysis.intentSignals,
      decisionRole: socialAnalysis.decisionRole,
      businessConfidence: socialAnalysis.businessConfidence,
      isCommercial: socialAnalysis.isCommercial,
      handle: (() => {
        try { return new URL(item.url).pathname.replace(/^\/|\/$/g, ""); } catch { return ""; }
      })()
    })),
    accountType: socialAnalysis.accountType,
    socialBusinessSignals: socialAnalysis.businessSignals,
    socialIntentSignals: socialAnalysis.intentSignals,
    socialDecisionRole: socialAnalysis.decisionRole,
    socialBusinessConfidence: socialAnalysis.businessConfidence,
    businessSignals: socialAnalysis.businessSignals,
    intentSignals: socialAnalysis.intentSignals,
    model: finderData.model,
    score: scoreLeadFromText(`${title} ${capture.text || ""}`),
    scoreBasis: "登录态页面初始评分，完成官网核验后重新计算",
    reason: `从${capture.platform || "社媒"}当前可见页面采集到 ${(capture.emails || []).length} 个邮箱、${links.length} 个公开链接。`,
    next: "在线索审核中执行全网补全"
  });
}

async function importSocialCaptures() {
  const status = $("#captureInboxStatus");
  if (!status) return;
  try {
    const response = await fetch("/api/social-captures", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const result = await response.json();
    const captures = Array.isArray(result.captures) ? result.captures : [];
    const seen = new Set(JSON.parse(localStorage.getItem(SOCIAL_CAPTURE_SEEN_KEY) || "[]"));
    let imported = 0;
    [...captures].reverse().forEach((capture) => {
      if (!capture?.id || seen.has(capture.id)) return;
      const lead = captureToLead(capture);
      const duplicate = [...reviewLeads, ...customers].some((item) =>
        String(item.sourceUrl || item.source).toLowerCase().replace(/\/$/, "") ===
        String(lead.sourceUrl || lead.source).toLowerCase().replace(/\/$/, "")
      );
      if (!duplicate) {
        reviewLeads.unshift(lead);
        imported += 1;
      }
      seen.add(capture.id);
    });
    localStorage.setItem(SOCIAL_CAPTURE_SEEN_KEY, JSON.stringify([...seen].slice(-500)));
    if (imported) refreshAllLeadViews();
    status.textContent = imported
      ? `刚导入 ${imported} 条采集线索`
      : captures.length
        ? `采集器已连接 · 共 ${captures.length} 条`
        : "采集器已连接 · 暂无数据";
  } catch {
    status.textContent = "等待 Chrome 采集器";
  }
}

function generateLetter(data) {
  const profile = productProfiles[data.model] || productProfiles["问界 M9"];
  const websiteLower = data.websiteText.toLowerCase();
  const isLuxury = /luxury|premium|range rover|mercedes|bmw|executive/.test(websiteLower);
  const isEv = /ev|electric|hybrid|new energy/.test(websiteLower);
  const isImport = /import|export|trading|dealer|showroom/.test(websiteLower);

  const traits = [];
  if (isLuxury) traits.push("luxury car showroom");
  if (isEv) traits.push("premium EV business");
  if (isImport) traits.push("import/export operation");
  if (!traits.length) traits.push("automotive business");

  const insight = `这家公司官网显示它是${traits.join("、")}，适合推荐${data.model}。系统会把客户官网信息和车型卖点融合，而不是发一封通用群发邮件。`;
  const recipient = data.contactName ? data.contactName : `${data.company} team`;

  const english = data.channel === "Email"
    ? `Subject: Dealer CIF quotation for ${profile.english} from China\n\nHi ${recipient},\n\nI found your website and noticed that you focus on ${traits.join(", ")}. We supply HIMA smart EV models from China, including ${profile.english}.\n\n${profile.english} is ${profile.pitch}. I believe it could be a strong fit for customers looking for premium Chinese smart vehicles.\n\nWould it be relevant for your team to review the available colors, export specifications and a dealer CIF quotation for ${profile.english}?\n\nBest regards`
    : `Hi ${recipient}, I found your website and noticed that you focus on ${traits.join(", ")}.\n\nWe supply HIMA smart EV models from China, including ${profile.english}. It is ${profile.pitch}.\n\nWould it be relevant for your team to review dealer CIF prices, available colors and export specifications for ${profile.english}?`;

  const chinese = `中文意思：我看到你们官网主要做${traits.join("、")}。我们供应中国华为系鸿蒙智行新能源车型，包括${data.model}。这款车的优势是${profile.chinese}。想问你们是否有兴趣了解经销商 CIF 报价、现车颜色和出口细节。`;

  return { insight, english, chinese };
}

function renderQuote(values = {}) {
  const selectedCustomer = values.customer !== "" && values.customer !== undefined
    ? customers[Number(values.customer)]
    : null;
  const customer = selectedCustomer?.company || "未选择客户";
  const model = values.model || "问界 M9";
  const qty = Number(values.qty || 1);
  const price = Number(values.price || modelReferencePrices[model] || 68000);
  const local = Number(values.local || 950);
  const freight = Number(values.freight || 3600);
  const insuranceRate = Number(values.insurance || 0.008);
  const docs = Number(values.docs || 1800);
  const other = Number(values.other || 650);
  const destination = values.destination || "Jebel Ali, UAE";
  const validDays = Number(values.validDays || 7);
  const vehicleTotal = price * qty;
  const localTotal = local * qty;
  const insurance = vehicleTotal * insuranceRate;
  const total = vehicleTotal + localTotal + freight + insurance + docs + other;
  const validUntil = new Date(Date.now() + validDays * 86400000).toLocaleDateString();
  lastQuote = {
    id: `Q-${Date.now().toString(36).toUpperCase()}`,
    customer,
    model,
    qty,
    destination,
    price,
    local,
    freight,
    insurance,
    docs,
    other,
    total,
    validUntil,
    createdAt: new Date().toLocaleString(),
    english: `CIF reference price for ${productProfiles[model]?.english || model}: ${money(total)}. This price does not include destination import duty, VAT, registration fee or local delivery cost.`
  };

  $("#quoteResult").innerHTML = `
    <div class="quote-total-card">
      <span>CIF 参考总价</span>
      <strong>${money(total)}</strong>
      <small>${qty > 1 ? `平均每辆 ${money(total / qty)}` : "到港参考总成本"}</small>
    </div>
    <div class="quote-summary-grid">
      <div><span>车型</span><strong>${escapeHtml(model)}</strong></div>
      <div><span>数量</span><strong>${qty} 辆</strong></div>
      <div class="wide"><span>目的港</span><strong>${escapeHtml(destination)}</strong></div>
      <div class="wide"><span>有效期</span><strong>至 ${escapeHtml(validUntil)}</strong></div>
    </div>
    <div class="quote-cost-head">
      <span>费用构成</span>
      <small>USD</small>
    </div>
    <dl class="quote-cost-list">
      <div><dt>车辆采购</dt><dd>${money(vehicleTotal)}</dd></div>
      <div><dt>国内费用</dt><dd>${money(localTotal)}</dd></div>
      <div><dt>海运费</dt><dd>${money(freight)}</dd></div>
      <div><dt>运输保险</dt><dd>${money(insurance)}</dd></div>
      <div><dt>文件与认证</dt><dd>${money(docs)}</dd></div>
      <div><dt>其他杂费</dt><dd>${money(other)}</dd></div>
    </dl>
    <p class="quote-disclaimer">此结果仅作报价参考，不包含目的国进口关税、VAT、注册及本地交付费用。</p>
  `;
}

function renderQuoteHistory() {
  const box = $("#quoteHistory");
  if (!box) return;
  const count = $("#quoteVersionCount");
  if (count) count.textContent = `${quoteHistory.length} 个版本`;
  box.innerHTML = quoteHistory.length ? quoteHistory.map((quote, index) => `
    <tr>
      <td>V${quoteHistory.length - index}</td>
      <td>${escapeHtml(quote.customer)}</td>
      <td>${escapeHtml(quote.model)}</td>
      <td>${escapeHtml(quote.qty)}</td>
      <td><strong>${money(quote.total)}</strong></td>
      <td>${escapeHtml(quote.validUntil || "未设置")}</td>
      <td>${escapeHtml(quote.createdAt)}</td>
      <td><button class="quote-delete" type="button" data-quote-delete="${index}" aria-label="删除这个报价版本">删除</button></td>
    </tr>
  `).join("") : `<tr><td colspan="8" class="quote-empty">暂无报价版本</td></tr>`;
}

function renderFollowTasks() {
  const box = $("#followTasks");
  if (!box) return;
  const tasks = customers
    .map((lead, index) => ({ lead, index }))
    .filter(({ lead }) => !["已成交", "已流失"].includes(lead.stage))
    .slice(0, 8);
  box.innerHTML = tasks.length ? tasks.map(({ lead, index }) => `
    <article>
      <span>${escapeHtml(lead.stage || "待跟进")}${lead.score >= 75 ? " · A 级优先" : ""}</span>
      <h3>${escapeHtml(lead.company)}</h3>
      <p>建议动作：${escapeHtml(lead.next || `根据客户官网信息生成英文开发信，推荐${lead.model}。`)}</p>
      ${lead.nextFollowAt ? `<small>计划跟进：${escapeHtml(lead.nextFollowAt)}</small>` : ""}
      <div class="task-actions">
        <button type="button" data-follow-action="email" data-index="${index}">写开发信</button>
        ${lead.stage === "准备联系" ? `<button type="button" data-follow-action="contacted" data-index="${index}">标记已联系</button>` : ""}
        <button type="button" data-follow-action="quote" data-index="${index}">进入报价</button>
      </div>
    </article>
  `).join("") : `<p class="empty">暂无今日跟进。线索审核通过后，会自动生成跟进任务。</p>`;
}

function renderKpis() {
  const pending = $("#kpiPending");
  if (!pending) return;
  pending.textContent = reviewLeads.length;
  $("#kpiVerified").textContent = [...reviewLeads, ...customers].filter((lead) => lead.researchAt).length;
  $("#kpiCustomers").textContent = customers.length;
  const contacted = customers.filter((lead) => !["准备联系", "暂缓", "已流失"].includes(lead.stage)).length;
  const replied = customers.filter((lead) => ["有回复", "报价中", "谈判中", "已成交"].includes(lead.stage)).length;
  $("#kpiContacted").textContent = contacted;
  $("#kpiReplied").textContent = replied;
  $("#kpiQuotes").textContent = quoteHistory.length;
  const approvalBase = reviewLeads.length + customers.length;
  const approvalRate = approvalBase ? Math.round(customers.length / approvalBase * 100) : 0;
  const replyRate = contacted ? Math.round(replied / contacted * 100) : 0;
  const nextRecommendation = reviewLeads.some((lead) => !lead.researchAt)
    ? `还有 ${reviewLeads.filter((lead) => !lead.researchAt).length} 条线索未完成全网核验。`
    : customers.some((lead) => lead.stage === "准备联系")
      ? `还有 ${customers.filter((lead) => lead.stage === "准备联系").length} 个客户尚未首次触达。`
      : "当前没有阻塞项，继续新增高质量线索。";
  $("#kpiInsight").innerHTML = `
    <div><span>审核通过率</span><strong>${approvalRate}%</strong></div>
    <div><span>客户回复率</span><strong>${replyRate}%</strong></div>
    <div class="wide"><span>当前最重要动作</span><strong>${escapeHtml(nextRecommendation)}</strong></div>
  `;
}

function bindNavigation() {
  $$("[data-section]").forEach((button) => {
    button.addEventListener("click", () => showSection(button.dataset.section));
  });
}

function showSection(id) {
  $$(".section").forEach((section) => section.classList.toggle("active", section.id === id));
  $$(".nav button").forEach((button) => button.classList.toggle("active", button.dataset.section === id));
  if (window.location.hash !== `#${id}`) {
    history.replaceState(null, "", `#${id}`);
  }
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function discoverySourceLabel(value) {
  return {
    combined: "综合搜索",
    social: "社媒综合",
    google: "Google Maps",
    osm: "OpenStreetMap",
    dealer: "车商官网 / 行业目录",
    instagram: "Instagram",
    facebook: "Facebook",
    tiktok: "TikTok",
    youtube: "YouTube",
    linkedin: "LinkedIn"
  }[value] || value || "综合搜索";
}

function formatJobTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

function renderDiscoveryJobs() {
  const box = $("#discoveryJobList");
  if (!box) return;
  const stateLabels = {
    queued: "排队中",
    running: "运行中",
    completed: "已完成",
    failed: "失败",
    canceled: "已取消"
  };
  const activeJobs = discoveryJobs.filter((job) => ["queued", "running"].includes(job.status));
  const inactiveJobs = discoveryJobs.filter((job) => !["queued", "running"].includes(job.status));
  const collapsedJobs = [
    ...activeJobs,
    ...inactiveJobs.slice(0, Math.max(0, 4 - activeJobs.length))
  ];
  const visibleJobs = discoveryJobsExpanded ? discoveryJobs : collapsedJobs;
  const count = $("#discoveryJobCount");
  if (count) count.textContent = `${discoveryJobs.length} 个任务`;
  const toggle = $("#toggleDiscoveryJobs");
  if (toggle) {
    toggle.hidden = discoveryJobs.length <= collapsedJobs.length;
    toggle.textContent = discoveryJobsExpanded
      ? "收起任务"
      : `展开全部（${discoveryJobs.length}）`;
  }
  box.innerHTML = visibleJobs.length ? visibleJobs.map((job) => {
    const count = Number(job.result?.count || job.result?.leads?.length || 0);
    const canImport = job.status === "completed" && !job.imported && count > 0;
    const canRetry = ["failed", "canceled"].includes(job.status);
    const canCancel = ["queued", "running"].includes(job.status);
    const actionLabel = job.imported
      ? "已导入"
      : canImport
        ? `导入 ${count} 条`
        : canRetry
          ? "重新执行"
          : canCancel
            ? "取消任务"
          : job.status === "completed"
            ? "无新线索"
            : `${Number(job.progress || 0)}%`;
    const actionAttribute = canImport
      ? `data-import-job="${escapeHtml(job.id)}"`
      : canRetry
        ? `data-retry-job="${escapeHtml(job.id)}"`
        : canCancel
          ? `data-cancel-job="${escapeHtml(job.id)}"`
        : "";
    return `
      <article class="discovery-job">
        <div class="discovery-job-main">
          <div class="discovery-job-title">
            <strong>${escapeHtml(job.country || "未指定市场")} · ${escapeHtml(job.model || "未指定车型")}</strong>
            <span>${escapeHtml(discoverySourceLabel(job.sourceMode))}</span>
          </div>
          <div class="discovery-job-meta">
            <span>${escapeHtml(formatJobTime(job.createdAt))}</span>
            ${job.status === "completed" ? `<span>发现 ${count} 条</span>` : ""}
          </div>
          <div class="discovery-job-status">
            <span class="job-state ${escapeHtml(job.status)}">${escapeHtml(stateLabels[job.status] || job.status)}</span>
            <p>${escapeHtml(job.error || job.message || "等待云端处理")}</p>
          </div>
        </div>
        <div class="discovery-job-actions">
          <button class="discovery-job-action" type="button"
            ${actionAttribute} ${canImport || canRetry || canCancel ? "" : "disabled"}>
            ${escapeHtml(actionLabel)}
          </button>
          <button class="discovery-job-delete" type="button"
            data-delete-job="${escapeHtml(job.id)}"
            ${canCancel ? `disabled title="请先取消运行中的任务"` : ""}>
            删除
          </button>
        </div>
      </article>
    `;
  }).join("") : `<p class="empty">暂无云端获客任务。</p>`;
}

async function loadDiscoveryJobs() {
  const response = await fetch("/api/discover/jobs", { cache: "no-store" });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  discoveryJobs = Array.isArray(result.jobs) ? result.jobs : [];
  renderDiscoveryJobs();
  const active = discoveryJobs.find((job) => ["queued", "running"].includes(job.status));
  if (active) {
    setFinderProgress({
      percent: Math.max(5, Number(active.progress || 5)),
      stage: active.stage || "search",
      state: "running",
      title: "已恢复云端获客任务",
      elapsed: "后台持续运行",
      message: active.message || "任务仍在云端执行，可以关闭当前页面。"
    });
  }
  return discoveryJobs;
}

async function markDiscoveryImported(jobId) {
  if (!jobId) return;
  await fetch("/api/discover/mark-imported", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: jobId })
  }).catch(() => undefined);
  await loadDiscoveryJobs().catch(() => undefined);
}

async function retryDiscoveryJob(jobId) {
  const button = document.querySelector(`[data-retry-job="${CSS.escape(jobId)}"]`);
  if (button) {
    button.disabled = true;
    button.textContent = "正在重试";
  }
  try {
    const response = await fetch("/api/discover/retry", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: jobId })
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    await loadDiscoveryJobs();
    setFinderProgress({
      percent: 5,
      stage: "search",
      state: "running",
      title: "失败任务已重新启动",
      elapsed: "后台持续运行",
      message: "新任务已经进入云端执行队列，可关闭页面后稍后回来查看。"
    });
  } catch (error) {
    await loadDiscoveryJobs().catch(() => undefined);
    setFinderProgress({
      percent: 100,
      stage: "done",
      state: "error",
      title: "任务重试失败",
      message: error.message
    });
  }
}

async function cancelDiscoveryJob(jobId) {
  const button = document.querySelector(`[data-cancel-job="${CSS.escape(jobId)}"]`);
  if (button) {
    button.disabled = true;
    button.textContent = "正在取消";
  }
  try {
    const response = await fetch("/api/discover/cancel", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: jobId })
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    await loadDiscoveryJobs();
    setFinderProgress({
      percent: 100,
      stage: "done",
      state: "error",
      title: "任务已取消",
      message: "任务结果将不会写入任务中心。如需继续，可点击“重新执行”。"
    });
  } catch (error) {
    await loadDiscoveryJobs().catch(() => undefined);
    setFinderProgress({
      percent: 100,
      stage: "done",
      state: "error",
      title: "取消任务失败",
      message: error.message
    });
  }
}

async function deleteDiscoveryJob(jobId) {
  if (!jobId || !window.confirm("确定删除这条云端获客任务记录吗？")) return;
  const button = document.querySelector(`[data-delete-job="${CSS.escape(jobId)}"]`);
  if (button) {
    button.disabled = true;
    button.textContent = "删除中";
  }
  try {
    const response = await fetch("/api/discover/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: jobId })
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    await loadDiscoveryJobs();
  } catch (error) {
    await loadDiscoveryJobs().catch(() => undefined);
    setFinderProgress({
      percent: 100,
      stage: "done",
      state: "error",
      title: "任务删除失败",
      message: error.message
    });
  }
}

function mergeDiscoveryResult(result) {
  const found = Array.isArray(result?.leads) ? result.leads : [];
  const existing = new Set(
    [...reviewLeads, ...customers].map((lead) => `${lead.company}|${lead.source}`.toLowerCase())
  );
  const fresh = found
    .map(normalizeLead)
    .filter((lead) => !existing.has(`${lead.company}|${lead.source}`.toLowerCase()));
  if (fresh.length) {
    reviewLeads = [...fresh, ...reviewLeads];
    refreshAllLeadViews();
  }
  return { found, fresh };
}

async function importDiscoveryJob(jobId) {
  const button = document.querySelector(`[data-import-job="${CSS.escape(jobId)}"]`);
  if (button) {
    button.disabled = true;
    button.textContent = "正在导入";
  }
  try {
    const response = await fetch(`/api/discover/status?${new URLSearchParams({ id: jobId })}`, {
      cache: "no-store"
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    const merged = mergeDiscoveryResult(result.job?.result || {});
    await markDiscoveryImported(jobId);
    setFinderProgress({
      percent: 100,
      stage: "done",
      state: "complete",
      title: `已导入 ${merged.fresh.length} 条新线索`,
      message: merged.fresh.length
        ? "任务结果已进入线索审核，并已同步到云端客户数据。"
        : "任务结果中的线索已存在，没有重复导入。"
    });
  } catch (error) {
    setFinderProgress({
      percent: 100,
      stage: "done",
      state: "error",
      title: "任务结果导入失败",
      message: error.message
    });
    await loadDiscoveryJobs().catch(() => undefined);
  }
}

async function runCloudDiscovery(data, words, onProgress) {
  const startResponse = await fetch("/api/discover/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      goal: data.goal,
      country: data.country,
      model: data.model,
      sourceMode: data.sourceMode,
      accountScope: data.accountScope,
      freshness: data.freshness,
      keywords: words.join(" | ")
    })
  });
  const startResult = await startResponse.json().catch(() => ({}));
  if (!startResponse.ok || !startResult.ok || !startResult.job?.id) {
    throw new Error(startResult.error || `云端任务创建失败（HTTP ${startResponse.status}）`);
  }
  if (typeof onProgress === "function" && startResult.job.reused) {
    onProgress({
      ...startResult.job,
      message: "检测到相同搜索正在运行，已接入现有任务，未重复创建。"
    });
  }

  const deadline = Date.now() + 12 * 60 * 1000;
  let consecutiveReadErrors = 0;
  while (Date.now() < deadline) {
    await new Promise((resolve) => setTimeout(resolve, document.hidden ? 5000 : 1800));
    let statusResponse;
    let statusResult;
    try {
      statusResponse = await fetch(`/api/discover/status?${new URLSearchParams({
        id: startResult.job.id
      })}`, { cache: "no-store" });
      statusResult = await statusResponse.json().catch(() => ({}));
      if (!statusResponse.ok || !statusResult.ok) {
        throw new Error(statusResult.error || `HTTP ${statusResponse.status}`);
      }
      consecutiveReadErrors = 0;
    } catch (error) {
      consecutiveReadErrors += 1;
      if (statusResponse?.status === 401 || consecutiveReadErrors >= 5) {
        const statusError = new Error(`连续无法读取云端任务状态：${error.message}`);
        statusError.code = "JOB_STATUS_UNAVAILABLE";
        throw statusError;
      }
      if (typeof onProgress === "function") {
        onProgress({
          status: "running",
          stage: "search",
          progress: Math.min(90, 12 + consecutiveReadErrors * 3),
          message: `网络短暂中断，正在第 ${consecutiveReadErrors} 次重新连接任务。`
        });
      }
      continue;
    }
    const job = statusResult.job || {};
    if (typeof onProgress === "function") onProgress(job);
    if (job.status === "completed") {
      return { ...(job.result || { ok: true, leads: [], count: 0 }), __jobId: job.id };
    }
    if (job.status === "failed") throw new Error(job.error || job.message || "云端搜索失败");
    if (job.status === "canceled") {
      const canceledError = new Error("云端搜索任务已取消");
      canceledError.code = "JOB_CANCELED";
      throw canceledError;
    }
  }
  const timeoutError = new Error("页面等待已超过 12 分钟，任务仍在云端后台运行。");
  timeoutError.code = "JOB_WAIT_TIMEOUT";
  throw timeoutError;
}

function bindForms() {
  $("#toggleDiscoveryJobs")?.addEventListener("click", () => {
    discoveryJobsExpanded = !discoveryJobsExpanded;
    renderDiscoveryJobs();
  });

  $("#refreshDiscoveryJobs")?.addEventListener("click", () => {
    loadDiscoveryJobs().catch((error) => {
      $("#discoveryJobList").innerHTML = `<p class="empty">任务读取失败：${escapeHtml(error.message)}</p>`;
    });
  });

  $("#discoveryJobList")?.addEventListener("click", (event) => {
    const importButton = event.target.closest("[data-import-job]");
    if (importButton && !importButton.disabled) importDiscoveryJob(importButton.dataset.importJob);
    const retryButton = event.target.closest("[data-retry-job]");
    if (retryButton && !retryButton.disabled) retryDiscoveryJob(retryButton.dataset.retryJob);
    const cancelButton = event.target.closest("[data-cancel-job]");
    if (cancelButton && !cancelButton.disabled) cancelDiscoveryJob(cancelButton.dataset.cancelJob);
    const deleteButton = event.target.closest("[data-delete-job]");
    if (deleteButton && !deleteButton.disabled) deleteDiscoveryJob(deleteButton.dataset.deleteJob);
  });

  $("#countryGrid").addEventListener("click", (event) => {
    const card = event.target.closest("[data-country]");
    if (card) chooseMarket(card.dataset.country);
  });

  $("#countryGrid").addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    const card = event.target.closest("[data-country]");
    if (!card) return;
    event.preventDefault();
    chooseMarket(card.dataset.country);
  });

  $("#finderForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const submitButton = event.currentTarget.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = "正在搜索并自动核验…";
    const data = Object.fromEntries(new FormData(event.currentTarget).entries());
    const words = generateKeywords(data.goal, data.country, data.model);
    renderKeywords(words);
    const searchProgress = startFinderSearchProgress();
    runCloudDiscovery(data, words, (job) => {
      setFinderStatus(job.message || "云端正在检索公开商业来源，无需启动本地工作台。");
      loadDiscoveryJobs().catch(() => undefined);
    })
      .then(async (result) => {
        const elapsedSeconds = searchProgress.stop();
        const { found, fresh } = mergeDiscoveryResult(result);
        if (!found.length) {
          await markDiscoveryImported(result.__jobId);
          setFinderProgress({
            percent: 100,
            stage: "done",
            state: "complete",
            title: "本轮搜索已完成",
            elapsed: `用时 ${elapsedSeconds} 秒`,
            message: result.notice || "没有抓到新线索。可以换国家、城市或更具体的关键词再试。"
          });
          return;
        }
        const sourceLabel = discoverySourceLabel(data.sourceMode);
        const freshnessLabel = data.freshness === "all" ? "不限时间" : `最近 ${data.freshness} 天`;
        setFinderProgress({
          percent: 62,
          stage: "verify",
          title: `已发现 ${found.length} 条线索`,
          elapsed: `搜索用时 ${elapsedSeconds} 秒`,
          message: `${sourceLabel} · ${freshnessLabel}：其中 ${fresh.length} 条为新线索，开始自动全网核验。`
        });
        if (!fresh.length) {
          await markDiscoveryImported(result.__jobId);
          setFinderProgress({
            percent: 100,
            stage: "done",
            state: "complete",
            title: "本轮搜索已完成",
            elapsed: `用时 ${elapsedSeconds} 秒`,
            message: `${sourceLabel} · ${freshnessLabel}：发现的 ${found.length} 条线索均已存在，没有重复入库。`
          });
          return;
        }
        await markDiscoveryImported(result.__jobId);
        setFinderProgress({
          percent: 100,
          stage: "done",
          state: "complete",
          title: `已新增 ${fresh.length} 条待审核线索`,
          elapsed: `总用时 ${elapsedSeconds} 秒`,
          message: `${sourceLabel} · ${freshnessLabel}：线索已保存。请进入“线索审核”，按评分从高到低查看；需要更完整的邮箱、联系人和多来源证据时，再执行全网核验。`
        });
      })
      .catch((error) => {
        const elapsedSeconds = searchProgress.stop();
        const backgroundOnly = ["JOB_WAIT_TIMEOUT", "JOB_STATUS_UNAVAILABLE"].includes(error.code);
        const canceled = error.code === "JOB_CANCELED";
        setFinderProgress({
          percent: backgroundOnly ? 80 : 100,
          stage: backgroundOnly ? "verify" : "done",
          state: backgroundOnly ? "running" : canceled ? "complete" : "error",
          title: backgroundOnly
            ? "任务仍在后台执行"
            : canceled
              ? "任务已取消"
              : "本轮获客失败",
          elapsed: `用时 ${elapsedSeconds} 秒`,
          message: backgroundOnly
            ? `${error.message} 请稍后在“云端获客任务”中刷新查看，避免重复发起相同搜索。`
            : canceled
              ? "任务已停止接收搜索结果，可从任务中心重新执行。"
              : `云端实时获客失败：${error.message}。请稍后重试，不需要启动本地 BAT。`
        });
      })
      .finally(() => {
        searchProgress.stop();
        submitButton.disabled = false;
        submitButton.textContent = "一键获客到待审核";
      });
    showSection("lead-finder");
  });

  $("#finderForm").addEventListener("input", updateSocialProspectingQueries);
  $("#finderForm").addEventListener("change", updateSocialProspectingQueries);
  $(".social-search-box").addEventListener("click", (event) => {
    const link = event.target.closest("[data-social-platform]");
    if (link) $("#socialLeadForm").platform.value = link.dataset.socialPlatform;
  });

  $("#socialLeadForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget).entries());
    const url = safeHttpUrl(data.pageUrl);
    const domain = url ? new URL(url).hostname.toLowerCase() : "";
    const expectedDomains = {
      Facebook: "facebook.com",
      Instagram: "instagram.com",
      TikTok: "tiktok.com",
      YouTube: "youtube.com",
      LinkedIn: "linkedin.com"
    };
    const expectedDomain = expectedDomains[data.platform] || "";
    const status = $("#socialLeadStatus");
    if (!url || !domain.includes(expectedDomain)) {
      status.textContent = `网址必须是有效的 ${data.platform} 主页绝对地址。`;
      status.classList.add("error");
      return;
    }
    const finderData = Object.fromEntries(new FormData($("#finderForm")).entries());
    const country = countries.find((item) => item.name === finderData.country);
    const city = country?.cities?.split(" / ")[0] || "";
    const notes = String(data.notes || "").trim();
    const socialAnalysis = analyzeSocialBusinessText(`${data.company} ${notes}`, data.accountType);
    const lead = normalizeLead({
      company: data.company,
      country: String(finderData.country || "").split(" ")[0],
      city,
      type: data.accountType === "个人决策人" ? "公开个人决策人" : "社媒发现的汽车潜在客户",
      source: url,
      origin: data.platform,
      sourceType: "Chrome 登录态人工发现",
      sourceTitle: `${data.company} · ${data.platform}`,
      sourceUrl: url,
      sourceExcerpt: notes || "销售人员在已登录的社媒页面中人工发现，等待全网核验。",
      evidenceSources: [{
        title: `${data.company} · ${data.platform}`,
        url,
        excerpt: notes || "登录态人工发现的公开主页，需在线索审核中继续核验。",
        sourceName: data.platform,
        sourceType: "社交媒体公开主页",
        reliability: "C",
        reliabilityReason: "人工发现的公开社媒主页，尚未与企业官网交叉验证"
      }],
      socialAccounts: [url],
      socialProfiles: [{
        platform: data.platform,
        accountType: socialAnalysis.accountType,
        relationship: "Chrome 登录态人工发现",
        title: data.company,
        description: notes || "等待全网核验",
        url,
        handle: new URL(url).pathname.replace(/^\/|\/$/g, ""),
        ...socialAnalysis
      }],
      accountType: socialAnalysis.accountType,
      socialBusinessSignals: socialAnalysis.businessSignals,
      socialIntentSignals: socialAnalysis.intentSignals,
      socialDecisionRole: socialAnalysis.decisionRole,
      socialBusinessConfidence: socialAnalysis.businessConfidence,
      businessSignals: socialAnalysis.businessSignals,
      intentSignals: socialAnalysis.intentSignals,
      model: finderData.model,
      score: scoreLeadFromText(`${data.company} ${notes}`),
      scoreBasis: "社媒人工发现初始评分，完成官网核验后重新计算",
      reason: notes || `${data.platform} 公开主页发现的潜在客户，需核对官网业务和联系方式。`,
      next: "在线索审核中执行全网补全"
    });
    const duplicate = [...reviewLeads, ...customers].some((item) =>
      String(item.sourceUrl || item.source).toLowerCase().replace(/\/$/, "") === url.toLowerCase().replace(/\/$/, "")
    );
    if (duplicate) {
      status.textContent = "该主页已经存在，没有重复保存。";
      status.classList.add("error");
      return;
    }
    reviewLeads.unshift(lead);
    refreshAllLeadViews();
    event.currentTarget.reset();
    status.classList.remove("error");
    status.textContent = `已保存 ${data.company}，请到线索审核执行全网补全。`;
  });

  $("#emailForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget).entries());
    const result = generateLetter(data);
    $("#leadInsight").textContent = result.insight;
    $("#englishLetter").textContent = result.english;
    $("#chineseMeaning").textContent = result.chinese;
  });

  $("#fillLeadFromCrm").addEventListener("click", () => {
    const index = Number($("#leadSelect").value || 0);
    if (!customers[index]) return;
    openCustomerInEmail(index);
    const form = $("#emailForm");
    const result = generateLetter(Object.fromEntries(new FormData(form).entries()));
    $("#leadInsight").textContent = result.insight;
    $("#englishLetter").textContent = result.english;
    $("#chineseMeaning").textContent = result.chinese;
  });

  $("#leadForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget).entries());
    const website = data.website || `${data.company} ${data.type} ${data.country}`;
    const score = scoreLeadFromText(`${data.company} ${data.type} ${data.country} ${website}`);
    const lead = {
      company: data.company,
      country: data.country,
      city: data.city,
      type: data.type,
      source: data.source || "Website",
      model: data.model,
      score,
      stage: score >= 75 ? "准备联系" : "待审核",
      next: data.next || "发送首次开发信",
      website,
      reason: `${data.city} 的${data.type}，官网信息显示：${website.slice(0, 90)}。适合推荐${data.model}。`
    };
    reviewLeads.unshift(normalizeLead(lead));
    event.currentTarget.reset();
    refreshAllLeadViews();
    showSection("review");
  });

  $("#reviewGrid").addEventListener("click", (event) => {
    const adjustmentButton = event.target.closest("[data-score-adjust]");
    if (adjustmentButton) {
      calibrateLeadScore(
        Number(adjustmentButton.dataset.index),
        Number(adjustmentButton.dataset.scoreAdjust)
      );
      return;
    }
    const resetButton = event.target.closest("[data-score-reset]");
    if (resetButton) {
      calibrateLeadScore(Number(resetButton.dataset.index), 0, true);
      return;
    }
    const researchButton = event.target.closest("[data-research-index]");
    if (researchButton) {
      researchLead(Number(researchButton.dataset.researchIndex));
      return;
    }
    const button = event.target.closest("[data-review-action]");
    if (!button) return;
    const index = Number(button.dataset.index);
    if (button.dataset.reviewAction === "approve") approveLead(index);
    if (button.dataset.reviewAction === "reject") rejectLead(index);
  });

  $("#copyEmail").addEventListener("click", async () => {
    const text = $("#englishLetter").textContent.trim();
    if (!text) return;
    await navigator.clipboard.writeText(text);
    $("#copyEmail").textContent = "已复制";
    setTimeout(() => {
      $("#copyEmail").textContent = "复制英文";
    }, 1200);
  });

  $("#quoteForm").addEventListener("submit", (event) => {
    event.preventDefault();
    renderQuote(Object.fromEntries(new FormData(event.currentTarget).entries()));
  });

  $("#quoteModel").addEventListener("change", (event) => {
    $("#quotePrice").value = modelReferencePrices[event.target.value] || 0;
    renderQuote(Object.fromEntries(new FormData($("#quoteForm")).entries()));
  });

  $("#quoteCustomer").addEventListener("change", (event) => {
    if (event.target.value === "") return;
    applyCustomerToQuote(Number(event.target.value));
  });

  $("#saveQuote").addEventListener("click", () => {
    if ($("#quoteCustomer").value === "") {
      const button = $("#saveQuote");
      button.textContent = "请先选择客户";
      setTimeout(() => { button.textContent = "保存报价版本"; }, 1400);
      return;
    }
    renderQuote(Object.fromEntries(new FormData($("#quoteForm")).entries()));
    quoteHistory.unshift({ ...lastQuote });
    const customerIndex = Number($("#quoteCustomer").value);
    const customer = customers[customerIndex];
    if (customer && !["谈判中", "已成交"].includes(customer.stage)) {
      customer.stage = "报价中";
      customer.next = "发送报价并确认客户对价格、配置和交期的反馈";
    }
    saveState();
    renderQuoteHistory();
    renderCrm();
    renderFollowTasks();
    renderKpis();
  });

  $("#researchAllLeads").addEventListener("click", researchAllLeads);

  $("#crmRows").addEventListener("change", (event) => {
    if (event.target.matches("[data-crm-stage]")) {
      updateCustomerStage(Number(event.target.dataset.crmStage), event.target.value);
      return;
    }
    if (event.target.matches("[data-crm-next]")) {
      const lead = customers[Number(event.target.dataset.crmNext)];
      if (!lead) return;
      lead.next = event.target.value.trim();
      saveState();
      renderFollowTasks();
      renderKpis();
    }
  });

  $("#crmRows").addEventListener("click", (event) => {
    const button = event.target.closest("[data-crm-action]");
    if (!button) return;
    const index = Number(button.dataset.index);
    if (button.dataset.crmAction === "email") openCustomerInEmail(index);
    if (button.dataset.crmAction === "quote") openCustomerInQuote(index);
  });

  $("#followTasks").addEventListener("click", (event) => {
    const button = event.target.closest("[data-follow-action]");
    if (!button) return;
    const index = Number(button.dataset.index);
    if (button.dataset.followAction === "email") openCustomerInEmail(index);
    if (button.dataset.followAction === "quote") openCustomerInQuote(index);
    if (button.dataset.followAction === "contacted") updateCustomerStage(index, "已联系");
  });

  $("#riskCountry").addEventListener("change", (event) => renderRiskProfile(event.target.value));

  $("#quoteHistory").addEventListener("click", (event) => {
    const button = event.target.closest("[data-quote-delete]");
    if (!button) return;
    const index = Number(button.dataset.quoteDelete);
    const quote = quoteHistory[index];
    if (!quote) return;
    if (!confirm(`确认删除 ${quote.customer || "未选择客户"} 的 ${quote.model || ""} 报价版本吗？`)) return;
    quoteHistory.splice(index, 1);
    saveState();
    renderQuoteHistory();
    renderKpis();
  });

  $("#exportCustomerTable").addEventListener("click", exportCustomersCsv);

  $("#exportData").addEventListener("click", () => {
    const text = JSON.stringify({ reviewLeads, customers, rejectedLeads, quotes: quoteHistory }, null, 2);
    downloadFile(
      text,
      `huawei-ev-leads-${new Date().toISOString().slice(0, 10)}.json`,
      "application/json;charset=utf-8"
    );
  });

  $("#clearSavedData").addEventListener("click", () => {
    if (!confirm("确认清空待审核线索、客户池、拒绝记录和报价吗？")) return;
    localStorage.removeItem(STORAGE_KEY);
    reviewLeads = [];
    customers = [];
    rejectedLeads = [];
    quoteHistory = [];
    refreshAllLeadViews();
  });

}

function renderDefaultLetter() {
  $("#leadInsight").textContent = "客户池有客户后，可以从下拉框选择客户并自动生成开发信。";
  $("#englishLetter").textContent = "";
  $("#chineseMeaning").textContent = "暂无客户。请先一键获客、审核通过，再生成开发信。";
}

function renderBeijingGreeting() {
  const now = new Date();
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat("en-US", {
      timeZone: "Asia/Shanghai",
      year: "numeric",
      month: "numeric",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hourCycle: "h23"
    }).formatToParts(now).map((part) => [part.type, part.value])
  );
  const weekday = new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    weekday: "long"
  }).format(now);
  const hour = Number(parts.hour);
  let greeting = "晚上好";
  if (hour >= 5 && hour < 11) greeting = "早上好";
  else if (hour >= 11 && hour < 13) greeting = "中午好";
  else if (hour >= 13 && hour < 18) greeting = "下午好";
  $("#timeGreeting").textContent = greeting;
  $("#beijingDate").textContent =
    `${parts.year}年${parts.month}月${parts.day}日 · ${weekday} · ` +
    `${parts.hour}:${parts.minute}:${parts.second} · 北京时间`;
}

async function init() {
  await hydrateCloudState();
  window.__workbenchInitErrors = [];
  const startupSteps = [
    ["北京时间", renderBeijingGreeting],
    ["市场", renderCountries],
    ["关键词", renderKeywords],
    ["线索", renderLeads],
    ["审核", renderReview],
    ["客户池", renderCrm],
    ["开发信", renderDefaultLetter],
    ["报价", renderQuote],
    ["报价历史", renderQuoteHistory],
    ["报价客户", renderQuoteCustomerSelect],
    ["跟进", renderFollowTasks],
    ["风险", renderRiskProfile],
    ["KPI", renderKpis],
    ["导航", bindNavigation],
    ["表单", bindForms]
  ];
  startupSteps.forEach(([name, callback]) => {
    try {
      callback();
    } catch (error) {
      window.__workbenchInitErrors.push({ name, message: error.message });
      console.error(`Workbench module failed: ${name}`, error);
    }
  });
  setInterval(renderBeijingGreeting, 1_000);
  loadDiscoveryJobs().catch((error) => {
    if ($("#discoveryJobList")) {
      $("#discoveryJobList").innerHTML = `<p class="empty">任务读取失败：${escapeHtml(error.message)}</p>`;
    }
  });
  discoveryJobsTimer = window.setInterval(() => {
    loadDiscoveryJobs().catch(() => undefined);
  }, 5_000);
  window.addEventListener("online", () => {
    hydrateCloudState(true).catch(() => undefined);
  });
  window.setInterval(() => {
    if (!cloudStateReady && navigator.onLine) {
      hydrateCloudState(true).catch(() => undefined);
    }
  }, 30_000);
  updateSocialProspectingQueries();
  importSocialCaptures();
  setInterval(importSocialCaptures, 4_000);
  const requestedSection = window.location.hash.slice(1);
  if (requestedSection && document.getElementById(requestedSection)?.classList.contains("section")) {
    showSection(requestedSection);
  }
  const logoutButton = document.getElementById("logoutButton");
  if (logoutButton) {
    logoutButton.addEventListener("click", async () => {
      logoutButton.disabled = true;
      try {
        await fetch("/api/logout", { method: "POST" });
      } finally {
        window.location.replace("/login.html");
      }
    });
  }
}

init();
