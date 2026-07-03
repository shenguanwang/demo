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

const IRRELEVANT_REVIEW_LEAD_DOMAINS = [
  "cgtn.com",
  "cgtnamerica.com",
  "cnn.com",
  "bbc.com",
  "bbc.co.uk",
  "reuters.com",
  "apnews.com",
  "aljazeera.com",
  "bloomberg.com"
];

const NON_CUSTOMER_WEBSITE_DOMAINS = [
  "ggpht.com",
  "ytimg.com",
  "iytimg.com",
  "googleusercontent.com",
  "gstatic.com",
  "googlevideo.com"
];

const IRRELEVANT_REVIEW_LEAD_PATTERNS = [
  /\bcgtn\b/i,
  /china global television/i,
  /\bnews\b/i,
  /\bnewsroom\b/i,
  /\bjournalist\b/i,
  /\bnewspaper\b/i,
  /\bmagazine\b/i,
  /\bmedia outlet\b/i,
  /\bpress agency\b/i,
  /\bbroadcast(ing|er)?\b/i,
  /\btelevision network\b/i,
  /\btv network\b/i,
  /\bpublic radio\b/i,
  /\bradio station\b/i,
  /\bcurrent affairs\b/i,
  /\bworld news\b/i,
  /\bbreaking news\b/i
];

function leadHostname(value) {
  try {
    const raw = String(value || "").trim();
    if (!raw) return "";
    return new URL(/^https?:\/\//i.test(raw) ? raw : `https://${raw}`).hostname.replace(/^www\./, "").toLowerCase();
  } catch {
    return "";
  }
}

function isNonCustomerWebsiteUrl(value) {
  const raw = String(value || "").toLowerCase();
  const hostname = leadHostname(value);
  if (!hostname) return false;
  return (
    raw.includes("window.ytplayer")
    || raw.includes("ytplayer")
    || NON_CUSTOMER_WEBSITE_DOMAINS.some((domain) => hostname === domain || hostname.endsWith(`.${domain}`))
  );
}

function sanitizeCustomerWebsite(value) {
  return isNonCustomerWebsiteUrl(value) ? "" : String(value || "").trim();
}

function isBlockedLeadDomain(value) {
  const hostname = leadHostname(value);
  if (!hostname) return false;
  return IRRELEVANT_REVIEW_LEAD_DOMAINS.some((domain) => (
    hostname === domain || hostname.endsWith(`.${domain}`)
  ));
}

function isIrrelevantReviewLead(lead) {
  const evidenceSources = Array.isArray(lead?.evidenceSources) ? lead.evidenceSources : [];
  const socialProfiles = Array.isArray(lead?.socialProfiles) ? lead.socialProfiles : [];
  const urls = [
    lead?.customerWebsite,
    lead?.sourceUrl,
    lead?.source,
    ...evidenceSources.map((item) => item?.url),
    ...socialProfiles.map((item) => item?.url)
  ];
  if (urls.some(isBlockedLeadDomain)) return true;

  const text = [
    lead?.company,
    lead?.type,
    lead?.sourceTitle,
    lead?.sourceExcerpt,
    lead?.researchSummary,
    lead?.origin,
    lead?.sourceType,
    lead?.discoverySource,
    lead?.sourceTranslation,
    ...evidenceSources.flatMap((item) => [item?.title, item?.excerpt, item?.sourceName, item?.sourceType]),
    ...socialProfiles.flatMap((item) => [item?.name, item?.title, item?.description])
  ].filter(Boolean).join(" ");

  return IRRELEVANT_REVIEW_LEAD_PATTERNS.some((pattern) => pattern.test(text));
}

function filterReviewLeadsForBusinessFit(leads) {
  return (Array.isArray(leads) ? leads : []).filter((lead) => !isIrrelevantReviewLead(lead));
}

function purgeIrrelevantReviewLeads() {
  const keptLeads = filterReviewLeadsForBusinessFit(reviewLeads);
  if (keptLeads.length === reviewLeads.length) return false;
  reviewLeads = keptLeads;
  reviewSelectedIds = new Set([...reviewSelectedIds].filter((id) => reviewLeads.some((lead) => lead.id === id)));
  if (selectedReviewLeadId && !reviewLeads.some((lead) => String(lead.id) === selectedReviewLeadId)) {
    selectedReviewLeadId = "";
  }
  saveState();
  return true;
}

const savedState = loadSavedState();
let reviewLeads = savedState.reviewLeads;
let customers = savedState.customers;
let rejectedLeads = savedState.rejectedLeads;
let quoteHistory = savedState.quotes;
let afterSalesOrders = savedState.afterSalesOrders;
let deletedRecords = savedState.deletedRecords;
let lastQuote = null;
let cloudStateReady = false;
let cloudStateVersion = Number(savedState._cloudVersion || 0);
let localStateDirty = Boolean(savedState._cloudDirty);
let cloudHydrating = false;
let cloudSaveTimer = null;
let cloudSaveChain = Promise.resolve();
let discoveryJobs = [];
let discoveryJobsTimer = null;
let discoveryJobPage = 1;
const DISCOVERY_JOBS_PAGE_SIZE = 4;
let discoverySchedules = [];
let discoverySchedulePage = 1;
const DISCOVERY_SCHEDULES_PAGE_SIZE = 4;
let finderHistoryPage = 1;
const FINDER_HISTORY_PAGE_SIZE = 18;
let activeDiscoveryJobFilter = "all";
let reviewSelectedIds = new Set();
let selectedReviewLeadId = "";
let editingReviewLeadId = "";
let currentSession = null;
let adminKpiSnapshot = null;
let adminKpiLoading = false;
let crmViewFilter = "all";
let navigationBound = false;

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

function evidenceValues(records, fallback = "") {
  const values = [];
  if (Array.isArray(records)) {
    records.forEach((record) => {
      const value = String(record?.value || "").trim();
      if (value) values.push(value);
    });
  }
  if (fallback) values.push(String(fallback).trim());
  const seen = new Set();
  return values.filter((value) => {
    const key = value.replace(/\D/g, "") || value.toLowerCase();
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function renderContactSummary(lead) {
  const phones = evidenceValues(lead.phoneSources, lead.phone);
  const whatsapps = evidenceValues(lead.whatsappSources, lead.whatsapp)
    .filter((value) => !phones.some((phone) => (phone.replace(/\D/g, "") || phone) === (value.replace(/\D/g, "") || value)));
  const rows = [
    ...phones.map((value) => ({ label: "电话", value })),
    ...whatsapps.map((value) => ({ label: "WhatsApp", value })),
  ];
  if (!rows.length) return escapeHtml("未发现");
  return `<div class="contact-summary-list">${rows.map((row) => `
    <span><b>${escapeHtml(row.label)}</b>${escapeHtml(row.value)}</span>
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
    button.textContent = "客户池暂无客户";
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
    afterSalesOrders: [],
    deletedRecords: [],
    ownerUsername: "",
    _cloudVersion: 0,
    _cloudDirty: false
  };
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw);
    return {
      reviewLeads: filterReviewLeadsForBusinessFit(parsed.reviewLeads),
      customers: Array.isArray(parsed.customers) ? parsed.customers : [],
      rejectedLeads: Array.isArray(parsed.rejectedLeads) ? parsed.rejectedLeads : [],
      quotes: Array.isArray(parsed.quotes) ? parsed.quotes : [],
      afterSalesOrders: Array.isArray(parsed.afterSalesOrders) ? parsed.afterSalesOrders : [],
      deletedRecords: Array.isArray(parsed.deletedRecords) ? parsed.deletedRecords : [],
      ownerUsername: String(parsed.ownerUsername || ""),
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
    quotes: quoteHistory,
    afterSalesOrders,
    deletedRecords
  };
}

function persistLocalState(dirty = localStateDirty) {
  localStateDirty = dirty;
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    ...workspaceStateSnapshot(),
    ownerUsername: currentSession?.username || "",
    _cloudVersion: cloudStateVersion,
    _cloudDirty: localStateDirty
  }));
}

function recordIdentity(record, type) {
  if (type === "deletedRecords") return `deleted:${record?.key || ""}`;
  if (type === "quotes") {
    if (record?.id) return `quotes:id:${record.id}`;
    return `${type}:${record?.customer || ""}|${record?.model || ""}|${record?.createdAt || ""}`;
  }
  if (type === "afterSalesOrders") {
    if (record?.id) return `afterSalesOrders:id:${record.id}`;
    return `${type}:${record?.orderNo || ""}|${record?.customer || ""}|${record?.vin || ""}|${record?.createdAt || ""}`.toLowerCase();
  }
  if (record?.id) return `lead:id:${record.id}`;
  return `lead:${record?.company || ""}|${record?.country || ""}|${
    record?.customerWebsite || record?.sourceUrl || record?.source || ""
  }`.toLowerCase();
}

function rememberDeletedRecord(record, type) {
  const key = recordIdentity(record, type);
  if (!key || deletedRecords.some((item) => item.key === key)) return;
  deletedRecords.unshift({
    key,
    type,
    deletedAt: new Date().toISOString()
  });
  deletedRecords = deletedRecords.slice(0, 10_000);
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
  const mergedDeletedRecords = mergeRecordLists(
    remoteState?.deletedRecords,
    localState?.deletedRecords,
    "deletedRecords"
  );
  const deletedKeys = new Set(mergedDeletedRecords.map((record) => record.key));
  const merged = {
    reviewLeads: mergeRecordLists(remoteState?.reviewLeads, localState?.reviewLeads, "reviewLeads")
      .filter((record) => !deletedKeys.has(recordIdentity(record, "reviewLeads")))
      .filter((record) => !isIrrelevantReviewLead(record)),
    customers: mergeRecordLists(remoteState?.customers, localState?.customers, "customers")
      .filter((record) => !deletedKeys.has(recordIdentity(record, "customers"))),
    rejectedLeads: mergeRecordLists(remoteState?.rejectedLeads, localState?.rejectedLeads, "rejectedLeads")
      .filter((record) => !deletedKeys.has(recordIdentity(record, "rejectedLeads"))),
    quotes: mergeRecordLists(remoteState?.quotes, localState?.quotes, "quotes")
      .filter((record) => !deletedKeys.has(recordIdentity(record, "quotes"))),
    afterSalesOrders: mergeRecordLists(remoteState?.afterSalesOrders, localState?.afterSalesOrders, "afterSalesOrders")
      .filter((record) => !deletedKeys.has(recordIdentity(record, "afterSalesOrders"))),
    deletedRecords: mergedDeletedRecords
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
  deletedRecords = Array.isArray(state?.deletedRecords) ? state.deletedRecords : [];
  const deletedKeys = new Set(deletedRecords.map((record) => record.key));
  reviewLeads = Array.isArray(state?.reviewLeads)
    ? filterReviewLeadsForBusinessFit(state.reviewLeads)
        .filter((record) => !deletedKeys.has(recordIdentity(record, "reviewLeads")))
        .map(normalizeLead)
    : [];
  customers = Array.isArray(state?.customers)
    ? state.customers.filter((record) => !deletedKeys.has(recordIdentity(record, "customers"))).map(normalizeLead)
    : [];
  rejectedLeads = Array.isArray(state?.rejectedLeads)
    ? state.rejectedLeads.filter((record) => !deletedKeys.has(recordIdentity(record, "rejectedLeads"))).map(normalizeLead)
    : [];
  quoteHistory = Array.isArray(state?.quotes)
    ? state.quotes.filter((record) => !deletedKeys.has(recordIdentity(record, "quotes")))
    : [];
  afterSalesOrders = Array.isArray(state?.afterSalesOrders)
    ? state.afterSalesOrders.filter((record) => !deletedKeys.has(recordIdentity(record, "afterSalesOrders"))).map(normalizeAfterSalesOrder)
    : [];
  persistLocalState(localStateDirty);
  if (render) {
    renderLeads();
    renderReview();
    renderCrm();
    renderFollowTasks();
    renderKpis();
    renderQuoteHistory();
    renderQuoteCustomerSelect();
    renderAfterSales();
  }
}

function setCloudSyncStatus(text, state = "syncing") {
  const status = $("#cloudSyncStatus");
  if (!status) return;
  status.dataset.syncState = state;
  const label = status.querySelector("span");
  if (label) label.textContent = text;
}

class AuthenticationExpiredError extends Error {
  constructor() {
    super("登录状态已失效，正在跳转登录");
    this.name = "AuthenticationExpiredError";
  }
}

function redirectToLogin() {
  const returnTo = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  window.location.replace(`/login.html?next=${encodeURIComponent(returnTo)}`);
}

async function apiFetch(input, init) {
  const response = await fetch(input, init);
  if (response.status === 401) {
    redirectToLogin();
    throw new AuthenticationExpiredError();
  }
  return response;
}

async function pushCloudState(state = workspaceStateSnapshot(), mergeAttempts = 0) {
  setCloudSyncStatus("正在同步云端数据", "syncing");
  const response = await apiFetch("/api/workspace-state", {
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
    const response = await apiFetch("/api/workspace-state", { cache: "no-store" });
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
      ? 20
      : /vehicle importer|car importer|parallel import|import and export|汽车进口|平行进口/.test(value) ? 11 : 0,
    customerFit: /import|distributor|进口|分销|平行进口/.test(value)
      ? 27
      : /dealer|showroom|trading|经销|展厅|贸易/.test(value)
        ? 22
        : /fleet|rental|procurement|车队|租赁|采购/.test(value)
          ? 20
          : /automotive|vehicle|cars|汽车/.test(value) ? 12 : 0,
    purchaseIntent: /rfq|looking to buy|supplier wanted|dealer wanted|bulk order|询价|求购|招募经销商|批量采购/.test(value)
      ? 20
      : /procurement|wholesale|fleet purchase|采购|批发|车队/.test(value) ? 15 : 0,
    businessCapacity: /branches|locations|regional network|集团|分店|区域网络/.test(value)
      ? 13
      : /multi-brand|brand portfolio|多品牌/.test(value)
        ? 11
        : /luxury|premium|supercar|豪华|高端/.test(value) ? 7 : 0,
    modelFit: /electric|hybrid|new energy|chinese car|新能源|电动|混动|中国汽车/.test(value)
      ? 8
      : options.model ? 5 : 0,
    contactability: /owner|founder|director|procurement manager|老板|创始人|采购经理/.test(value)
      ? 7
      : /@|whatsapp|phone|contact|邮箱|电话|联系/.test(value) ? 6 : 0,
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
  const grade = lead.score >= 80 ? "适合优先联系" : "需要人工复核";
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

function normalizeAfterSalesOrder(raw = {}) {
  const createdAt = raw.createdAt || new Date().toISOString();
  const serviceLogs = Array.isArray(raw.serviceLogs) ? raw.serviceLogs : [];
  return {
    id: raw.id || `AS-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).slice(2, 6).toUpperCase()}`,
    customer: raw.customer || "",
    orderNo: raw.orderNo || raw.quoteId || "",
    quoteId: raw.quoteId || "",
    customerId: raw.customerId || "",
    model: raw.model || "",
    qty: Number(raw.qty || 1),
    vin: raw.vin || "",
    destination: raw.destination || raw.country || "",
    deliveryDate: raw.deliveryDate || "",
    warrantyUntil: raw.warrantyUntil || "",
    status: raw.status || "待交付",
    serviceType: raw.serviceType || "交付回访",
    owner: raw.owner || "",
    note: raw.note || "",
    createdAt,
    updatedAt: raw.updatedAt || createdAt,
    serviceLogs: serviceLogs.map((log) => ({
      at: log.at || createdAt,
      type: log.type || raw.serviceType || "交付回访",
      note: log.note || "",
      status: log.status || raw.status || "待交付"
    }))
  };
}

function afterSalesSourceOptions() {
  const quoted = quoteHistory.map((quote, index) => ({
    value: `quote:${index}`,
    label: `报价 ${quote.id || index + 1} · ${quote.customer || "未命名客户"} · ${quote.model || ""}`,
    data: quote
  }));
  const wonCustomers = customers
    .map((lead, index) => ({ lead, index }))
    .filter(({ lead }) => lead.stage === "已成交");
  return [
    ...quoted,
    ...wonCustomers.map(({ lead, index }) => ({
      value: `customer:${index}`,
      label: `成交客户 · ${lead.company || "未命名客户"} · ${lead.model || ""}`,
      data: lead
    }))
  ];
}

function renderAfterSalesSourceSelect() {
  const select = $("#afterSalesSource");
  if (!select) return;
  const current = select.value;
  const options = afterSalesSourceOptions();
  select.innerHTML = `<option value="">手工录入</option>${options.map((option) =>
    `<option value="${escapeHtml(option.value)}">${escapeHtml(option.label)}</option>`
  ).join("")}`;
  if ([...select.options].some((option) => option.value === current)) select.value = current;
}

function fillAfterSalesFromSource(value) {
  const form = $("#afterSalesForm");
  if (!form || !value) return;
  const [type, rawIndex] = value.split(":");
  const index = Number(rawIndex);
  if (type === "quote") {
    const quote = quoteHistory[index];
    if (!quote) return;
    form.customer.value = quote.customer || "";
    form.orderNo.value = quote.id || "";
    form.model.value = quote.model || "";
    form.qty.value = quote.qty || 1;
    form.destination.value = quote.destination || "";
    form.note.value = quote.quoteNotes || "";
  }
  if (type === "customer") {
    const lead = customers[index];
    if (!lead) return;
    form.customer.value = lead.company || "";
    form.orderNo.value = "";
    form.model.value = lead.model || "";
    form.qty.value = 1;
    form.destination.value = destinationByCountry[countryKey(lead.country)] || lead.country || "";
    form.note.value = lead.next || "";
  }
}

function afterSalesHealth(order) {
  const status = order.status || "";
  const warrantyDate = order.warrantyUntil ? new Date(order.warrantyUntil) : null;
  const warrantyExpired = warrantyDate && !Number.isNaN(warrantyDate.getTime()) && warrantyDate < new Date();
  if (status.includes("升级") || status.includes("投诉")) return ["urgent", "需优先处理"];
  if (status.includes("处理")) return ["working", "处理中"];
  if (warrantyExpired) return ["expired", "质保已到期"];
  if (status.includes("解决") || status.includes("关闭")) return ["closed", "已闭环"];
  return ["normal", "正常跟踪"];
}

function renderAfterSales() {
  renderAfterSalesSourceSelect();
  const board = $("#afterSalesBoard");
  const summary = $("#afterSalesSummary");
  if (!board) return;
  const openCount = afterSalesOrders.filter((order) => !["已解决", "已关闭"].includes(order.status)).length;
  const urgentCount = afterSalesOrders.filter((order) => afterSalesHealth(order)[0] === "urgent").length;
  if (summary) summary.textContent = `${afterSalesOrders.length} 个售后订单 · ${openCount} 个待跟进${urgentCount ? ` · ${urgentCount} 个需升级` : ""}`;
  board.innerHTML = afterSalesOrders.length ? afterSalesOrders.map((order, index) => {
    const [healthClass, healthLabel] = afterSalesHealth(order);
    const latestLog = order.serviceLogs?.[0];
    return `
      <article class="aftersales-card ${healthClass}">
        <div class="aftersales-card-head">
          <div>
            <span>${escapeHtml(order.orderNo || "未填写订单号")}</span>
            <h4>${escapeHtml(order.customer || "未填写客户")}</h4>
          </div>
          <b>${escapeHtml(healthLabel)}</b>
        </div>
        <dl>
          <div><dt>车型 / 数量</dt><dd>${escapeHtml(order.model || "待确认")} · ${escapeHtml(order.qty || 1)} 台</dd></div>
          <div><dt>VIN</dt><dd>${escapeHtml(order.vin || "待确认")}</dd></div>
          <div><dt>目的港</dt><dd>${escapeHtml(order.destination || "待确认")}</dd></div>
          <div><dt>交付日期</dt><dd>${escapeHtml(order.deliveryDate || "待确认")}</dd></div>
          <div><dt>质保截止</dt><dd>${escapeHtml(order.warrantyUntil || "待确认")}</dd></div>
          <div><dt>当前状态</dt><dd>${escapeHtml(order.status || "待交付")}</dd></div>
        </dl>
        <div class="aftersales-log">
          <strong>${escapeHtml(order.serviceType || "交付回访")}</strong>
          <p>${escapeHtml(order.note || latestLog?.note || "暂无处理记录")}</p>
          ${latestLog ? `<small>最近记录：${escapeHtml(formatJobTime(latestLog.at))} · ${escapeHtml(latestLog.status)}</small>` : ""}
        </div>
        <div class="aftersales-actions">
          <select data-after-status="${index}" aria-label="更新售后状态">
            ${["待交付", "质保期内", "处理中", "已解决", "需升级处理", "已关闭"].map((status) =>
              `<option ${status === order.status ? "selected" : ""}>${status}</option>`
            ).join("")}
          </select>
          <button type="button" data-after-log="${index}">追加记录</button>
          <button class="danger-button" type="button" data-after-delete="${index}">删除</button>
        </div>
      </article>
    `;
  }).join("") : `<p class="empty">暂无已完成订单。可以从报价历史或已成交客户生成售后订单，也可以手工录入。</p>`;
}

function saveAfterSalesOrder(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const data = Object.fromEntries(new FormData(form).entries());
  const now = new Date().toISOString();
  const order = normalizeAfterSalesOrder({
    ...data,
    createdAt: now,
    updatedAt: now,
    serviceLogs: data.note ? [{ at: now, type: data.serviceType, note: data.note, status: data.status }] : []
  });
  afterSalesOrders.unshift(order);
  form.reset();
  form.qty.value = 1;
  saveState();
  renderAfterSales();
  renderKpis();
}

function updateAfterSalesStatus(index, status) {
  const order = afterSalesOrders[index];
  if (!order) return;
  order.status = status;
  order.updatedAt = new Date().toISOString();
  order.serviceLogs = [{
    at: order.updatedAt,
    type: "状态更新",
    note: `售后状态更新为：${status}`,
    status
  }, ...(order.serviceLogs || [])].slice(0, 20);
  saveState();
  renderAfterSales();
}

function appendAfterSalesLog(index) {
  const order = afterSalesOrders[index];
  if (!order) return;
  const note = prompt("请输入本次售后处理记录，例如客户反馈、备件进度、下一步责任人：", order.note || "");
  if (!note) return;
  const now = new Date().toISOString();
  order.note = note;
  order.updatedAt = now;
  order.serviceLogs = [{
    at: now,
    type: order.serviceType || "售后跟进",
    note,
    status: order.status || "处理中"
  }, ...(order.serviceLogs || [])].slice(0, 20);
  saveState();
  renderAfterSales();
}

function deleteAfterSalesOrder(index) {
  const order = afterSalesOrders[index];
  if (!order) return;
  if (!confirm(`确认删除 ${order.customer || "该客户"} 的售后订单吗？`)) return;
  rememberDeletedRecord(order, "afterSalesOrders");
  afterSalesOrders.splice(index, 1);
  saveState();
  renderAfterSales();
  renderKpis();
}

function renderKeywords(words = defaultKeywords) {
  $("#keywords").innerHTML = words.map((word) => `<span>${word}</span>`).join("");
}

function discoveryJobLeadMatches(lead, jobId) {
  return jobId === "all" || String(lead.discoveryJobId || "") === String(jobId || "");
}

function activeDiscoveryJob() {
  if (activeDiscoveryJobFilter === "all") return null;
  return discoveryJobs.find((job) => String(job.id) === String(activeDiscoveryJobFilter)) || null;
}

function renderLeads() {
  const filteredLeads = reviewLeads.filter((lead) => discoveryJobLeadMatches(lead, activeDiscoveryJobFilter));
  const summary = $("#candidateLeadSummary");
  const job = activeDiscoveryJob();
  if (summary) {
    summary.textContent = job
      ? `${discoveryJobLabel(job)}：显示 ${filteredLeads.length} 条候选客户`
      : "点击客户卡片可跳到审核详情";
  }
  $("#leadList").innerHTML = filteredLeads.length ? filteredLeads.map((lead) => `
    <article class="lead-card" data-candidate-lead="${escapeHtml(lead.id || "")}" role="button" tabindex="0" title="查看线索审核详情">
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
  `).join("") : `<p class="empty">${job ? "这条搜索记录暂无候选客户，可能尚未导入或已被审核/删除。" : "暂无待审核线索。请先点击“一键获客到待审核”。"}</p>`;
}

function showCandidateInReview(leadId) {
  const lead = reviewLeads.find((item) => String(item.id || "") === String(leadId || ""));
  if (!lead) return;
  const statusFilter = $("#reviewStatusFilter");
  const discoveryFilter = $("#reviewDiscoveryFilter");
  if (statusFilter) statusFilter.value = "pending";
  if ($("#reviewTimeFilter")) $("#reviewTimeFilter").value = "all";
  if ($("#reviewSourceFilter")) $("#reviewSourceFilter").value = "all";
  if ($("#reviewCountryFilter")) $("#reviewCountryFilter").value = "all";
  if ($("#reviewTierFilter")) $("#reviewTierFilter").value = "all";
  renderReviewFilterOptions();
  if (discoveryFilter) {
    const hasJobOption = lead.discoveryJobId && [...discoveryFilter.options].some((option) => option.value === lead.discoveryJobId);
    discoveryFilter.value = hasJobOption ? lead.discoveryJobId : "all";
  }
  selectedReviewLeadId = `pending:${lead.id}`;
  showSection("review");
  renderReview();
  requestAnimationFrame(() => {
    const row = document.querySelector(`[data-review-lead-row="${CSS.escape(selectedReviewLeadId)}"]`);
    row?.scrollIntoView({ behavior: "smooth", block: "center" });
    row?.focus({ preventScroll: true });
  });
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

function reviewStatusMode() {
  return $("#reviewStatusFilter")?.value === "approved" ? "approved" : "pending";
}

function reviewSourceLeads() {
  return reviewStatusMode() === "approved" ? customers : reviewLeads;
}

function renderReview() {
  // Keep the review queue stable. Scores are decision support, not a reason to
  // move the card the reviewer is currently working on after manual calibration.
  const reviewMode = reviewStatusMode();
  if (reviewMode === "pending") purgeIrrelevantReviewLeads();
  renderReviewFilterOptions();
  const sourceLeads = reviewSourceLeads();
  const rankedLeads = sourceLeads
    .map((lead, index) => ({ lead, index }))
    .filter(({ lead }) => reviewLeadMatchesFilters(lead));
  const visibleIds = new Set(rankedLeads.map(({ lead, index }) => `${reviewMode}:${lead.id || index}`));
  if (reviewMode === "pending") {
    reviewSelectedIds = new Set([...reviewSelectedIds].filter((id) => reviewLeads.some((lead) => lead.id === id)));
  } else {
    reviewSelectedIds = new Set();
  }
  const visibleReviewIds = rankedLeads.map(({ lead }) => lead.id).filter(Boolean);
  const selectedVisibleCount = [...reviewSelectedIds].filter((id) => visibleReviewIds.includes(id)).length;
  const summary = $("#reviewFilterSummary");
  if (summary) summary.textContent = `显示 ${rankedLeads.length} / ${sourceLeads.length} 条${reviewMode === "approved" ? " · 已审核客户" : reviewSelectedIds.size ? ` · 已选 ${reviewSelectedIds.size} 条` : ""}`;
  const selectVisibleButton = $("#selectVisibleReviewLeads");
  if (selectVisibleButton) {
    selectVisibleButton.disabled = reviewMode === "approved" || !rankedLeads.length;
    selectVisibleButton.textContent = rankedLeads.length && selectedVisibleCount === rankedLeads.length ? "取消选择当前结果" : "全选当前结果";
  }
  const deleteSelectedButton = $("#deleteSelectedReviewLeads");
  if (deleteSelectedButton) {
    deleteSelectedButton.disabled = reviewMode === "approved" || !reviewSelectedIds.size;
    deleteSelectedButton.textContent = `删除已选（${reviewSelectedIds.size}）`;
  }
  if (!rankedLeads.length) {
    $("#reviewGrid").innerHTML = `<p class="empty">${reviewMode === "approved" ? "暂无已审核客户。客户池中的客户会显示在这里。" : "暂无待审核线索。一键获客抓到的客户会先出现在这里。"}</p>`;
    return;
  }
  const rankedLeadRows = rankedLeads.map((record, rankIndex) => ({ ...record, rankIndex }));
  if (!selectedReviewLeadId || !visibleIds.has(selectedReviewLeadId)) {
    selectedReviewLeadId = `${reviewMode}:${rankedLeadRows[0].lead.id || rankedLeadRows[0].index}`;
  }
  const selectedRecord = rankedLeadRows.find(({ lead, index }) => `${reviewMode}:${lead.id || index}` === selectedReviewLeadId) || rankedLeadRows[0];
  const reviewListHtml = rankedLeadRows.map(({ lead, index, rankIndex }) => {
    const rowId = `${reviewMode}:${lead.id || index}`;
    const phoneCount = evidenceValues(lead.phoneSources, lead.phone).length + evidenceValues(lead.whatsappSources, lead.whatsapp).length;
    const missing = (lead.sourceCoverage?.missingFields || []).join("、") || "齐全";
    return `
      <article class="review-list-row ${rowId === selectedReviewLeadId ? "active" : ""}" data-review-lead-row="${escapeHtml(rowId)}" tabindex="0">
        ${reviewMode === "pending" ? `<label class="review-select"><input type="checkbox" data-review-select="${escapeHtml(lead.id)}" ${reviewSelectedIds.has(lead.id) ? "checked" : ""}><span>选择</span></label>` : `<span class="review-approved-mark">已审核</span>`}
        <div class="review-list-main">
          <strong>${escapeHtml(lead.company)}</strong>
          <span>${escapeHtml(formatReviewLeadTime(lead))} · ${escapeHtml(lead.origin || lead.sourceType || "公开来源")}</span>
        </div>
        <div class="review-list-badges">
          <b>${escapeHtml(lead.score)}分 · ${escapeHtml(scoreTierLabel(lead.scoreTier))}</b>
          <span>${escapeHtml(lead.confidenceLabel || "待确认")} ${escapeHtml(lead.confidence || 0)}%</span>
        </div>
        <div class="review-list-meta">
          <span>电话 ${phoneCount}</span>
          <span>来源 ${escapeHtml(lead.sourceCoverage?.total || lead.evidenceSources?.length || 0)}/官${escapeHtml(lead.sourceCoverage?.official || 0)}</span>
          <span>缺 ${escapeHtml(missing)}</span>
        </div>
      </article>
    `;
  }).join("");
  const selectedDetailHtml = [selectedRecord].map(({ lead, index, rankIndex }) => {
    const editId = `${reviewMode}:${lead.id || index}`;
    const isEditing = editingReviewLeadId === editId;
    return `
    <article class="review-card">
      <div class="review-title-row">
        <div>
          <div class="review-card-meta">
            ${reviewMode === "pending" ? `<label class="review-select"><input type="checkbox" data-review-select="${escapeHtml(lead.id)}" ${reviewSelectedIds.has(lead.id) ? "checked" : ""}><span>选择</span></label>` : `<span class="tag">已审核客户</span>`}
            <span class="tag">#${rankIndex + 1} · ${lead.researchAt ? "已完成公开信息尽调" : "待全网补全"}</span>
            <span class="review-captured-at">${escapeHtml(formatReviewLeadTime(lead))} · ${escapeHtml(lead.source || lead.origin || "未知来源")}</span>
          </div>
          <h3>${escapeHtml(lead.company)}</h3>
          <p>${escapeHtml(lead.researchSummary || "当前只有原始发现来源，请先执行全网补全。")}</p>
        </div>
        ${reviewMode === "pending" ? `<button class="research-button" type="button" data-research-index="${index}">
          ${lead.researching ? "正在检索…" : lead.researchAt ? "重新全网核验" : "全网补全信息"}
        </button>` : `<span class="review-approved-status">已进入客户池</span>`}
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
          <dd>${renderContactSummary(lead)}</dd>
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
          <span>进出口资质 <strong>${escapeHtml(lead.scoreDimensions?.tradeQualification || 0)}/20</strong></span>
          <span>客户匹配 <strong>${escapeHtml(lead.scoreDimensions?.customerFit || 0)}/27</strong></span>
          <span>采购意向 <strong>${escapeHtml(lead.scoreDimensions?.purchaseIntent || 0)}/20</strong></span>
          <span>经营能力 <strong>${escapeHtml(lead.scoreDimensions?.businessCapacity || 0)}/14</strong></span>
          <span>车型匹配 <strong>${escapeHtml(lead.scoreDimensions?.modelFit || 0)}/12</strong></span>
          <span>可触达性 <strong>${escapeHtml(lead.scoreDimensions?.contactability || 0)}/7</strong></span>
          ${Number(lead.scoreDimensions?.penalty || 0) < 0
            ? `<span class="penalty">风险扣分 <strong>${escapeHtml(lead.scoreDimensions.penalty)}</strong></span>`
            : ""}
        </div>
        <div>${(lead.scoreBreakdown || []).length
          ? lead.scoreBreakdown.map((item) => `<b class="${Number(item.points) < 0 ? "negative" : ""}">${escapeHtml(item.label)} ${Number(item.points) > 0 ? "+" : ""}${escapeHtml(item.points)}</b>`).join("")
          : `<b>${escapeHtml(lead.scoreBasis || "等待官网核验")}</b>`}
        </div>
        ${reviewMode === "pending" ? `<div class="score-calibration">
          <span>人工校准</span>
          <button type="button" data-score-adjust="-5" data-index="${index}">-5</button>
          <button type="button" data-score-adjust="5" data-index="${index}">+5</button>
          <button type="button" data-score-reset data-index="${index}">恢复系统分</button>
        </div>` : ""}
      </div>
      <div class="split-actions">
        ${safeHttpUrl(lead.sourceUrl || lead.source)
          ? `<a class="button-link ghost" href="${escapeHtml(safeHttpUrl(lead.sourceUrl || lead.source))}" target="_blank" rel="noopener noreferrer">查看线索原文</a>`
          : `<button class="ghost" type="button" disabled title="该线索没有可打开的原始网址">查看线索原文</button>`}
        ${reviewMode === "pending" ? `
          <button class="primary" type="button" data-review-action="approve" data-index="${index}">通过</button>
          <button class="ghost" type="button" data-review-action="reject" data-index="${index}">拒绝</button>
          <button class="danger-button" type="button" data-review-action="delete" data-index="${index}">删除</button>
          <button class="ghost" type="button" data-review-edit="${index}" data-review-edit-id="${escapeHtml(editId)}">编辑</button>
        ` : `<button class="primary" type="button" data-section="crm">回到客户池</button>`}
      </div>
      ${reviewMode === "pending" && isEditing ? renderLeadEditForm(lead, index, editId) : ""}
      <details class="review-more" data-review-detail-id="${escapeHtml(lead.id || index)}" data-review-detail-index="${index}" data-review-detail-mode="${reviewMode}">
        <summary>
          <span>查看全部来源与核验详情</span>
          <small class="review-source-badges">
            <b>${lead.sourceCoverage?.total || lead.evidenceSources?.length || 0} 个来源</b>
            <b>${(lead.socialProfiles || []).length} 个社媒账号</b>
          </small>
        </summary>
        <div class="review-more-content" data-review-detail-content></div>
      </details>
    </article>
  `;
  }).join("");
  $("#reviewGrid").innerHTML = `
    <div class="review-workbench">
      <aside class="review-workbench-list" aria-label="待审核线索列表">
        <div class="review-workbench-list-head">
          <strong>${reviewMode === "approved" ? "已审核客户" : "待审核线索"}</strong>
          <span>${rankedLeadRows.length} 条</span>
        </div>
        <div class="review-list-scroll">${reviewListHtml}</div>
      </aside>
      <section class="review-workbench-detail">${selectedDetailHtml}</section>
    </div>
  `;
}

function leadEditListValue(values, fallback = "") {
  const normalized = Array.isArray(values) ? values : [];
  const rows = normalized
    .map((item) => String(item?.value || item?.email || item || "").trim())
    .filter(Boolean);
  if (fallback) rows.push(String(fallback).trim());
  return Array.from(new Set(rows.filter(Boolean))).join("\n");
}

function leadEditTextListValue(values) {
  return Array.isArray(values) ? values.map((item) => String(item || "").trim()).filter(Boolean).join("\n") : "";
}

function splitLeadEditLines(value) {
  return String(value || "")
    .split(/\r?\n|[;；]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function manualEvidenceSource(lead) {
  return {
    url: safeHttpUrl(lead.sourceUrl || lead.source || lead.customerWebsite) || "",
    name: "人工核验",
    verified: true,
    excerpt: "人工查看线索原文后补充"
  };
}

function manualValueSources(values, lead) {
  const source = manualEvidenceSource(lead);
  return values.map((value) => ({
    value,
    sources: source.url ? [source] : [{ ...source, url: "" }]
  }));
}

function renderLeadEditForm(lead, index, editId) {
  return `
    <form class="lead-edit-panel" data-review-edit-form data-index="${index}" data-edit-id="${escapeHtml(editId)}">
      <div class="lead-edit-head">
        <strong>编辑线索信息</strong>
        <span>人工查看原文后补充的信息，保存后会同步到审核详情和云端。</span>
      </div>
      <div class="lead-edit-grid">
        <label>公司名称
          <input name="company" value="${escapeHtml(lead.company || "")}">
        </label>
        <label>客户官网
          <input name="customerWebsite" value="${escapeHtml(lead.customerWebsite || "")}" placeholder="https://example.com">
        </label>
        <label>联系人
          <input name="contactName" value="${escapeHtml(lead.contactName || "")}">
        </label>
        <label>职位
          <input name="contactRole" value="${escapeHtml(lead.contactRole || "")}">
        </label>
        <label>邮箱（每行一个）
          <textarea name="emails" rows="3">${escapeHtml(leadEditListValue(lead.emailSources, lead.email))}</textarea>
        </label>
        <label>电话（每行一个）
          <textarea name="phones" rows="3">${escapeHtml(leadEditListValue(lead.phoneSources, lead.phone))}</textarea>
        </label>
        <label>WhatsApp（每行一个）
          <textarea name="whatsapps" rows="3">${escapeHtml(leadEditListValue(lead.whatsappSources, lead.whatsapp))}</textarea>
        </label>
        <label>推荐车型（每行一个）
          <textarea name="recommendedModels" rows="3">${escapeHtml(leadEditTextListValue(lead.recommendedModels || [lead.model]))}</textarea>
        </label>
        <label class="lead-edit-wide">机会信号（每行一个）
          <textarea name="signals" rows="3">${escapeHtml(leadEditTextListValue([...(lead.intentSignals || []), ...(lead.businessSignals || [])]))}</textarea>
        </label>
        <label class="lead-edit-wide">推荐联系理由
          <textarea name="contactReason" rows="4">${escapeHtml(lead.contactReason || lead.reason || "")}</textarea>
        </label>
      </div>
      <div class="lead-edit-actions">
        <button class="primary" type="submit">保存修改</button>
        <button class="ghost" type="button" data-review-edit-cancel>取消</button>
      </div>
    </form>
  `;
}

function saveReviewLeadEdit(index, form) {
  const lead = reviewLeads[index];
  if (!lead || !form) return;
  const data = Object.fromEntries(new FormData(form).entries());
  const emails = splitLeadEditLines(data.emails).map((item) => item.toLowerCase());
  const phones = splitLeadEditLines(data.phones);
  const whatsapps = splitLeadEditLines(data.whatsapps);
  const recommendedModels = splitLeadEditLines(data.recommendedModels);
  const signals = splitLeadEditLines(data.signals);
  const source = manualEvidenceSource(lead);
  const emailSources = emails.map((email) => ({
    email,
    sources: source.url ? [source] : [{ ...source, url: "" }]
  }));
  const nextLead = normalizeLead({
    ...lead,
    company: String(data.company || lead.company || "").trim() || lead.company,
    customerWebsite: String(data.customerWebsite || "").trim(),
    contactName: String(data.contactName || "").trim(),
    contactRole: String(data.contactRole || "").trim(),
    email: emails[0] || "",
    emailSources: mergeEmailSources(emailSources, lead.emailSources || []),
    phone: phones[0] || "",
    phoneSources: manualValueSources(phones, lead),
    whatsapp: whatsapps[0] || "",
    whatsappSources: manualValueSources(whatsapps, lead),
    recommendedModels: recommendedModels.length ? recommendedModels : lead.recommendedModels,
    intentSignals: signals,
    businessSignals: [],
    contactReason: String(data.contactReason || "").trim(),
    manualEditedAt: new Date().toISOString(),
    sourceCoverage: {
      ...(lead.sourceCoverage || {}),
      contactable: Boolean(emails.length || phones.length || whatsapps.length),
      missingFields: (lead.sourceCoverage?.missingFields || []).filter((field) => {
        const text = String(field || "");
        if (emails.length && /邮箱|email/i.test(text)) return false;
        if ((phones.length || whatsapps.length) && /电话|phone|whatsapp/i.test(text)) return false;
        if (data.contactName && /联系人|contact/i.test(text)) return false;
        return true;
      })
    }
  });
  reviewLeads[index] = nextLead;
  selectedReviewLeadId = `pending:${nextLead.id || index}`;
  editingReviewLeadId = "";
  refreshAllLeadViews();
}


function renderReviewDetailContent(lead) {
  return `
      <div class="review-drawer-head">
        <div>
          <strong>${escapeHtml(lead.company)} · 核验详情</strong>
          <span>在右侧查看，不影响当前线索列表位置</span>
        </div>
        <button class="ghost compact" type="button" data-close-review-details>关闭</button>
      </div>
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
      <p><strong>审核说明：</strong>证据完整度和系统评分仅供参考；即使证据不足，也可以由人工判断后点击“通过”。</p>
  `;
}

function reviewDetailLead(details) {
  const id = details?.dataset?.reviewDetailId || "";
  const index = Number(details?.dataset?.reviewDetailIndex);
  const leads = details?.dataset?.reviewDetailMode === "approved" ? customers : reviewLeads;
  return leads.find((lead) => String(lead.id || "") === id) || leads[index] || null;
}

function clearReviewDetail(details) {
  const content = details?.querySelector("[data-review-detail-content]");
  if (!content) return;
  content.textContent = "";
  delete content.dataset.loaded;
}

function closeOpenReviewDetails(except = null) {
  $$("#reviewGrid details.review-more[open]").forEach((details) => {
    if (details !== except) details.removeAttribute("open");
  });
}

function hydrateReviewDetail(details) {
  const content = details?.querySelector("[data-review-detail-content]");
  if (!content || content.dataset.loaded === "true") return;
  const lead = reviewDetailLead(details);
  content.innerHTML = lead
    ? renderReviewDetailContent(lead)
    : `<p class="empty">详情已刷新，请重新打开线索。</p>`;
  content.dataset.loaded = "true";
}

function reviewLeadTimestamp(lead) {
  const value = lead.createdAt || lead.importedAt || lead.discoveredAt || lead.researchAt || lead.publishedAt || "";
  const date = value ? new Date(value) : null;
  return date && !Number.isNaN(date.getTime()) ? date : null;
}

function formatReviewLeadTime(lead) {
  const date = reviewLeadTimestamp(lead);
  return date ? `入池 ${date.toLocaleDateString("zh-CN")}` : "入池时间未知";
}

const reviewSourceOptions = [
  ["combined", "综合搜索（地图 + 官网）"],
  ["social", "社媒综合（Facebook + Instagram + TikTok + YouTube + LinkedIn）"],
  ["google", "Google Maps 企业数据"],
  ["osm", "OpenStreetMap 地图"],
  ["dealer", "车商官网 / 汽车行业目录"],
  ["instagram", "Instagram 公开账号"],
  ["facebook", "Facebook 公开主页"],
  ["tiktok", "TikTok 公开账号"],
  ["youtube", "YouTube 公开频道"],
  ["linkedin", "LinkedIn 公司 / 个人主页"],
  ["telegram", "Telegram 公开频道 / 群组"],
  ["twitter", "X / Twitter 公开主页"],
  ["threads", "Threads 公开主页"],
  ["pinterest", "Pinterest 公开主页"],
  ["reddit", "Reddit 公开社区 / 用户"],
  ["vk", "VK 公开主页"]
];

function reviewSourceKey(lead) {
  const concreteValue = [
    lead.platform,
    lead.origin,
    lead.sourceType,
    lead.sourceTitle,
    lead.source,
    lead.sourceUrl,
    ...(lead.evidenceSources || []).flatMap((source) => [
      source.sourceName,
      source.sourceType,
      source.url
    ])
  ].filter(Boolean).join(" ").toLowerCase();
  if (!concreteValue) return "dealer";
  if (
    concreteValue.includes("youtube.com")
    || concreteValue.includes("youtu.be")
    || concreteValue.includes("youtube")
    || concreteValue.includes("yt3.ggpht.com")
    || concreteValue.includes("ytimg.com")
  ) return "youtube";
  if (
    concreteValue.includes("google maps")
    || concreteValue.includes("maps.google.")
    || concreteValue.includes("google.com/maps")
    || concreteValue.includes("maps/search")
    || concreteValue.includes("place_id")
    || concreteValue.includes("places api")
  ) return "google";
  if (concreteValue.includes("openstreetmap") || concreteValue.includes("overpass") || concreteValue.includes("osm")) return "osm";
  if (concreteValue.includes("instagram.com") || concreteValue.includes("instagram")) return "instagram";
  if (concreteValue.includes("facebook.com") || concreteValue.includes("facebook")) return "facebook";
  if (concreteValue.includes("tiktok.com") || concreteValue.includes("tiktok")) return "tiktok";
  if (concreteValue.includes("linkedin.com") || concreteValue.includes("linkedin")) return "linkedin";
  if (concreteValue.includes("t.me") || concreteValue.includes("telegram")) return "telegram";
  if (concreteValue.includes("x.com") || concreteValue.includes("twitter.com") || concreteValue.includes("twitter")) return "twitter";
  if (concreteValue.includes("threads.net") || concreteValue.includes("threads")) return "threads";
  if (concreteValue.includes("pinterest.")) return "pinterest";
  if (concreteValue.includes("reddit.com") || concreteValue.includes("reddit")) return "reddit";
  if (concreteValue.includes("vk.com")) return "vk";
  if (
    concreteValue.includes("官网")
    || concreteValue.includes("official")
    || concreteValue.includes("directory")
    || concreteValue.includes("行业")
    || concreteValue.includes("dealer")
    || concreteValue.includes("showroom")
  ) return "dealer";
  const value = [
    lead.discoverySource,
    lead.sourceMode
  ].filter(Boolean).join(" ").toLowerCase();
  if (/\bcombined\b|综合搜索/.test(value)) return "dealer";
  if (/\bsocial\b|社媒综合/.test(value)) return "social";
  if (value === "google") return "google";
  if (value.includes("openstreetmap") || value.includes("overpass") || value.includes("osm")) return "osm";
  if (value.includes("instagram.com") || value.includes("instagram")) return "instagram";
  if (value.includes("facebook.com") || value.includes("facebook")) return "facebook";
  if (value.includes("tiktok.com") || value.includes("tiktok")) return "tiktok";
  if (value.includes("youtube.com") || value.includes("youtu.be") || value.includes("youtube")) return "youtube";
  if (value.includes("linkedin.com") || value.includes("linkedin")) return "linkedin";
  if (value.includes("t.me") || value.includes("telegram")) return "telegram";
  if (value.includes("x.com") || value.includes("twitter.com") || value.includes("twitter")) return "twitter";
  if (value.includes("threads.net") || value.includes("threads")) return "threads";
  if (value.includes("pinterest.")) return "pinterest";
  if (value.includes("reddit.com") || value.includes("reddit")) return "reddit";
  if (value.includes("vk.com")) return "vk";
  return "dealer";
}

function reviewCountryKey(value) {
  const key = countryKey(value);
  return key ? key.toLowerCase() : "";
}

function reviewLeadCountryKey(lead) {
  return reviewCountryKey(lead.country);
}

function discoveryJobFilterOptions(leads) {
  const options = new Map();
  leads.forEach((lead) => {
    const id = String(lead.discoveryJobId || "");
    if (!id) return;
    const job = discoveryJobs.find((item) => String(item.id) === id);
    options.set(id, lead.discoveryJobLabel || discoveryJobLabel(job) || `搜索记录 ${id.slice(0, 8)}`);
  });
  discoveryJobs.forEach((job) => {
    const id = String(job.id || "");
    if (!id || options.has(id)) return;
    options.set(id, discoveryJobLabel(job));
  });
  return [...options.entries()];
}

function renderReviewFilterOptions() {
  const sourceSelect = $("#reviewSourceFilter");
  const countrySelect = $("#reviewCountryFilter");
  const discoverySelect = $("#reviewDiscoveryFilter");
  if (!sourceSelect && !countrySelect && !discoverySelect) return;
  const sourceLeads = reviewSourceLeads();
  const current = sourceSelect?.value || "all";
  const available = new Set(sourceLeads.map(reviewSourceKey));
  if (sourceSelect) {
    const options = reviewSourceOptions
      .filter(([value]) => available.has(value) || value === current)
      .map(([value, label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`)
      .join("");
    sourceSelect.innerHTML = `<option value="all">全部来源</option>${options || reviewSourceOptions.map(([value, label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`).join("")}`;
    sourceSelect.value = current === "all" || [...available].includes(current) ? current : "all";
  }

  if (countrySelect) {
    const currentCountry = countrySelect.value || "all";
    const countryOptions = new Map();
    countries.forEach((country) => {
      const value = reviewCountryKey(country.name);
      if (value) countryOptions.set(value, country.name);
    });
    sourceLeads.forEach((lead) => {
      const value = reviewLeadCountryKey(lead);
      if (value && !countryOptions.has(value)) countryOptions.set(value, lead.country);
    });
    const countryOptionHtml = [...countryOptions.entries()]
      .sort((a, b) => String(a[1]).localeCompare(String(b[1]), "zh-CN"))
      .map(([value, label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`)
      .join("");
    countrySelect.innerHTML = `<option value="all">全部国家</option>${countryOptionHtml}`;
    countrySelect.value = currentCountry === "all" || countryOptions.has(currentCountry) ? currentCountry : "all";
  }

  if (discoverySelect) {
    const currentDiscovery = discoverySelect.value || "all";
    const options = discoveryJobFilterOptions(sourceLeads);
    discoverySelect.innerHTML = `<option value="all">全部搜索记录</option>${options.map(([value, label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`).join("")}`;
    discoverySelect.value = currentDiscovery === "all" || options.some(([value]) => value === currentDiscovery) ? currentDiscovery : "all";
  }
}

function reviewLeadMatchesFilters(lead) {
  const discoveryFilter = $("#reviewDiscoveryFilter")?.value || "all";
  const timeFilter = $("#reviewTimeFilter")?.value || "all";
  const sourceFilter = $("#reviewSourceFilter")?.value || "all";
  const countryFilter = $("#reviewCountryFilter")?.value || "all";
  const tierFilter = $("#reviewTierFilter")?.value || "all";
  const source = reviewSourceKey(lead);
  if (discoveryFilter !== "all" && String(lead.discoveryJobId || "") !== discoveryFilter) return false;
  if (sourceFilter !== "all" && source !== sourceFilter) return false;
  if (countryFilter !== "all" && reviewLeadCountryKey(lead) !== countryFilter) return false;
  if (tierFilter !== "all" && lead.scoreTier !== tierFilter) return false;
  if (timeFilter === "all") return true;
  const date = reviewLeadTimestamp(lead);
  if (!date) return timeFilter === "unknown";
  if (timeFilter === "unknown") return false;
  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const ageDays = (Date.now() - date.getTime()) / 86400000;
  if (timeFilter === "today") return date >= startOfToday;
  if (timeFilter === "7") return ageDays >= 0 && ageDays < 7;
  if (timeFilter === "30") return ageDays >= 0 && ageDays < 30;
  return ageDays >= 30;
}

function deleteReviewLeads(ids) {
  const idSet = new Set(ids.filter(Boolean));
  const selected = reviewLeads.filter((lead) => idSet.has(lead.id));
  if (!selected.length) return;
  const description = selected.length === 1 ? `“${selected[0].company}”` : `${selected.length} 条线索`;
  if (!confirm(`确认删除${description}吗？删除后不会进入客户池或拒绝记录。`)) return;
  selected.forEach((lead) => rememberDeletedRecord(lead, "reviewLeads"));
  reviewLeads = reviewLeads.filter((lead) => !idSet.has(lead.id));
  reviewSelectedIds = new Set([...reviewSelectedIds].filter((id) => !idSet.has(id)));
  refreshAllLeadViews();
}

function renderCrm() {
  const today = new Date().toISOString().slice(0, 10);
  const activeCustomers = customers.filter((lead) => !["已成交", "已流失"].includes(lead.stage));
  const dueCustomers = activeCustomers.filter((lead) => !lead.nextFollowAt || lead.nextFollowAt <= today);
  const overdueCustomers = activeCustomers.filter((lead) => lead.nextFollowAt && lead.nextFollowAt < today);
  const missingCustomers = activeCustomers.filter((lead) => !lead.nextFollowAt);
  const priorityCustomers = customers.filter((lead) => ["A", "B"].includes(lead.scoreTier));
  const counts = { all: customers.length, due: dueCustomers.length, overdue: overdueCustomers.length, missing: missingCustomers.length, priority: priorityCustomers.length };
  const tabs = $("#crmViewTabs");
  if (tabs) {
    Object.entries(counts).forEach(([key, count]) => {
      const badge = $(`#crmCount${key[0].toUpperCase()}${key.slice(1)}`);
      if (badge) badge.textContent = count;
    });
    Array.from(tabs.querySelectorAll("[data-crm-filter]")).forEach((button) => button.classList.toggle("active", button.dataset.crmFilter === crmViewFilter));
  }
  const filteredCustomers = customers.map((lead, index) => ({ lead, index })).filter(({ lead }) => {
    if (crmViewFilter === "due") return !["已成交", "已流失"].includes(lead.stage) && (!lead.nextFollowAt || lead.nextFollowAt <= today);
    if (crmViewFilter === "overdue") return !["已成交", "已流失"].includes(lead.stage) && lead.nextFollowAt && lead.nextFollowAt < today;
    if (crmViewFilter === "missing") return !["已成交", "已流失"].includes(lead.stage) && !lead.nextFollowAt;
    if (crmViewFilter === "priority") return ["A", "B"].includes(lead.scoreTier);
    return true;
  });
  const viewHint = $("#crmViewHint");
  if (viewHint) viewHint.textContent = {
    all: `显示全部 ${customers.length} 位客户池客户。`,
    due: `优先处理今天需要推进的 ${dueCustomers.length} 位客户。`,
    overdue: `共有 ${overdueCustomers.length} 位客户已超过计划跟进日期。`,
    missing: `共有 ${missingCustomers.length} 位客户尚未设定下一次跟进日期。`,
    priority: `显示评分为 A / B 的 ${priorityCustomers.length} 位高价值客户。`
  }[crmViewFilter];
  $("#crmRows").innerHTML = filteredCustomers.length ? filteredCustomers.map(({ lead, index }) => `
    <tr>
      <td><button class="link-button crm-customer-link" type="button" data-crm-action="review" data-index="${index}">${escapeHtml(lead.company)}</button><br><span>${escapeHtml(lead.contactName || lead.email || lead.phone || "暂无联系人")}</span></td>
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
      <td>${renderCrmFollowStatus(lead, today)}</td>
      <td>
        <div class="crm-actions">
          <button type="button" data-crm-action="email" data-index="${index}">写开发信</button>
          <button type="button" data-crm-action="quote" data-index="${index}">去报价</button>
          <button type="button" data-crm-action="return-review" data-index="${index}">退回审核</button>
          <button type="button" data-crm-action="delete" data-index="${index}">删除</button>
        </div>
      </td>
    </tr>
  `).join("") : `<tr><td colspan="9">当前视图没有符合条件的客户。</td></tr>`;
  $("#heroPending").textContent = reviewLeads.length;
  $("#heroCustomers").textContent = customers.length;
  $("#heroGradeA").textContent = customers.filter((lead) => lead.score >= 80).length;
  renderLeadSelect();
}

function renderCrmFollowStatus(lead, today) {
  if (["已成交", "已流失"].includes(lead.stage)) return `<span class="crm-follow-status complete">${escapeHtml(lead.stage)}</span>`;
  if (!lead.nextFollowAt) return `<span class="crm-follow-status missing">未设置</span>`;
  if (lead.nextFollowAt < today) return `<span class="crm-follow-status overdue">已逾期 ${escapeHtml(lead.nextFollowAt)}</span>`;
  if (lead.nextFollowAt === today) return `<span class="crm-follow-status due">今天 ${escapeHtml(lead.nextFollowTime || "")}</span>`;
  return `<span class="crm-follow-status planned">${escapeHtml(lead.nextFollowAt)}</span>`;
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

function primaryEmailForLead(lead) {
  if (lead?.email) return String(lead.email).trim();
  const emailRecord = Array.isArray(lead?.emailSources) ? lead.emailSources.find((record) => record?.email) : null;
  return String(emailRecord?.email || "").trim();
}

function openCustomerInReview(index) {
  const lead = customers[index];
  if (!lead) return;
  const statusFilter = $("#reviewStatusFilter");
  if (statusFilter) statusFilter.value = "approved";
  selectedReviewLeadId = `approved:${lead.id || index}`;
  showSection("review");
  renderReview();
}

function returnCustomerToReview(index) {
  const lead = customers[index];
  if (!lead) return;
  if (!confirm(`确认把客户 ${lead.company} 退回到线索审核吗？客户池中将不再显示该客户。`)) return;
  const [removed] = customers.splice(index, 1);
  const returnedLead = normalizeLead({
    ...removed,
    stage: "待审核",
    next: "退回审核，等待人工重新判断",
    returnedToReviewAt: new Date().toISOString(),
    returnedFromCrm: true,
    manualApproval: false
  });
  reviewLeads = reviewLeads.filter((item) => String(item.id || "") !== String(returnedLead.id || ""));
  reviewLeads.unshift(returnedLead);
  selectedReviewLeadId = `pending:${returnedLead.id}`;
  const statusFilter = $("#reviewStatusFilter");
  if (statusFilter) statusFilter.value = "pending";
  refreshAllLeadViews();
  showSection("review");
}

function openCustomerInEmail(index) {
  const lead = customers[index];
  if (!lead) return;
  const form = $("#emailForm");
  $("#leadSelect").value = String(index);
  form.company.value = lead.company;
  form.contactName.value = lead.contactName || "";
  form.recipientEmail.value = primaryEmailForLead(lead);
  form.website.value = lead.customerWebsite || lead.sourceUrl || lead.source || "";
  form.websiteText.value = [
    lead.sourceExcerpt,
    lead.researchSummary,
    (lead.evidenceSources || []).slice(0, 4).map((item) => item.excerpt).join(" ")
  ].filter(Boolean).join(" ").slice(0, 2400);
  form.model.value = String(lead.model || "问界 M9").split("/")[0].trim();
  form.channel.value = "Email";
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
    ? new Date(Date.now() + 3 * 86400000).toISOString().slice(0, 10)
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
  renderAfterSales();
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
    sourceMode: raw.sourceMode || raw.discoverySource || "",
    discoverySource: raw.discoverySource || raw.sourceMode || "",
    discoveryJobId: raw.discoveryJobId || raw.jobId || "",
    discoveryJobLabel: raw.discoveryJobLabel || "",
    discoveryJobImportedAt: raw.discoveryJobImportedAt || "",
    platform: raw.platform || "",
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
    customerWebsite: sanitizeCustomerWebsite(raw.customerWebsite || ""),
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
    scoreModelVersion: 7,
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
      : "100分机会模型：进出口资质20、客户匹配27、采购意向20、经营能力14、车型匹配12、可触达性7",
    model: raw.model || "问界 M9",
    createdAt: raw.createdAt || raw.importedAt || raw.discoveredAt || new Date().toISOString(),
    score,
    stage: raw.stage || "待审核",
    next: raw.next || "审核通过后生成英文开发信",
    nextFollowAt: raw.nextFollowAt || "",
    nextFollowTime: raw.nextFollowTime || "10:00",
    assignedTo: raw.assignedTo || "管理员",
    customerTimezone: raw.customerTimezone || "",
    preferredChannel: raw.preferredChannel || "WhatsApp",
    manualApproval: Boolean(raw.manualApproval),
    manualApprovalAt: raw.manualApprovalAt || "",
    lastContactAt: raw.lastContactAt || "",
    followUpHistory: Array.isArray(raw.followUpHistory) ? raw.followUpHistory : [],
    website,
    reason: raw.reason || `${raw.city || raw.country} 的${raw.type || "汽车相关客户"}，建议人工审核后再联系。`
  };
}

function approveLead(index) {
  const lead = reviewLeads.splice(index, 1)[0];
  if (!lead) return;
  customers.unshift({
    ...lead,
    manualApproval: true,
    manualApprovalAt: new Date().toISOString(),
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
  renderReview();
  renderKpis();
  saveState();
}

function rejectLead(index) {
  const lead = reviewLeads.splice(index, 1)[0];
  if (!lead) return;
  rejectedLeads.unshift({ ...lead, stage: "已拒绝" });
  refreshAllLeadViews();
}

async function researchLead(index, options = {}) {
  const lead = reviewLeads[index];
  if (!lead || lead.researching) return;
  const mode = options.mode || "full";
  lead.researching = true;
  renderReview();
  try {
    const response = await apiFetch(`/api/research?${new URLSearchParams({
      company: lead.company,
      country: [lead.city, lead.country].filter(Boolean).join(", "),
      website: lead.customerWebsite || "",
      sourceUrl: lead.sourceUrl || lead.source || "",
      socialUrls: [
        ...(lead.socialAccounts || []),
        ...(lead.socialProfiles || []).map((item) => item.url),
        ...(lead.evidenceSources || []).map((item) => item.url)
      ].filter(Boolean).join(" | "),
      model: lead.model || "",
      type: lead.type || "",
      mode
    })}`);
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || `HTTP ${response.status}`);
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
    if (error instanceof AuthenticationExpiredError) return;
    lead.researchSummary = `全网补全失败：${error.message}。请稍后重试；若持续失败，请检查云端服务状态。`;
    renderReview();
  }
}

async function researchAllLeads() {
  const button = $("#researchAllLeads");
  const pending = reviewLeads
    .map((lead, index) => ({ lead, index }))
    .filter(({ lead }) => !lead.researchAt);
  if (!pending.length) {
    button.textContent = "当前线索已完成核验";
    setTimeout(() => { button.textContent = "全网补全当前线索"; }, 1600);
    return;
  }
  button.disabled = true;
  const batchSize = 4;
  for (let offset = 0; offset < pending.length; offset += batchSize) {
    button.textContent = `正在快速补全 ${Math.min(offset + batchSize, pending.length)} / ${pending.length}`;
    await Promise.all(pending.slice(offset, offset + batchSize).map(({ index }) => researchLead(index, { mode: "fast" })));
  }
  button.disabled = false;
  button.textContent = "全网补全当前线索";
}

async function autoResearchNewLeads(count, sourceLabel, freshnessLabel) {
  if (!count) return;
  const batchSize = 4;
  for (let offset = 0; offset < count; offset += batchSize) {
    const end = Math.min(offset + batchSize, count);
    setFinderProgress({
      percent: 62 + (end / count) * 32,
      stage: "verify",
      title: `正在核验 ${end} / ${count}`,
      message: `${sourceLabel} · ${freshnessLabel}：正在快速核对官网、联系方式与来源证据。`
    });
    await Promise.all(
      Array.from({ length: end - offset }, (_, index) => researchLead(offset + index, { mode: "fast" }))
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
  $("#extraSocialSearchLinks").innerHTML = [
    ["Telegram", "https://www.google.com/search?q=", `site:t.me ${place} car dealer OR motors OR showroom`],
    ["X", "https://www.google.com/search?q=", `site:x.com ${place} car dealer OR motors OR showroom`],
    ["Threads", "https://www.google.com/search?q=", `site:threads.net ${place} car dealer OR motors OR showroom`],
    ["Pinterest", "https://www.google.com/search?q=", `site:pinterest.com ${place} car dealer OR motors OR showroom`],
    ["Reddit", "https://www.google.com/search?q=", `site:reddit.com ${place} car dealer OR motors OR showroom`],
    ["VK", "https://www.google.com/search?q=", `site:vk.com ${place} car dealer OR motors OR showroom`]
  ].map(([platform, baseUrl, query]) =>
    `<a href="${baseUrl}${encodeURIComponent(query)}" target="_blank" rel="noopener noreferrer" data-social-platform="${escapeHtml(platform)}">${escapeHtml(platform)} ↗</a>`
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
  if (domain === "t.me" || domain.includes("telegram")) return "Telegram";
  if (domain.includes("x.com") || domain.includes("twitter")) return "X / Twitter";
  if (domain.includes("threads")) return "Threads";
  if (domain.includes("pinterest")) return "Pinterest";
  if (domain.includes("reddit")) return "Reddit";
  if (domain.includes("vk.com")) return "VK";
  return "官网";
}

function inferSocialNameFromUrl(url) {
  try {
    const parsed = new URL(url);
    const ignored = new Set(["company", "in", "pages", "channel", "user", "c"]);
    const parts = parsed.pathname.split("/").filter(Boolean);
    const handle = [...parts].reverse().find((part) => !ignored.has(part.toLowerCase())) || "";
    return decodeURIComponent(handle)
      .replace(/^@/, "")
      .replace(/[-_.]+/g, " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase())
      .trim();
  } catch {
    return "";
  }
}

function autoFillSocialFormFromUrl() {
  const form = $("#socialLeadForm");
  if (!form) return;
  const url = safeHttpUrl(form.pageUrl.value);
  if (!url) return;
  const platform = socialPlatformFromUrl(url);
  if (["Facebook", "Instagram", "TikTok", "YouTube", "LinkedIn"].includes(platform)) {
    form.platform.value = platform;
  }
  if (form.accountType.value === "自动判断") {
    const path = new URL(url).pathname.toLowerCase();
    form.accountType.value = platform === "LinkedIn" && path.startsWith("/in/")
      ? "个人决策人"
      : "公司账号";
  }
  if (!form.company.value.trim()) {
    form.company.value = inferSocialNameFromUrl(url);
  }
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
  const platformDomains = [
    "youtube.com", "youtu.be", "facebook.com", "instagram.com", "tiktok.com", "linkedin.com",
    "t.me", "telegram.me", "telegram.dog", "x.com", "twitter.com", "threads.net",
    "pinterest.com", "reddit.com", "vk.com"
  ];
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
  const localHosts = new Set(["localhost", "127.0.0.1", "::1"]);
  if (!localHosts.has(window.location.hostname)) {
    status.textContent = "云端公开搜索可用";
    status.title = "Chrome 登录态采集器只连接本机工作台；云端五平台公开搜索不需要扩展。";
    return;
  }
  try {
    const response = await apiFetch("/api/social-captures", { cache: "no-store" });
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

  const messages = {
    Email: `Subject: Dealer CIF quotation for ${profile.english} from China\n\nHi ${recipient},\n\nI found your website and noticed that you focus on ${traits.join(", ")}. We supply HIMA smart EV models from China, including ${profile.english}.\n\n${profile.english} is ${profile.pitch}. I believe it could be a strong fit for your market.\n\nWould it be relevant for your team to review available colors, export specifications and a dealer CIF quotation?\n\nBest regards`,
    WhatsApp: `Hi ${recipient}, I noticed your ${traits.join(" / ")} business. We export HIMA smart EVs from China, including ${profile.english}. Would you like me to send available colors and a dealer CIF price?`,
    "Instagram DM": `Hi ${recipient} — your ${traits[0]} caught my attention. We supply ${profile.english} smart EVs from China. Open to receiving a short dealer price/spec sheet?`,
    LinkedIn: `Hi ${recipient}, I came across your automotive business and thought ${profile.english} may fit your portfolio. We support dealer export specifications and CIF quotations from China. Would a brief product and pricing overview be useful?`
  };
  const english = messages[data.channel] || messages.WhatsApp;
  const followUps = [
    {
      day: "第1天",
      text: data.channel === "Email"
        ? `Hi ${recipient}, just checking whether the ${profile.english} dealer quotation would be relevant for your team.`
        : `Hi ${recipient}, would you like a quick ${profile.english} price and color list?`
    },
    {
      day: "第3天",
      text: `We can share export specifications, available colors and a CIF reference for ${profile.english}. Which destination port do you normally use?`
    },
    {
      day: "第7天",
      text: `Last follow-up from my side: should I keep you updated on ${profile.english} stock and dealer pricing, or is another HIMA model more relevant?`
    }
  ];

  const chinese = `中文意思：我看到你们官网主要做${traits.join("、")}。我们供应中国华为系鸿蒙智行新能源车型，包括${data.model}。这款车的优势是${profile.chinese}。想问你们是否有兴趣了解经销商 CIF 报价、现车颜色和出口细节。`;

  return { insight, english, chinese, followUps };
}

function emailDraftFromGeneratedText(text, data = {}) {
  const lines = String(text || "").replace(/\r\n/g, "\n").split("\n");
  const subjectIndex = lines.findIndex((line) => /^subject\s*:/i.test(line.trim()));
  const subject = subjectIndex >= 0
    ? lines[subjectIndex].replace(/^subject\s*:\s*/i, "").trim()
    : `HIMA smart EV export proposal for ${data.company || "your team"}`;
  const body = subjectIndex >= 0
    ? lines.filter((_, index) => index !== subjectIndex).join("\n").replace(/^\s+/, "")
    : lines.join("\n");
  return {
    to: String(data.recipientEmail || "").trim(),
    subject,
    body
  };
}

function outlookMailtoUrl(draft) {
  const params = new URLSearchParams({
    subject: draft.subject || "",
    body: draft.body || ""
  });
  return `mailto:${encodeURIComponent(draft.to || "")}?${params.toString()}`;
}

function openOutlookDraft(data = Object.fromEntries(new FormData($("#emailForm")).entries())) {
  const text = $("#englishLetter")?.textContent.trim() || "";
  const status = $("#outlookDraftStatus");
  if (!text) {
    if (status) status.textContent = "请先生成英文开发信。";
    return;
  }
  const draft = emailDraftFromGeneratedText(text, data);
  window.location.href = outlookMailtoUrl(draft);
  if (status) {
    status.textContent = `已请求打开 Outlook 编辑窗口${draft.to ? `，收件人：${draft.to}` : "，客户邮箱未发现，收件人请手动填写"}。`;
  }
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
  const configuration = String(values.configuration || "").trim();
  const deliveryDays = Number(values.deliveryDays || 45);
  const paymentTerms = String(values.paymentTerms || "30% deposit, 70% before shipment");
  const quoteNotes = String(values.quoteNotes || "").trim();
  const sellerCompany = String(values.sellerCompany || "HIMA Global").trim();
  const sellerContact = String(values.sellerContact || "").trim();
  const quoteStatus = String(values.quoteStatus || "Draft");
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
    configuration,
    deliveryDays,
    paymentTerms,
    quoteNotes,
    sellerCompany,
    sellerContact,
    quoteStatus,
    createdAt: new Date().toLocaleString(),
    english: `CIF quotation for ${productProfiles[model]?.english || model}: ${money(total)} to ${destination}. Payment: ${paymentTerms}. Estimated delivery: ${deliveryDays} days. Destination import duty, VAT, registration and local delivery are excluded.`
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
      <div class="wide"><span>配置/颜色</span><strong>${escapeHtml(configuration || "待客户确认")}</strong></div>
      <div class="wide"><span>目的港</span><strong>${escapeHtml(destination)}</strong></div>
      <div class="wide"><span>付款条款</span><strong>${escapeHtml(paymentTerms)}</strong></div>
      <div><span>预计交期</span><strong>${deliveryDays} 天</strong></div>
      <div><span>报价状态</span><strong>${escapeHtml(quoteStatus)}</strong></div>
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
    <p class="quote-disclaimer">此结果仅作报价参考，不包含目的国进口关税、VAT、注册及本地交付费用。${quoteNotes ? `备注：${escapeHtml(quoteNotes)}` : ""}</p>
  `;
}

function quoteDocumentHtml(quote) {
  return `<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(quote.id)} Quotation</title>
  <style>body{font-family:Arial,sans-serif;color:#18222d;max-width:900px;margin:40px auto;padding:0 28px}h1{margin-bottom:4px}.meta{color:#66717c}.total{font-size:28px;font-weight:700;margin:24px 0}table{width:100%;border-collapse:collapse}td{padding:10px;border-bottom:1px solid #ddd}td:first-child{color:#66717c;width:35%}.note{margin-top:28px;padding:16px;background:#f5f7f9;line-height:1.6}</style>
  </head><body><h1>Commercial Quotation</h1><p class="meta">${escapeHtml(quote.sellerCompany || "HIMA Global")}${quote.sellerContact ? ` · ${escapeHtml(quote.sellerContact)}` : ""}</p>
  <p class="meta">Quotation No. ${escapeHtml(quote.id)} · ${escapeHtml(quote.createdAt)} · Status: ${escapeHtml(quote.quoteStatus || "Draft")}</p>
  <div class="total">${money(quote.total)} CIF ${escapeHtml(quote.destination)}</div><table>
  <tr><td>Customer</td><td>${escapeHtml(quote.customer)}</td></tr><tr><td>Model</td><td>${escapeHtml(productProfiles[quote.model]?.english || quote.model)}</td></tr>
  <tr><td>Configuration / Color</td><td>${escapeHtml(quote.configuration || "To be confirmed")}</td></tr><tr><td>Quantity</td><td>${escapeHtml(quote.qty)}</td></tr>
  <tr><td>Unit reference price</td><td>${money(quote.total / Math.max(1, quote.qty))}</td></tr><tr><td>Payment terms</td><td>${escapeHtml(quote.paymentTerms)}</td></tr>
  <tr><td>Estimated delivery</td><td>${escapeHtml(quote.deliveryDays)} days</td></tr><tr><td>Valid until</td><td>${escapeHtml(quote.validUntil)}</td></tr></table>
  <div class="note">${escapeHtml(quote.english)}${quote.quoteNotes ? `<br><br>Notes: ${escapeHtml(quote.quoteNotes)}` : ""}</div></body></html>`;
}

function downloadQuoteDocument(quote = lastQuote) {
  if (!quote) return;
  downloadFile(quoteDocumentHtml(quote), `${quote.id}-${quote.customer || "customer"}.html`, "text/html;charset=utf-8");
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
      <td>${escapeHtml(quote.deliveryDays || 45)} 天</td>
      <td>${escapeHtml(quote.validUntil || "未设置")}</td>
      <td>${escapeHtml(quote.createdAt)}</td>
      <td><div class="quote-row-actions"><button type="button" data-quote-download="${index}">导出</button><button class="quote-delete" type="button" data-quote-delete="${index}" aria-label="删除这个报价版本">删除</button></div></td>
    </tr>
  `).join("") : `<tr><td colspan="9" class="quote-empty">暂无报价版本</td></tr>`;
}

function renderFollowTasks() {
  const box = $("#followTasks");
  if (!box) return;
  const today = new Date().toISOString().slice(0, 10);
  const defaultNextDate = new Date(Date.now() + 3 * 86400000).toISOString().slice(0, 10);
  const filter = $("#followFilter")?.value || "due";
  const allTasks = customers
    .map((lead, index) => ({ lead, index }))
    .filter(({ lead }) => !["已成交", "已流失"].includes(lead.stage));
  const dueCount = allTasks.filter(({ lead }) => !lead.nextFollowAt || lead.nextFollowAt <= today).length;
  const overdueCount = allTasks.filter(({ lead }) => lead.nextFollowAt && lead.nextFollowAt < today).length;
  const tasks = allTasks
    .filter(({ lead }) => filter === "all"
      || (filter === "recent" ? (lead.followUpHistory || []).length : !lead.nextFollowAt || lead.nextFollowAt <= today))
    .sort((a, b) => String(a.lead.nextFollowAt || "").localeCompare(String(b.lead.nextFollowAt || "")))
    .slice(0, 30);
  const summary = $("#followSummary");
  if (summary) summary.innerHTML = `<span>当前显示 <strong>${tasks.length}</strong></span><span>今日到期 <strong>${dueCount}</strong></span><span class="${overdueCount ? "overdue" : ""}">已逾期 <strong>${overdueCount}</strong></span>`;
  box.innerHTML = tasks.length ? tasks.map(({ lead, index }) => `
    <article class="${lead.nextFollowAt && lead.nextFollowAt < today ? "follow-overdue" : ""}">
      <span>${escapeHtml(lead.stage || "待跟进")}${lead.score >= 80 ? " · A 级优先" : ""}</span>
      <h3>${escapeHtml(lead.company)}</h3>
      <p>建议动作：${escapeHtml(lead.next || `根据客户官网信息生成英文开发信，推荐${lead.model}。`)}</p>
      <small>计划跟进：${escapeHtml(lead.nextFollowAt || "今天")}${lead.lastContactAt ? ` · 最近联系：${escapeHtml(lead.lastContactAt)}` : ""}</small>
      <div class="follow-context">
        <label>负责人 <input data-follow-owner="${index}" value="${escapeHtml(lead.assignedTo || "管理员")}"></label>
        <label>客户时区 <input data-follow-timezone="${index}" value="${escapeHtml(lead.customerTimezone || "")}" placeholder="例如 UTC+4"></label>
        <label>渠道
          <select data-follow-channel="${index}">
            ${["WhatsApp", "Email", "Instagram DM", "LinkedIn"].map((channel) => `<option ${channel === lead.preferredChannel ? "selected" : ""}>${channel}</option>`).join("")}
          </select>
        </label>
        <label>提醒时间 <input data-follow-time="${index}" type="time" value="${escapeHtml(lead.nextFollowTime || "10:00")}"></label>
      </div>
      <div class="follow-entry">
        <select data-follow-outcome="${index}">
          <option value="已发送消息">已发送消息</option><option value="客户有回复">客户有回复</option>
          <option value="需要报价">需要报价</option><option value="继续跟进">继续跟进</option>
          <option value="暂缓">暂缓</option><option value="无效客户">无效客户</option>
        </select>
        <input data-follow-date="${index}" type="date" value="${escapeHtml(lead.nextFollowAt && lead.nextFollowAt > today ? lead.nextFollowAt : defaultNextDate)}">
        <input data-follow-note="${index}" placeholder="记录客户反馈或下一步">
      </div>
      <div class="follow-save-row">
        <button type="button" data-follow-action="record" data-index="${index}">保存记录</button>
      </div>
      ${(lead.followUpHistory || []).length ? `<details class="follow-history"><summary>查看历史（${lead.followUpHistory.length}）</summary>${lead.followUpHistory.slice(0, 5).map((item) => `<p><b>${escapeHtml(item.at)}</b> · ${escapeHtml(item.outcome)}${item.note ? ` · ${escapeHtml(item.note)}` : ""}</p>`).join("")}</details>` : ""}
      <div class="task-actions">
        <button type="button" data-follow-action="email" data-index="${index}">写开发信</button>
        ${lead.stage === "准备联系" ? `<button type="button" data-follow-action="contacted" data-index="${index}">标记已联系</button>` : ""}
        <button type="button" data-follow-action="quote" data-index="${index}">进入报价</button>
      </div>
    </article>
  `).join("") : `<p class="empty">暂无今日跟进。线索审核通过后，会自动生成跟进任务。</p>`;
}

function recordFollowUp(index) {
  const lead = customers[index];
  if (!lead) return;
  const button = document.querySelector(`[data-follow-action="record"][data-index="${index}"]`);
  const outcome = document.querySelector(`[data-follow-outcome="${index}"]`)?.value || "继续跟进";
  const nextDate = document.querySelector(`[data-follow-date="${index}"]`)?.value || new Date(Date.now() + 3 * 86400000).toISOString().slice(0, 10);
  const nextTime = document.querySelector(`[data-follow-time="${index}"]`)?.value || "10:00";
  const assignedTo = document.querySelector(`[data-follow-owner="${index}"]`)?.value.trim() || "管理员";
  const customerTimezone = document.querySelector(`[data-follow-timezone="${index}"]`)?.value.trim() || "";
  const preferredChannel = document.querySelector(`[data-follow-channel="${index}"]`)?.value || "WhatsApp";
  const note = document.querySelector(`[data-follow-note="${index}"]`)?.value.trim() || "";
  const today = new Date().toISOString().slice(0, 10);
  lead.followUpHistory = [{
    at: today,
    outcome,
    note,
    nextFollowAt: nextDate,
    nextFollowTime: nextTime,
    assignedTo,
    preferredChannel
  }, ...(lead.followUpHistory || [])].slice(0, 100);
  lead.lastContactAt = today;
  lead.nextFollowAt = nextDate;
  lead.nextFollowTime = nextTime;
  lead.assignedTo = assignedTo;
  lead.customerTimezone = customerTimezone;
  lead.preferredChannel = preferredChannel;
  if (outcome === "客户有回复") lead.stage = "有回复";
  if (outcome === "需要报价") lead.stage = "报价中";
  if (outcome === "暂缓") lead.stage = "暂缓";
  if (outcome === "无效客户") lead.stage = "已流失";
  lead.next = note || defaultNextAction(lead.stage);
  if (button) {
    button.disabled = true;
    button.textContent = "已保存";
  }
  refreshAllLeadViews();
}

function summarizeKpiState(state) {
  const stateReviewLeads = Array.isArray(state?.reviewLeads) ? state.reviewLeads : [];
  const stateCustomers = Array.isArray(state?.customers) ? state.customers : [];
  const stateQuotes = Array.isArray(state?.quotes) ? state.quotes : [];
  const stateAfterSales = Array.isArray(state?.afterSalesOrders) ? state.afterSalesOrders : [];
  const contactedStages = new Set(["已联系", "有回复", "报价中", "谈判中", "已成交"]);
  const repliedStages = new Set(["有回复", "报价中", "谈判中", "已成交"]);
  return {
    pending: stateReviewLeads.length,
    verified: [...stateReviewLeads, ...stateCustomers].filter((lead) => lead.researchAt).length,
    customers: stateCustomers.length,
    contacted: stateCustomers.filter((lead) => contactedStages.has(lead.stage)).length,
    replied: stateCustomers.filter((lead) => repliedStages.has(lead.stage)).length,
    quotes: stateQuotes.length,
    afterSales: stateAfterSales.length,
    completed: stateCustomers.filter((lead) => lead.stage === "已成交").length
  };
}

function formatSyncTime(value) {
  if (!value) return "未同步";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  const pad = (number) => String(number).padStart(2, "0");
  return `${date.getFullYear()}年${pad(date.getMonth() + 1)}月${pad(date.getDate())}日 ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function renderAdminKpis() {
  const panel = $("#adminKpiPanel");
  if (!panel) return;
  const isAdmin = currentSession?.role === "admin";
  panel.hidden = !isAdmin;
  if (!isAdmin) return;
  const status = $("#adminKpiStatus");
  const rows = $("#adminKpiRows");
  const summary = $("#adminKpiSummary");
  if (!adminKpiSnapshot) {
    if (status) status.textContent = adminKpiLoading ? "正在读取团队数据…" : "等待读取团队数据";
    if (rows) rows.innerHTML = `<tr><td colspan="10">正在读取团队数据…</td></tr>`;
    if (summary) summary.innerHTML = "";
    if (!adminKpiLoading) refreshAdminKpis();
    return;
  }
  const users = Array.isArray(adminKpiSnapshot.users) ? adminKpiSnapshot.users : [];
  const totals = adminKpiSnapshot.totals || {};
  if (adminKpiSnapshot.error) {
    if (status) status.textContent = `团队KPI读取失败：${adminKpiSnapshot.error}`;
    if (rows) rows.innerHTML = `<tr><td colspan="10">${escapeHtml(adminKpiSnapshot.error)}</td></tr>`;
    if (summary) summary.innerHTML = "";
    return;
  }
  if (status) status.textContent = `已同步 ${users.length} 位销售人员的数据`;
  if (summary) {
    summary.innerHTML = `
      <div><span>团队待审核</span><strong>${Number(totals.pending || 0)}</strong></div>
      <div><span>团队客户</span><strong>${Number(totals.customers || 0)}</strong></div>
      <div><span>团队已联系</span><strong>${Number(totals.contacted || 0)}</strong></div>
      <div><span>团队有回复</span><strong>${Number(totals.replied || 0)}</strong></div>
      <div><span>团队报价</span><strong>${Number(totals.quotes || 0)}</strong></div>
      <div><span>成交/售后</span><strong>${Number(totals.completed || 0)} / ${Number(totals.afterSales || 0)}</strong></div>
    `;
  }
  if (rows) {
    rows.innerHTML = users.length ? users.map((user) => `
      <tr>
        <td><strong>${escapeHtml(user.username || "-")}</strong><br><small>${user.role === "admin" ? "管理员" : "销售"}</small></td>
        <td><span class="user-status ${user.status === "disabled" ? "disabled" : ""}">${user.status === "disabled" ? "已禁用" : "启用中"}</span></td>
        <td>${Number(user.pending || 0)}</td>
        <td>${Number(user.verified || 0)}</td>
        <td><strong>${Number(user.customers || 0)}</strong></td>
        <td>${Number(user.contacted || 0)}</td>
        <td>${Number(user.replied || 0)}</td>
        <td>${Number(user.quotes || 0)}</td>
        <td>${Number(user.completed || 0)} / ${Number(user.afterSales || 0)}</td>
        <td>${escapeHtml(formatSyncTime(user.updatedAt))}</td>
      </tr>
    `).join("") : `<tr><td colspan="10">还没有销售人员数据。</td></tr>`;
  }
}

async function refreshAdminKpis({ forceSync = false } = {}) {
  if (currentSession?.role !== "admin" || adminKpiLoading) return;
  adminKpiLoading = true;
  const status = $("#adminKpiStatus");
  if (status) status.textContent = forceSync ? "正在同步并读取团队数据…" : "正在读取团队数据…";
  try {
    if (forceSync && cloudStateReady) {
      await pushCloudState(workspaceStateSnapshot());
    }
    const response = await apiFetch("/api/admin/kpi", { cache: "no-store" });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    adminKpiSnapshot = result;
  } catch (error) {
    adminKpiSnapshot = { users: [], totals: {}, error: error.message };
    if (status) status.textContent = `团队KPI读取失败：${error.message}`;
  } finally {
    adminKpiLoading = false;
    renderKpis();
  }
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
  if (currentSession?.role === "admin" && adminKpiSnapshot?.totals) {
    const totals = adminKpiSnapshot.totals;
    pending.textContent = Number(totals.pending || 0);
    $("#kpiVerified").textContent = Number(totals.verified || 0);
    $("#kpiCustomers").textContent = Number(totals.customers || 0);
    $("#kpiContacted").textContent = Number(totals.contacted || 0);
    $("#kpiReplied").textContent = Number(totals.replied || 0);
    $("#kpiQuotes").textContent = Number(totals.quotes || 0);
  }
  const rateMetrics = currentSession?.role === "admin" && adminKpiSnapshot?.totals
    ? adminKpiSnapshot.totals
    : { pending: reviewLeads.length, customers: customers.length, contacted, replied };
  const approvalBase = Number(rateMetrics.pending || 0) + Number(rateMetrics.customers || 0);
  const approvalRate = approvalBase ? Math.round(Number(rateMetrics.customers || 0) / approvalBase * 100) : 0;
  const replyRate = Number(rateMetrics.contacted || 0)
    ? Math.round(Number(rateMetrics.replied || 0) / Number(rateMetrics.contacted || 0) * 100)
    : 0;
  const hasAnyData = reviewLeads.length || customers.length || quoteHistory.length || afterSalesOrders.length;
  const nextRecommendation = !hasAnyData
    ? "当前还没有客户数据。请先运行自动获客，或从已完成任务导入线索。"
    : reviewLeads.some((lead) => !lead.researchAt)
    ? `还有 ${reviewLeads.filter((lead) => !lead.researchAt).length} 条线索未完成全网核验。`
    : customers.some((lead) => lead.stage === "准备联系")
      ? `还有 ${customers.filter((lead) => lead.stage === "准备联系").length} 个客户尚未首次触达。`
      : "当前客户均已处理，可继续新增高质量线索或查看到期跟进。";
  $("#kpiInsight").innerHTML = `
    <div><span>审核通过率</span><strong>${approvalRate}%</strong></div>
    <div><span>客户回复率</span><strong>${replyRate}%</strong></div>
    <div class="wide"><span>当前最重要动作</span><strong>${escapeHtml(nextRecommendation)}</strong></div>
  `;
  renderAdminKpis();
}

function bindNavigation() {
  if (navigationBound) return;
  navigationBound = true;
  $$("[data-section]").forEach((button) => {
    button.addEventListener("click", () => showSection(button.dataset.section));
  });
}

function showSection(id) {
  $$(".section").forEach((section) => section.classList.toggle("active", section.id === id));
  $$(".nav button").forEach((button) => button.classList.toggle("active", button.dataset.section === id));
  $("#userManagementNav")?.classList.toggle("active", id === "user-management");
  if (window.location.hash !== `#${id}`) {
    history.replaceState(null, "", `#${id}`);
  }
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function showRequestedSection() {
  const requestedSection = window.location.hash.slice(1);
  if (requestedSection && document.getElementById(requestedSection)?.classList.contains("section")) {
    showSection(requestedSection);
  }
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
    linkedin: "LinkedIn",
    telegram: "Telegram",
    twitter: "X / Twitter",
    threads: "Threads",
    pinterest: "Pinterest",
    reddit: "Reddit",
    vk: "VK"
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

function discoveryJobStateLabels() {
  return {
    queued: "排队中",
    running: "运行中",
    completed: "已完成",
    failed: "失败",
    canceled: "已取消"
  };
}

function isScheduledDiscoveryJob(job) {
  return discoverySchedules.some((schedule) => schedule.lastJobId && schedule.lastJobId === job.id);
}

function discoveryJobResultText(job) {
  const count = Number(job.result?.count || job.result?.leads?.length || 0);
  if (job.imported) return `已导入 ${count} 条`;
  if (job.status === "completed") return count ? `发现 ${count} 条` : "无可导入线索";
  if (job.status === "failed") return "执行失败";
  if (job.status === "canceled") return "已取消";
  return `${Number(job.progress || 0)}%`;
}

function renderDiscoveryHistory() {
  const box = $("#finderHistoryGrid");
  if (!box) return;
  const countLabel = $("#finderHistoryCount");
  const stateLabels = discoveryJobStateLabels();
  const scheduleCards = discoverySchedules
    .filter((schedule) => !schedule.lastJobId)
    .map((schedule) => ({
      kind: "定时抓取",
      id: "",
      status: schedule.enabled ? "已启用" : "已暂停",
      time: schedule.updatedAt || schedule.createdAt || schedule.nextRunAt,
      country: schedule.country,
      model: schedule.model,
      sourceMode: schedule.sourceMode,
      result: schedule.enabled
        ? `下次 ${formatJobTime(schedule.nextRunAt)}`
        : "计划暂停"
    }));
  const jobCards = discoveryJobs.map((job) => ({
    kind: isScheduledDiscoveryJob(job) ? "定时抓取" : "自动抓取",
    id: job.id || "",
    status: stateLabels[job.status] || job.status || "未知",
    state: job.status || "",
    time: job.updatedAt || job.createdAt,
    country: job.country,
    model: job.model,
    sourceMode: job.sourceMode,
    result: discoveryJobResultText(job)
  }));
  const allCards = [...jobCards, ...scheduleCards]
    .sort((a, b) => new Date(b.time || 0) - new Date(a.time || 0));
  const pageCount = Math.max(1, Math.ceil(allCards.length / FINDER_HISTORY_PAGE_SIZE));
  finderHistoryPage = Math.max(1, Math.min(finderHistoryPage, pageCount));
  const pageStart = (finderHistoryPage - 1) * FINDER_HISTORY_PAGE_SIZE;
  const cards = allCards.slice(pageStart, pageStart + FINDER_HISTORY_PAGE_SIZE);
  if (countLabel) countLabel.textContent = `${allCards.length} 条`;
  const pageLabel = $("#finderHistoryPage");
  if (pageLabel) pageLabel.textContent = `${finderHistoryPage} / ${pageCount}`;
  const prev = $("#finderHistoryPrev");
  const next = $("#finderHistoryNext");
  if (prev) prev.disabled = finderHistoryPage <= 1;
  if (next) next.disabled = finderHistoryPage >= pageCount;
  box.innerHTML = cards.length ? cards.map((card) => `
    <article class="finder-history-card ${escapeHtml(card.state || "")} ${card.id && activeDiscoveryJobFilter === card.id ? "active" : ""}" ${card.id ? `data-discovery-history-job="${escapeHtml(card.id)}" role="button" tabindex="0"` : ""}>
      <div>
        <span>${escapeHtml(card.kind)}</span>
        <b>${escapeHtml(card.status)}</b>
      </div>
      <strong>${escapeHtml(card.country || "未指定市场")} · ${escapeHtml(card.model || "未指定车型")}</strong>
      <p>${escapeHtml(discoverySourceLabel(card.sourceMode))}</p>
      <footer>
        <span>${escapeHtml(formatJobTime(card.time))}</span>
        <em>${escapeHtml(card.result || "-")}</em>
      </footer>
    </article>
  `).join("") : `<p class="empty">暂无搜索记录。</p>`;
}

function applyDiscoveryHistoryFilter(jobId) {
  activeDiscoveryJobFilter = jobId || "all";
  renderLeads();
  renderDiscoveryHistory();
  $("#leadList")?.closest(".panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function focusDiscoveryJob(jobId) {
  const index = discoveryJobs.findIndex((job) => String(job.id || "") === String(jobId || ""));
  if (index >= 0) {
    discoveryJobPage = Math.floor(index / DISCOVERY_JOBS_PAGE_SIZE) + 1;
  }
  renderDiscoveryJobs();
  $("#discoveryJobList")?.closest(".panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
  const row = jobId ? document.querySelector(`[data-discovery-job="${CSS.escape(jobId)}"]`) : null;
  if (row) {
    row.classList.add("active");
    window.setTimeout(() => row.classList.remove("active"), 1800);
  }
}

function openDiscoveryHistoryJob(jobId) {
  const job = discoveryJobs.find((item) => String(item.id || "") === String(jobId || ""));
  if (!job) return;
  if (job.imported) {
    applyDiscoveryHistoryFilter(jobId);
    return;
  }
  focusDiscoveryJob(jobId);
}

function renderDiscoveryJobs() {
  const box = $("#discoveryJobList");
  if (!box) return;
  const stateLabels = discoveryJobStateLabels();
  const pageCount = Math.max(1, Math.ceil(discoveryJobs.length / DISCOVERY_JOBS_PAGE_SIZE));
  discoveryJobPage = Math.max(1, Math.min(discoveryJobPage, pageCount));
  const pageStart = (discoveryJobPage - 1) * DISCOVERY_JOBS_PAGE_SIZE;
  const visibleJobs = discoveryJobs.slice(pageStart, pageStart + DISCOVERY_JOBS_PAGE_SIZE);
  const count = $("#discoveryJobCount");
  if (count) count.textContent = `${discoveryJobs.length} 个历史任务`;
  const pageLabel = $("#discoveryPageLabel");
  if (pageLabel) pageLabel.textContent = `${discoveryJobPage} / ${pageCount}`;
  const prevPage = $("#discoveryPrevPage");
  const nextPage = $("#discoveryNextPage");
  if (prevPage) prevPage.disabled = discoveryJobPage <= 1;
  if (nextPage) nextPage.disabled = discoveryJobPage >= pageCount;
  box.innerHTML = visibleJobs.length ? visibleJobs.map((job) => {
    const count = Number(job.result?.count || job.result?.leads?.length || 0);
    const canImport = job.status === "completed" && !job.imported && count > 0;
    const canRetry = ["failed", "canceled"].includes(job.status);
    const canCancel = ["queued", "running"].includes(job.status);
    const diagnostics = job.result?.diagnostics;
    const actionLabel = job.imported
      ? "已导入"
      : canImport
        ? `导入 ${count} 条`
        : canRetry
          ? "重新执行"
          : canCancel
            ? "取消任务"
          : job.status === "completed"
            ? "无可导入线索"
            : `${Number(job.progress || 0)}%`;
    const actionAttribute = canImport
      ? `data-import-job="${escapeHtml(job.id)}"`
      : canRetry
        ? `data-retry-job="${escapeHtml(job.id)}"`
        : canCancel
          ? `data-cancel-job="${escapeHtml(job.id)}"`
        : "";
    return `
      <article class="discovery-job" data-discovery-job="${escapeHtml(job.id || "")}">
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
          ${diagnostics ? `
            <details class="job-diagnostics">
              <summary>失败诊断：${escapeHtml(diagnostics.category || "执行异常")}</summary>
              <p>${escapeHtml(diagnostics.suggestion || "")}</p>
              <small>来源：${escapeHtml(discoverySourceLabel(diagnostics.sourceMode))} · ${escapeHtml(formatJobTime(diagnostics.failedAt))}</small>
            </details>
          ` : ""}
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
  renderDiscoveryHistory();
}

function scheduleIntervalLabel(minutes) {
  const value = Number(minutes || 0);
  if (value === 60) return "每 1 小时";
  if (value === 360) return "每 6 小时";
  if (value === 720) return "每 12 小时";
  if (value === 1440) return "每天";
  if (value === 10080) return "每周";
  if (value % 1440 === 0) return `每 ${value / 1440} 天`;
  if (value % 60 === 0) return `每 ${value / 60} 小时`;
  return `每 ${value} 分钟`;
}

function renderDiscoverySchedules() {
  const box = $("#scheduleList");
  if (!box) return;
  const status = $("#scheduleStatus");
  const enabledCount = discoverySchedules.filter((schedule) => schedule.enabled).length;
  const pageCount = Math.max(1, Math.ceil(discoverySchedules.length / DISCOVERY_SCHEDULES_PAGE_SIZE));
  discoverySchedulePage = Math.max(1, Math.min(discoverySchedulePage, pageCount));
  const pageStart = (discoverySchedulePage - 1) * DISCOVERY_SCHEDULES_PAGE_SIZE;
  const visibleSchedules = discoverySchedules.slice(pageStart, pageStart + DISCOVERY_SCHEDULES_PAGE_SIZE);
  if (status) status.textContent = discoverySchedules.length
    ? `${enabledCount} 个启用 / ${discoverySchedules.length} 个计划`
    : "未设置计划";
  const pageLabel = $("#schedulePageLabel");
  if (pageLabel) pageLabel.textContent = `${discoverySchedulePage} / ${pageCount}`;
  const prevPage = $("#schedulePrevPage");
  const nextPage = $("#scheduleNextPage");
  if (prevPage) prevPage.disabled = discoverySchedulePage <= 1;
  if (nextPage) nextPage.disabled = discoverySchedulePage >= pageCount;
  box.innerHTML = visibleSchedules.length ? visibleSchedules.map((schedule) => `
    <article class="schedule-item">
      <div>
        <div class="schedule-title">
          <strong>${escapeHtml(schedule.country || "未指定市场")} · ${escapeHtml(schedule.model || "未指定车型")}</strong>
          <span class="${schedule.enabled ? "enabled" : "paused"}">${schedule.enabled ? "已启用" : "已暂停"}</span>
        </div>
        <p>${escapeHtml(discoverySourceLabel(schedule.sourceMode))} · ${escapeHtml(scheduleIntervalLabel(schedule.intervalMinutes))}</p>
        <small>下次执行：${escapeHtml(formatJobTime(schedule.nextRunAt))}${schedule.lastRunAt ? ` · 上次执行：${escapeHtml(formatJobTime(schedule.lastRunAt))}` : ""}</small>
      </div>
      <div class="schedule-actions">
        <button class="ghost compact" type="button" data-toggle-schedule="${escapeHtml(schedule.id)}">
          ${schedule.enabled ? "暂停" : "启用"}
        </button>
        <button class="danger-button compact" type="button" data-delete-schedule="${escapeHtml(schedule.id)}">删除</button>
      </div>
    </article>
  `).join("") : `<p class="empty">暂无定时计划。设置左侧找客户条件后，点击“保存定时抓取计划”。</p>`;
  renderDiscoveryHistory();
}

function currentDiscoveryPayload() {
  const form = $("#finderForm");
  const data = Object.fromEntries(new FormData(form).entries());
  const words = generateKeywords(data.goal, data.country, data.model);
  return {
    goal: data.goal,
    country: data.country,
    model: data.model,
    sourceMode: data.sourceMode,
    accountScope: data.accountScope,
    freshness: data.freshness,
    resultLimit: 90,
    keywords: words.join(" | ")
  };
}

async function loadDiscoverySchedules() {
  const response = await apiFetch("/api/discover/schedules", { cache: "no-store" });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  discoverySchedules = Array.isArray(result.schedules) ? result.schedules : [];
  renderDiscoverySchedules();
  return discoverySchedules;
}

async function saveDiscoverySchedule(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const submitButton = form.querySelector('button[type="submit"]');
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = "正在保存计划";
  }
  try {
    const formData = Object.fromEntries(new FormData(form).entries());
    const response = await apiFetch("/api/discover/schedules", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        payload: currentDiscoveryPayload(),
        intervalMinutes: formData.intervalMinutes,
        startMode: formData.startMode,
        enabled: Boolean(formData.enabled)
      })
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    discoverySchedulePage = 1;
    await loadDiscoverySchedules();
    await loadDiscoveryJobs().catch(() => undefined);
    const status = $("#scheduleStatus");
    if (status) status.textContent = "计划已保存";
  } catch (error) {
    const status = $("#scheduleStatus");
    if (status) status.textContent = `保存失败：${error.message}`;
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = "保存定时抓取计划";
    }
  }
}

async function toggleDiscoverySchedule(scheduleId) {
  const schedule = discoverySchedules.find((item) => item.id === scheduleId);
  if (!schedule) return;
  const response = await apiFetch("/api/discover/schedules", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      id: schedule.id,
      payload: schedule.payload,
      intervalMinutes: schedule.intervalMinutes,
      startMode: "delay",
      enabled: !schedule.enabled
    })
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  await loadDiscoverySchedules();
}

async function deleteDiscoverySchedule(scheduleId) {
  const response = await apiFetch("/api/discover/schedules", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "delete", id: scheduleId })
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  await loadDiscoverySchedules();
}

async function loadDiscoveryJobs() {
  const response = await apiFetch("/api/discover/jobs", { cache: "no-store" });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  discoveryJobs = Array.isArray(result.jobs) ? result.jobs : [];
  renderDiscoveryJobs();
  renderReviewFilterOptions();
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
  await apiFetch("/api/discover/mark-imported", {
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
    const response = await apiFetch("/api/discover/retry", {
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
    const response = await apiFetch("/api/discover/cancel", {
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
    const response = await apiFetch("/api/discover/delete", {
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

function discoveryJobLabel(job) {
  if (!job) return "";
  return `${job.country || "未指定市场"} · ${job.model || "未指定车型"} · ${formatJobTime(job.createdAt || job.updatedAt)}`;
}

function mergeDiscoveryResult(result, sourceMode = "", job = null) {
  const found = Array.isArray(result?.leads) ? result.leads : [];
  const existing = new Set(
    [...reviewLeads, ...customers].map((lead) => `${lead.company}|${lead.source}`.toLowerCase())
  );
  const fresh = found
    .map((lead) => normalizeLead({
      ...lead,
      sourceMode,
      discoverySource: sourceMode,
      discoveryJobId: job?.id || "",
      discoveryJobLabel: discoveryJobLabel(job),
      discoveryJobImportedAt: new Date().toISOString()
    }))
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
    const response = await apiFetch(`/api/discover/status?${new URLSearchParams({ id: jobId })}`, {
      cache: "no-store"
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    const merged = mergeDiscoveryResult(result.job?.result || {}, result.job?.payload?.sourceMode || "", result.job);
    await markDiscoveryImported(jobId);
    setFinderProgress({
      percent: 100,
      stage: "done",
      state: "complete",
      title: `已导入 ${merged.fresh.length} 条新线索`,
      message: merged.fresh.length
        ? "任务结果已进入线索审核，并已同步到云端数据。"
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
  const startResponse = await apiFetch("/api/discover/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      goal: data.goal,
      country: data.country,
      model: data.model,
      sourceMode: data.sourceMode,
      accountScope: data.accountScope,
      freshness: data.freshness,
      resultLimit: 90,
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
      statusResponse = await apiFetch(`/api/discover/status?${new URLSearchParams({
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
      return { ...(job.result || { ok: true, leads: [], count: 0 }), __jobId: job.id, __job: job };
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

async function loadDiscoverySourceStatus() {
  const target = $("#sourceAvailability");
  if (!target) return;
  try {
    const response = await apiFetch("/api/discovery-sources", { cache: "no-store" });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    const google = result.sources?.googleMaps;
    target.classList.toggle("warning", !google?.available);
    target.classList.toggle("ready", Boolean(google?.available));
    target.textContent = google?.available
      ? "数据源：Google Maps Places、Bing、DuckDuckGo、Brave、OpenStreetMap、官网/目录与公开社媒均可用。"
      : "数据源：Bing、DuckDuckGo、Brave、OpenStreetMap、官网/目录与公开社媒可用；Google Maps 需配置官方 Places API Key。";
  } catch {
    target.classList.add("warning");
    target.textContent = "暂时无法读取来源状态；自动获客仍会使用可访问的公开来源。";
  }
}

function bindForms() {
  $("#finderHistoryPrev")?.addEventListener("click", () => {
    finderHistoryPage = Math.max(1, finderHistoryPage - 1);
    renderDiscoveryHistory();
  });

  $("#finderHistoryNext")?.addEventListener("click", () => {
    const historyCount = discoveryJobs.length + discoverySchedules.filter((schedule) => !schedule.lastJobId).length;
    const pageCount = Math.max(1, Math.ceil(historyCount / FINDER_HISTORY_PAGE_SIZE));
    finderHistoryPage = Math.min(pageCount, finderHistoryPage + 1);
    renderDiscoveryHistory();
  });

  $("#discoveryPrevPage")?.addEventListener("click", () => {
    discoveryJobPage = Math.max(1, discoveryJobPage - 1);
    renderDiscoveryJobs();
  });

  $("#discoveryNextPage")?.addEventListener("click", () => {
    const pageCount = Math.max(1, Math.ceil(discoveryJobs.length / DISCOVERY_JOBS_PAGE_SIZE));
    discoveryJobPage = Math.min(pageCount, discoveryJobPage + 1);
    renderDiscoveryJobs();
  });

  $("#schedulePrevPage")?.addEventListener("click", () => {
    discoverySchedulePage = Math.max(1, discoverySchedulePage - 1);
    renderDiscoverySchedules();
  });

  $("#scheduleNextPage")?.addEventListener("click", () => {
    const pageCount = Math.max(1, Math.ceil(discoverySchedules.length / DISCOVERY_SCHEDULES_PAGE_SIZE));
    discoverySchedulePage = Math.min(pageCount, discoverySchedulePage + 1);
    renderDiscoverySchedules();
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

  $("#scheduleForm")?.addEventListener("submit", saveDiscoverySchedule);

  $("#scheduleList")?.addEventListener("click", (event) => {
    const toggleButton = event.target.closest("[data-toggle-schedule]");
    if (toggleButton) {
      toggleButton.disabled = true;
      toggleDiscoverySchedule(toggleButton.dataset.toggleSchedule).catch((error) => {
        const status = $("#scheduleStatus");
        if (status) status.textContent = `操作失败：${error.message}`;
        toggleButton.disabled = false;
      });
      return;
    }
    const deleteButton = event.target.closest("[data-delete-schedule]");
    if (deleteButton) {
      deleteButton.disabled = true;
      deleteDiscoverySchedule(deleteButton.dataset.deleteSchedule).catch((error) => {
        const status = $("#scheduleStatus");
        if (status) status.textContent = `删除失败：${error.message}`;
        deleteButton.disabled = false;
      });
    }
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
    discoveryJobPage = 1;
    finderHistoryPage = 1;
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
        const { found, fresh } = mergeDiscoveryResult(
          result,
          data.sourceMode,
          result.__job || {
            id: result.__jobId,
            country: data.country,
            model: data.model,
            sourceMode: data.sourceMode,
            createdAt: new Date().toISOString()
          }
        );
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
  $("#socialLeadForm").pageUrl.addEventListener("change", autoFillSocialFormFromUrl);
  $("#socialLeadForm").pageUrl.addEventListener("blur", autoFillSocialFormFromUrl);

  $("#socialLeadForm").addEventListener("submit", (event) => {
    event.preventDefault();
    autoFillSocialFormFromUrl();
    const data = Object.fromEntries(new FormData(event.currentTarget).entries());
    const url = safeHttpUrl(data.pageUrl);
    const domain = url ? new URL(url).hostname.toLowerCase() : "";
    const expectedDomains = {
      Facebook: ["facebook.com"],
      Instagram: ["instagram.com"],
      TikTok: ["tiktok.com"],
      YouTube: ["youtube.com", "youtu.be"],
      LinkedIn: ["linkedin.com"],
      Telegram: ["t.me", "telegram.me", "telegram.dog"],
      "X / Twitter": ["x.com", "twitter.com"],
      Threads: ["threads.net"],
      Pinterest: ["pinterest."],
      Reddit: ["reddit.com"],
      VK: ["vk.com"]
    };
    const expectedDomain = expectedDomains[data.platform] || [];
    const status = $("#socialLeadStatus");
    if (!url || !expectedDomain.some((item) => domain.includes(item))) {
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
      platform: data.platform,
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
    $("#followUpSequence").innerHTML = result.followUps.map((item) =>
      `<p><strong>${escapeHtml(item.day)}</strong>${escapeHtml(item.text)}</p>`
    ).join("");
    openOutlookDraft(data);
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
    $("#followUpSequence").innerHTML = result.followUps.map((item) =>
      `<p><strong>${escapeHtml(item.day)}</strong>${escapeHtml(item.text)}</p>`
    ).join("");
    openOutlookDraft(Object.fromEntries(new FormData(form).entries()));
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
      stage: score >= 80 ? "准备联系" : "待审核",
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
    const row = event.target.closest("[data-review-lead-row]");
    if (row && !event.target.closest("input, button, a, summary, details")) {
      selectedReviewLeadId = row.dataset.reviewLeadRow;
      editingReviewLeadId = "";
      closeOpenReviewDetails();
      renderReview();
      return;
    }
    const sectionButton = event.target.closest("[data-section]");
    if (sectionButton) {
      showSection(sectionButton.dataset.section);
      return;
    }
    const closeDetailsButton = event.target.closest("[data-close-review-details]");
    if (closeDetailsButton) {
      closeDetailsButton.closest("details")?.removeAttribute("open");
      return;
    }
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
    const editButton = event.target.closest("[data-review-edit]");
    if (editButton) {
      editingReviewLeadId = editButton.dataset.reviewEditId || "";
      renderReview();
      return;
    }
    const cancelEditButton = event.target.closest("[data-review-edit-cancel]");
    if (cancelEditButton) {
      editingReviewLeadId = "";
      renderReview();
      return;
    }
    const button = event.target.closest("[data-review-action]");
    if (!button) return;
    const index = Number(button.dataset.index);
    editingReviewLeadId = "";
    if (button.dataset.reviewAction === "approve") approveLead(index);
    if (button.dataset.reviewAction === "reject") rejectLead(index);
    if (button.dataset.reviewAction === "delete") deleteReviewLeads([reviewLeads[index]?.id]);
  });

  $("#reviewGrid").addEventListener("submit", (event) => {
    const form = event.target.closest("[data-review-edit-form]");
    if (!form) return;
    event.preventDefault();
    saveReviewLeadEdit(Number(form.dataset.index), form);
  });

  $("#reviewGrid").addEventListener("change", (event) => {
    const checkbox = event.target.closest("[data-review-select]");
    if (!checkbox) return;
    if (checkbox.checked) reviewSelectedIds.add(checkbox.dataset.reviewSelect);
    else reviewSelectedIds.delete(checkbox.dataset.reviewSelect);
    renderReview();
  });

  $("#reviewGrid").addEventListener("toggle", (event) => {
    const details = event.target;
    if (!details?.matches?.("details.review-more")) return;
    if (!details.open) {
      clearReviewDetail(details);
      return;
    }
    closeOpenReviewDetails(details);
    hydrateReviewDetail(details);
  }, true);

  ["#reviewStatusFilter", "#reviewDiscoveryFilter", "#reviewTimeFilter", "#reviewSourceFilter", "#reviewCountryFilter", "#reviewTierFilter"].forEach((selector) => {
    $(selector)?.addEventListener("change", renderReview);
  });

  $("#clearReviewFilters")?.addEventListener("click", () => {
    $("#reviewStatusFilter").value = "pending";
    $("#reviewDiscoveryFilter").value = "all";
    $("#reviewTimeFilter").value = "all";
    $("#reviewSourceFilter").value = "all";
    $("#reviewCountryFilter").value = "all";
    $("#reviewTierFilter").value = "all";
    renderReview();
  });

  $("#finderHistoryGrid")?.addEventListener("click", (event) => {
    const card = event.target.closest("[data-discovery-history-job]");
    if (!card) return;
    openDiscoveryHistoryJob(card.dataset.discoveryHistoryJob);
  });

  $("#finderHistoryGrid")?.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    const card = event.target.closest("[data-discovery-history-job]");
    if (!card) return;
    event.preventDefault();
    openDiscoveryHistoryJob(card.dataset.discoveryHistoryJob);
  });

  $("#leadList")?.addEventListener("click", (event) => {
    const card = event.target.closest("[data-candidate-lead]");
    if (!card) return;
    showCandidateInReview(card.dataset.candidateLead);
  });

  $("#leadList")?.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    const card = event.target.closest("[data-candidate-lead]");
    if (!card) return;
    event.preventDefault();
    showCandidateInReview(card.dataset.candidateLead);
  });

  $("#selectVisibleReviewLeads")?.addEventListener("click", () => {
    if (reviewStatusMode() !== "pending") return;
    const visible = reviewLeads.filter(reviewLeadMatchesFilters).map((lead) => lead.id);
    const allVisibleSelected = visible.length && visible.every((id) => reviewSelectedIds.has(id));
    visible.forEach((id) => allVisibleSelected ? reviewSelectedIds.delete(id) : reviewSelectedIds.add(id));
    renderReview();
  });

  $("#deleteSelectedReviewLeads")?.addEventListener("click", () => {
    if (reviewStatusMode() !== "pending") return;
    deleteReviewLeads([...reviewSelectedIds]);
  });

  $("#userForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const status = $("#userFormStatus");
    const data = Object.fromEntries(new FormData(form).entries());
    status.className = "form-status";
    if (data.password !== data.confirmPassword) {
      status.textContent = "两次输入的密码不一致。";
      status.classList.add("error");
      return;
    }
    const submit = form.querySelector("button[type='submit']");
    submit.disabled = true;
    try {
      const response = await apiFetch("/api/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: data.username, password: data.password })
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
      form.reset();
      status.textContent = `已添加用户：${result.user.username}`;
      status.classList.add("success");
      await loadUsers();
    } catch (error) {
      status.textContent = error.message || "添加用户失败，请稍后重试。";
      status.classList.add("error");
    } finally {
      submit.disabled = false;
    }
  });

  $("#refreshUsers")?.addEventListener("click", () => loadUsers().catch((error) => {
    $("#userRows").innerHTML = `<tr><td colspan="6">${escapeHtml(error.message)}</td></tr>`;
  }));

  $("#refreshKpiDashboard")?.addEventListener("click", () => {
    adminKpiSnapshot = null;
    renderKpis();
    refreshAdminKpis({ forceSync: true });
  });

  $("#userRows")?.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-user-action]");
    if (!button) return;
    const username = button.dataset.username;
    try {
      if (button.dataset.userAction === "password") {
        const password = window.prompt(`请输入 ${username} 的新密码（至少 6 位）：`);
        if (password === null) return;
        await updateUser(username, { password });
      }
      if (button.dataset.userAction === "status") {
        const nextStatus = button.dataset.status === "enabled" ? "disabled" : "enabled";
        if (!confirm(`确认${nextStatus === "disabled" ? "禁用" : "启用"}用户 ${username} 吗？`)) return;
        await updateUser(username, { status: nextStatus });
      }
      if (button.dataset.userAction === "delete") {
        if (!confirm(`确认永久删除用户 ${username} 吗？该用户的线索、客户、报价和获客任务也会一并删除。`)) return;
        await updateUser(username, { action: "delete" });
      }
    } catch (error) {
      window.alert(error.message || "操作失败，请稍后重试。");
    }
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

  $("#openOutlookDraft")?.addEventListener("click", () => openOutlookDraft());

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
      customer.nextFollowAt = new Date(Date.now() + 2 * 86400000).toISOString().slice(0, 10);
      customer.followUpHistory = [{
        at: new Date().toISOString().slice(0, 10),
        outcome: "已生成报价",
        note: `${lastQuote.id} · ${money(lastQuote.total)} · ${lastQuote.destination}`,
        nextFollowAt: customer.nextFollowAt
      }, ...(customer.followUpHistory || [])].slice(0, 100);
    }
    saveState();
    renderQuoteHistory();
    renderAfterSales();
    renderCrm();
    renderFollowTasks();
    renderKpis();
  });
  $("#downloadQuote").addEventListener("click", () => {
    if ($("#quoteCustomer").value === "") {
      const button = $("#downloadQuote");
      button.textContent = "请先选择客户";
      setTimeout(() => { button.textContent = "导出英文报价单"; }, 1400);
      return;
    }
    renderQuote(Object.fromEntries(new FormData($("#quoteForm")).entries()));
    downloadQuoteDocument(lastQuote);
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
    if (button.dataset.crmAction === "review") openCustomerInReview(index);
    if (button.dataset.crmAction === "email") openCustomerInEmail(index);
    if (button.dataset.crmAction === "quote") openCustomerInQuote(index);
    if (button.dataset.crmAction === "return-review") returnCustomerToReview(index);
    if (button.dataset.crmAction === "delete") {
      const lead = customers[index];
      if (!lead || !confirm(`确认删除客户 ${lead.company} 吗？此删除会同步到其他设备。`)) return;
      rememberDeletedRecord(lead, "customers");
      customers.splice(index, 1);
      refreshAllLeadViews();
    }
  });

  $("#crmViewTabs")?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-crm-filter]");
    if (!button) return;
    crmViewFilter = button.dataset.crmFilter || "all";
    renderCrm();
  });

  $("#followTasks").addEventListener("click", (event) => {
    const button = event.target.closest("[data-follow-action]");
    if (!button) return;
    const index = Number(button.dataset.index);
    if (button.dataset.followAction === "email") openCustomerInEmail(index);
    if (button.dataset.followAction === "quote") openCustomerInQuote(index);
    if (button.dataset.followAction === "contacted") updateCustomerStage(index, "已联系");
    if (button.dataset.followAction === "record") recordFollowUp(index);
  });
  $("#followFilter")?.addEventListener("change", renderFollowTasks);

  $("#riskCountry").addEventListener("change", (event) => renderRiskProfile(event.target.value));
  $("#afterSalesForm")?.addEventListener("submit", saveAfterSalesOrder);
  $("#afterSalesSource")?.addEventListener("change", (event) => fillAfterSalesFromSource(event.target.value));
  $("#afterSalesBoard")?.addEventListener("change", (event) => {
    if (event.target.matches("[data-after-status]")) {
      updateAfterSalesStatus(Number(event.target.dataset.afterStatus), event.target.value);
    }
  });
  $("#afterSalesBoard")?.addEventListener("click", (event) => {
    const logButton = event.target.closest("[data-after-log]");
    if (logButton) {
      appendAfterSalesLog(Number(logButton.dataset.afterLog));
      return;
    }
    const deleteButton = event.target.closest("[data-after-delete]");
    if (deleteButton) deleteAfterSalesOrder(Number(deleteButton.dataset.afterDelete));
  });

  $("#quoteHistory").addEventListener("click", (event) => {
    const downloadButton = event.target.closest("[data-quote-download]");
    if (downloadButton) {
      downloadQuoteDocument(quoteHistory[Number(downloadButton.dataset.quoteDownload)]);
      return;
    }
    const button = event.target.closest("[data-quote-delete]");
    if (!button) return;
    const index = Number(button.dataset.quoteDelete);
    const quote = quoteHistory[index];
    if (!quote) return;
    if (!confirm(`确认删除 ${quote.customer || "未选择客户"} 的 ${quote.model || ""} 报价版本吗？`)) return;
    rememberDeletedRecord(quote, "quotes");
    quoteHistory.splice(index, 1);
    saveState();
    renderQuoteHistory();
    renderAfterSales();
    renderKpis();
  });

  $("#exportCustomerTable").addEventListener("click", exportCustomersCsv);

  $("#exportData").addEventListener("click", () => {
    const text = JSON.stringify({ reviewLeads, customers, rejectedLeads, quotes: quoteHistory, afterSalesOrders, deletedRecords }, null, 2);
    downloadFile(
      text,
      `huawei-ev-leads-${new Date().toISOString().slice(0, 10)}.json`,
      "application/json;charset=utf-8"
    );
  });

  $("#clearSavedData").addEventListener("click", () => {
    if (!confirm("确认清空当前账号下的待审核线索、客户池、拒绝记录、报价和售后订单吗？")) return;
    reviewLeads.forEach((record) => rememberDeletedRecord(record, "reviewLeads"));
    customers.forEach((record) => rememberDeletedRecord(record, "customers"));
    rejectedLeads.forEach((record) => rememberDeletedRecord(record, "rejectedLeads"));
    quoteHistory.forEach((record) => rememberDeletedRecord(record, "quotes"));
    afterSalesOrders.forEach((record) => rememberDeletedRecord(record, "afterSalesOrders"));
    reviewLeads = [];
    customers = [];
    rejectedLeads = [];
    quoteHistory = [];
    afterSalesOrders = [];
    refreshAllLeadViews();
  });

}

function renderDefaultLetter() {
  $("#leadInsight").textContent = "客户池有客户后，可以从下拉框选择客户并自动生成开发信。";
  $("#englishLetter").textContent = "";
  $("#chineseMeaning").textContent = "暂无客户。请先一键获客、审核通过，再生成开发信。";
  if ($("#followUpSequence")) $("#followUpSequence").innerHTML = "";
}

async function loadSession() {
  const response = await fetch("/api/session", { cache: "no-store" });
  const session = await response.json().catch(() => ({}));
  if (!response.ok || !session.authenticated) throw new AuthenticationExpiredError();
  currentSession = session;
  if (savedState.ownerUsername !== session.username) {
    reviewLeads = [];
    customers = [];
    rejectedLeads = [];
    quoteHistory = [];
    afterSalesOrders = [];
    deletedRecords = [];
    cloudStateVersion = 0;
    localStateDirty = false;
    persistLocalState(false);
  }
  const userManagementNav = $("#userManagementNav");
  if (userManagementNav) userManagementNav.hidden = session.role !== "admin";
  const userManagementSection = $("#user-management");
  if (userManagementSection) userManagementSection.hidden = session.role !== "admin";
  return session;
}

function renderUsers(users = []) {
  const rows = $("#userRows");
  if (!rows) return;
  $("#userCount").textContent = `${users.length} 位用户`;
  rows.innerHTML = users.length ? users.map((user, index) => `
    <tr>
      <td>${index + 1}</td>
      <td><strong>${escapeHtml(user.username)}</strong>${user.builtIn ? `<br><small>系统内置</small>` : ""}</td>
      <td>${user.role === "admin" ? "管理员" : "普通用户"}</td>
      <td>${escapeHtml(formatSyncTime(user.createdAt))}</td>
      <td><span class="user-status ${user.status === "disabled" ? "disabled" : ""}">${user.status === "disabled" ? "已禁用" : "启用中"}</span></td>
      <td><div class="user-actions">${user.builtIn ? `<span class="meta">受保护</span>` : `
        <button type="button" data-user-action="password" data-username="${escapeHtml(user.username)}">改密码</button>
        <button type="button" data-user-action="status" data-status="${user.status}" data-username="${escapeHtml(user.username)}">${user.status === "disabled" ? "启用" : "禁用"}</button>
        <button class="danger" type="button" data-user-action="delete" data-username="${escapeHtml(user.username)}">删除</button>`}</div></td>
    </tr>`).join("") : `<tr><td colspan="6">暂无普通用户。管理员可通过左侧表单添加。</td></tr>`;
}

async function loadUsers() {
  if (currentSession?.role !== "admin") return;
  const rows = $("#userRows");
  if (rows) rows.innerHTML = `<tr><td colspan="6">正在读取用户列表…</td></tr>`;
  const response = await apiFetch("/api/users", { cache: "no-store" });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  renderUsers(Array.isArray(result.users) ? result.users : []);
}

async function updateUser(username, payload) {
  const response = await apiFetch(`/api/users/${encodeURIComponent(username)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  await loadUsers();
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
  window.__workbenchInitErrors = [];
  bindNavigation();
  showRequestedSection();
  window.addEventListener("hashchange", showRequestedSection);
  try {
    await loadSession();
  } catch (error) {
    console.error("Session load failed:", error);
    redirectToLogin();
    return;
  }
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
    ["售后", renderAfterSales],
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
  hydrateCloudState(true).catch((error) => {
    setCloudSyncStatus("云端不可用，当前使用本地副本", "error");
    console.error("Cloud workspace load failed:", error);
  });
  loadUsers().catch((error) => {
    if ($("#userRows")) $("#userRows").innerHTML = `<tr><td colspan="6">${escapeHtml(error.message)}</td></tr>`;
  });
  setInterval(renderBeijingGreeting, 1_000);
  loadDiscoveryJobs().catch((error) => {
    if ($("#discoveryJobList")) {
      $("#discoveryJobList").innerHTML = `<p class="empty">任务读取失败：${escapeHtml(error.message)}</p>`;
    }
  });
  loadDiscoverySchedules().catch((error) => {
    if ($("#scheduleList")) {
      $("#scheduleList").innerHTML = `<p class="empty">定时计划读取失败：${escapeHtml(error.message)}</p>`;
    }
  });
  discoveryJobsTimer = window.setInterval(() => {
    loadDiscoveryJobs().catch(() => undefined);
    loadDiscoverySchedules().catch(() => undefined);
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
  loadDiscoverySourceStatus();
  importSocialCaptures();
  setInterval(importSocialCaptures, 4_000);
  showRequestedSection();
  window.addEventListener("hashchange", showRequestedSection);
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
