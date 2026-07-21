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
  },
  {
    name: "Nigeria 尼日利亚",
    rank: "第三优先级",
    cities: "Lagos / Abuja / Port Harcourt",
    reason: "人口和商业规模大，适合从进口商、车商集团和企业车队切入。",
    targets: "汽车进口商、经销商集团、企业车队"
  },
  {
    name: "Ghana 加纳",
    rank: "第三优先级",
    cities: "Accra / Kumasi / Tema",
    reason: "西非英语市场，港口和贸易体系相对活跃，适合开发进口商和多品牌车商。",
    targets: "汽车进口商、多品牌展厅、车队采购"
  },
  {
    name: "Algeria 阿尔及利亚",
    rank: "第三优先级",
    cities: "Algiers / Oran / Constantine",
    reason: "北非大型汽车市场，需重点确认进口政策、认证和本地代理资质。",
    targets: "汽车进口商、区域代理、经销商集团"
  },
  {
    name: "Côte d'Ivoire 科特迪瓦",
    rank: "第三优先级",
    cities: "Abidjan / Yamoussoukro",
    reason: "西非法语商业中心之一，适合寻找进口商、贸易公司和企业车队。",
    targets: "汽车进口商、贸易公司、企业车队"
  },
  {
    name: "Egypt 埃及",
    rank: "第三优先级",
    cities: "Cairo / Alexandria / Giza",
    reason: "北非人口和汽车消费规模大，适合从经销集团、进口商和商务车队筛选。",
    targets: "经销商集团、汽车进口商、商务车队"
  },
  {
    name: "Kyrgyzstan 吉尔吉斯",
    rank: "第三优先级",
    cities: "Bishkek / Osh",
    reason: "中亚转口和二手/进口车交易活跃，适合找平行进口商和区域贸易商。",
    targets: "平行进口商、汽车贸易公司、区域代理"
  },
  {
    name: "Ethiopia 埃塞俄比亚",
    rank: "第三优先级",
    cities: "Addis Ababa / Dire Dawa",
    reason: "东非人口规模大，适合先筛选政府/企业车队和实力进口商。",
    targets: "汽车进口商、政府/企业采购、车队运营商"
  },
  {
    name: "Oman 阿曼",
    rank: "第三优先级",
    cities: "Muscat / Salalah / Sohar",
    reason: "海湾市场，适合寻找豪华车商、多品牌展厅和商务接待车队。",
    targets: "豪车展厅、多品牌经销商、商务接待车队"
  },
  {
    name: "Armenia 亚美尼亚",
    rank: "第三优先级",
    cities: "Yerevan / Gyumri",
    reason: "高加索小型进口车市场，可作为区域代理和平行进口补充市场。",
    targets: "汽车贸易公司、平行进口商、区域代理"
  },
  {
    name: "Bahrain 巴林",
    rank: "其他可开发",
    marketGroup: "other",
    cities: "Manama / Riffa / Muharraq",
    reason: "海湾小型高购买力市场，可与阿联酋、沙特客户网络联动开发。",
    targets: "豪华车展厅、多品牌进口商、商务车队"
  },
  {
    name: "Jordan 约旦",
    rank: "其他可开发",
    marketGroup: "other",
    cities: "Amman / Zarqa / Irbid",
    reason: "左舵进口车市场，可寻找覆盖本国及周边市场的经销商和贸易商。",
    targets: "汽车进口商、多品牌经销商、区域贸易商"
  },
  {
    name: "Georgia 格鲁吉亚",
    rank: "其他可开发",
    marketGroup: "other",
    cities: "Tbilisi / Batumi / Rustavi",
    reason: "高加索汽车贸易和转口活跃，适合开发平行进口及区域分销客户。",
    targets: "平行进口商、汽车贸易公司、区域批发商"
  },
  {
    name: "Vietnam 越南",
    rank: "其他可开发",
    marketGroup: "other",
    cities: "Ho Chi Minh City / Hanoi / Da Nang",
    reason: "东南亚新能源车增长快且采用左舵，但需面对本土品牌和价格竞争。",
    targets: "新能源车经销商、高端展厅、企业车队"
  },
  {
    name: "Philippines 菲律宾",
    rank: "其他可开发",
    marketGroup: "other",
    cities: "Metro Manila / Cebu / Davao",
    reason: "左舵英语市场，新能源政策逐步推进，适合先开发进口商和车商集团。",
    targets: "汽车进口商、经销商集团、企业车队"
  },
  {
    name: "Mexico 墨西哥",
    rank: "其他可开发",
    marketGroup: "other",
    cities: "Mexico City / Monterrey / Guadalajara",
    reason: "拉美大型汽车市场，中国新能源车增长快，适合寻找全国及区域经销网络。",
    targets: "汽车进口商、经销商集团、新能源车展厅"
  },
  {
    name: "Brazil 巴西",
    rank: "其他可开发",
    marketGroup: "other",
    cities: "São Paulo / Rio de Janeiro / Brasília",
    reason: "拉美最大汽车市场之一，插混和中国品牌接受度提升，但需提前核算税费与认证。",
    targets: "大型经销集团、汽车进口商、企业车队"
  },
  {
    name: "Chile 智利",
    rank: "其他可开发",
    marketGroup: "other",
    cities: "Santiago / Valparaíso / Concepción",
    reason: "进口车型市场开放度较高，可从多品牌经销商和新能源车渠道切入。",
    targets: "汽车进口商、多品牌经销商、车队采购"
  },
  {
    name: "Colombia 哥伦比亚",
    rank: "其他可开发",
    marketGroup: "other",
    cities: "Bogotá / Medellín / Cali",
    reason: "新能源政策和城市电动化持续推进，适合开发进口商、经销集团和商务车队。",
    targets: "汽车进口商、经销商集团、商务车队"
  },
  {
    name: "Morocco 摩洛哥",
    rank: "其他可开发",
    marketGroup: "other",
    cities: "Casablanca / Rabat / Tangier",
    reason: "北非汽车产业和港口条件较好，可作为北非及法语市场的补充入口。",
    targets: "汽车进口商、经销商集团、区域贸易公司"
  }
];

const domesticRegions = [
  {
    value: "",
    label: "不搜索国内",
    cities: "",
    targets: "汽车经销商、进口贸易商、企业车队"
  },
  {
    value: "全国",
    label: "全国",
    cities: "北京 / 上海 / 广州 / 深圳 / 成都 / 杭州 / 武汉",
    targets: "多品牌车商、汽车贸易公司、企业车队、二网经销商"
  },
  {
    value: "华北",
    label: "华北",
    cities: "北京 / 天津 / 石家庄 / 太原 / 呼和浩特",
    targets: "汽车集团、平行进口商、政企车队、二网经销商"
  },
  {
    value: "华东",
    label: "华东",
    cities: "上海 / 杭州 / 南京 / 苏州 / 宁波 / 合肥 / 济南 / 福州",
    targets: "汽车贸易公司、高端展厅、外贸公司、企业采购"
  },
  {
    value: "华南",
    label: "华南",
    cities: "广州 / 深圳 / 佛山 / 东莞 / 南宁 / 海口",
    targets: "外贸车商、出口公司、豪华车展厅、港口贸易商"
  },
  {
    value: "华中",
    label: "华中",
    cities: "武汉 / 长沙 / 郑州",
    targets: "汽车经销集团、新能源车商、企业车队"
  },
  {
    value: "西南",
    label: "西南",
    cities: "成都 / 重庆 / 昆明 / 贵阳 / 拉萨",
    targets: "区域经销商、车队采购、汽车贸易公司"
  },
  {
    value: "西北",
    label: "西北",
    cities: "西安 / 兰州 / 银川 / 西宁 / 乌鲁木齐",
    targets: "区域代理、商用采购、边贸汽车公司"
  },
  {
    value: "东北",
    label: "东北",
    cities: "沈阳 / 大连 / 长春 / 哈尔滨",
    targets: "经销集团、二网车商、进口车贸易公司"
  }
];

const DEFAULT_FINDER_MODEL = "华为系新能源汽车";

const salesStages = ["准备联系", "已联系", "有回复", "报价中", "谈判中", "已成交", "暂缓", "已流失"];

const destinationByCountry = {
  UAE: "Jebel Ali, UAE",
  "Saudi Arabia": "Dammam, Saudi Arabia",
  Kazakhstan: "Aktau, Kazakhstan",
  Russia: "Vladivostok, Russia",
  Qatar: "Doha, Qatar",
  Kuwait: "Kuwait City, Kuwait",
  Uzbekistan: "Poti, Georgia (transit to Uzbekistan)",
  Azerbaijan: "Alat Port, Azerbaijan",
  Nigeria: "Lagos, Nigeria",
  Ghana: "Tema, Ghana",
  Algeria: "Algiers, Algeria",
  "Côte d'Ivoire": "Abidjan, Côte d'Ivoire",
  Egypt: "Alexandria, Egypt",
  Kyrgyzstan: "Bishkek, Kyrgyzstan",
  Ethiopia: "Addis Ababa, Ethiopia",
  Oman: "Sohar, Oman",
  Armenia: "Yerevan, Armenia"
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

[
  "Nigeria", "Ghana", "Algeria", "Côte d'Ivoire", "Egypt",
  "Kyrgyzstan", "Ethiopia", "Oman", "Armenia"
].forEach((key) => {
  riskProfiles[key] = {
    certification: "成交前让当地进口商或清关代理书面确认车型准入、认证、年份、排放、关税和上牌资料。",
    cockpit: "交车前核对英文/当地语言界面、网络、地图、远程 App 和高温/低温环境适配，不承诺未验证功能。",
    logistics: "按实际港口或内陆交付城市确认海运、清关、内陆运输、保险和本地费用，报价中单列目的港外费用。",
    service: "先确认当地维修合作方、诊断能力、常用备件和质保责任边界，再承诺交付后的服务周期。"
  };
});

const STORAGE_KEY = "huawei-ev-export-workbench-v3";
const LOCAL_STATE_CACHE_VERSION = 2;
const SOCIAL_CAPTURE_SEEN_KEY = "huawei-ev-social-capture-seen-v1";
const UI_SETTINGS_KEY = "huawei-ev-workbench-ui-settings-v1";
const DEFAULT_UI_SETTINGS = {
  brightness: 100,
  theme: "light"
};

const IRRELEVANT_REVIEW_LEAD_DOMAINS = [
  "cgtn.com",
  "cgtnamerica.com",
  "cnn.com",
  "bbc.com",
  "bbc.co.uk",
  "reuters.com",
  "apnews.com",
  "aljazeera.com",
  "bloomberg.com",
  "kfc.co.th",
  "kfc.com",
  "mcdonalds.com",
  "burgerking.com",
  "pizzahut.com",
  "dominos.com",
  "starbucks.com"
];

const NON_CUSTOMER_WEBSITE_DOMAINS = [
  "ytcfg.set",
  "ggpht.com",
  "ytimg.com",
  "iytimg.com",
  "googleusercontent.com",
  "gstatic.com",
  "googlevideo.com",
  "kfc.co.th",
  "kfc.com",
  "mcdonalds.com",
  "burgerking.com",
  "pizzahut.com",
  "dominos.com",
  "starbucks.com"
];

const NON_CUSTOMER_WEBSITE_PATTERNS = [
  "ytcfg.set",
  "ytinitialdata",
  "ytinitialplayerresponse",
  "window.ytplayer",
  "ytplayer",
  "kfc.",
  "mcdonalds.",
  "burgerking.",
  "pizzahut.",
  "dominos.",
  "starbucks."
];

const DIRECTORY_OPERATOR_WEBSITE_DOMAINS = [
  "dubicars.com",
  "saudisale.com",
  "qmotor.com"
];

const MAX_LEADS_PER_CUSTOMER_WEBSITE = 5;

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
    NON_CUSTOMER_WEBSITE_PATTERNS.some((pattern) => raw.includes(pattern) || hostname.includes(pattern))
    || NON_CUSTOMER_WEBSITE_DOMAINS.some((domain) => hostname === domain || hostname.endsWith(`.${domain}`))
  );
}

function sanitizeCustomerWebsite(value) {
  const hostname = leadHostname(value);
  const isDirectoryOperator = DIRECTORY_OPERATOR_WEBSITE_DOMAINS.some((domain) => (
    hostname === domain || hostname.endsWith(`.${domain}`)
  ));
  return isNonCustomerWebsiteUrl(value) || isDirectoryOperator ? "" : String(value || "").trim();
}

function customerWebsiteKey(value) {
  const sanitized = sanitizeCustomerWebsite(value);
  const hostname = leadHostname(sanitized);
  return hostname || "";
}

function canonicalLeadUrl(value) {
  try {
    const raw = String(value || "").trim();
    if (!raw || !/^(?:https?:\/\/|www\.)/i.test(raw)) return "";
    const url = new URL(/^https?:\/\//i.test(raw) ? raw : `https://${raw}`);
    const hostname = url.hostname.replace(/^www\./, "").toLowerCase();
    const pathname = url.pathname.replace(/\/+$/, "") || "/";
    return `${hostname}${pathname}`.toLowerCase();
  } catch {
    return "";
  }
}

function normalizedLeadIdentityText(value) {
  return String(value || "")
    .normalize("NFKC")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim();
}

function leadRejectionFingerprints(lead) {
  const fingerprints = new Set();
  const company = normalizedLeadIdentityText(lead?.company);
  const country = normalizedLeadIdentityText(lead?.country);
  if (company && country) fingerprints.add(`company:${country}:${company}`);

  const website = customerWebsiteKey(lead?.customerWebsite);
  if (website) fingerprints.add(`website:${website}`);

  const evidenceSources = Array.isArray(lead?.evidenceSources) ? lead.evidenceSources : [];
  const socialProfiles = Array.isArray(lead?.socialProfiles) ? lead.socialProfiles : [];
  [
    lead?.sourceUrl,
    ...evidenceSources.map((item) => item?.url),
    ...socialProfiles.map((item) => item?.url)
  ].forEach((value) => {
    const key = canonicalLeadUrl(value);
    if (key) fingerprints.add(`url:${key}`);
  });

  const email = String(lead?.email || "").trim().toLowerCase();
  if (email) fingerprints.add(`email:${email}`);
  [lead?.phone, lead?.whatsapp].forEach((value) => {
    const digits = String(value || "").replace(/\D/g, "");
    if (digits.length >= 7) fingerprints.add(`phone:${digits}`);
  });
  return fingerprints;
}

function matchesRejectedLeadMemory(lead, rejectedFingerprintSet) {
  for (const fingerprint of leadRejectionFingerprints(lead)) {
    if (rejectedFingerprintSet.has(fingerprint)) return true;
  }
  return false;
}

function limitDuplicateCustomerWebsites(leads, existingRecords = []) {
  const counts = new Map();
  (Array.isArray(existingRecords) ? existingRecords : []).forEach((record) => {
    const key = customerWebsiteKey(record?.customerWebsite);
    if (key) counts.set(key, (counts.get(key) || 0) + 1);
  });
  return (Array.isArray(leads) ? leads : []).filter((lead) => {
    const key = customerWebsiteKey(lead?.customerWebsite);
    if (!key) return true;
    const nextCount = (counts.get(key) || 0) + 1;
    if (nextCount > MAX_LEADS_PER_CUSTOMER_WEBSITE) return false;
    counts.set(key, nextCount);
    return true;
  });
}

function isBlockedLeadDomain(value) {
  const hostname = leadHostname(value);
  if (!hostname) return false;
  return (
    isNonCustomerWebsiteUrl(value)
    || IRRELEVANT_REVIEW_LEAD_DOMAINS.some((domain) => (
      hostname === domain || hostname.endsWith(`.${domain}`)
    ))
  );
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
let websiteLeads = savedState.websiteLeads || [];
let rejectedLeads = savedState.rejectedLeads;
let quoteHistory = savedState.quotes;
let afterSalesOrders = savedState.afterSalesOrders;
let deletedRecords = savedState.deletedRecords;
let lastQuote = null;
let manualParsedLead = null;
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
const autoImportingDiscoveryJobs = new Set();
const hiddenDiscoveryJobIds = new Set(JSON.parse(localStorage.getItem(`${STORAGE_KEY}:hidden-discovery-jobs`) || "[]"));
let discoverySchedules = [];
let discoverySchedulePage = 1;
const DISCOVERY_SCHEDULE_GROUPS_PAGE_SIZE = 1;
let scheduledDiscoveryJobs = [];
let scheduledRunPage = 1;
const SCHEDULED_RUNS_PAGE_SIZE = 12;
let scheduledRunPollTick = 0;
let adminUsers = [];
let finderHistoryPage = 1;
const FINDER_HISTORY_PAGE_SIZE = 24;
let activeDiscoveryJobFilter = "all";
let reviewSelectedIds = new Set();
let selectedReviewLeadId = "";
let editingReviewLeadId = "";
let rejectingReviewLeadId = "";
let openReviewDetailKey = "";
const reviewDetailScrollPositions = new Map();
let reviewSearchRenderTimer = 0;
let reviewDetailHydrationId = 0;
const rejectReasonOptions = [
  "不是汽车经销/进口/分销客户",
  "地区不符合目标市场",
  "重复线索",
  "联系方式无效或无法核验",
  "媒体/个人账号/内容频道",
  "维修、配件、租赁等非目标客户",
  "信息太少，暂不跟进"
];
const leadAttachmentAccept = [
  "image/*",
  ".pdf",
  ".doc",
  ".docx",
  ".xls",
  ".xlsx",
  ".csv",
  ".txt",
  ".md",
  ".rtf"
].join(",");
const maxLeadAttachmentBytes = 4 * 1024 * 1024;
const maxLeadAttachmentCount = 6;
const ASSIGNED_COUNTRY_NONE = "__none__";
const loadingButtonTimers = new WeakMap();
let currentSession = null;
let adminKpiSnapshot = null;
let adminKpiLoading = false;
let adminSettingsSnapshot = null;
let adminOperationsSnapshot = null;
let adminApiShowAll = false;
let crmViewFilter = "all";
let crmSearchQuery = "";
let crmTierFilter = "all";
let crmStageFilter = "all";
let crmSortBy = "priority";
let navigationBound = false;
let salesOverviewBound = false;
let salesMap = null;
let selectedSalesCountry = "";
let salesMapMetric = "leads";
let salesMapRange = "all";

const salesCountryCoordinates = {
  UAE: [24.45, 54.38],
  "Saudi Arabia": [24.71, 46.67],
  Kazakhstan: [48.02, 66.92],
  Russia: [55.75, 37.62],
  Qatar: [25.29, 51.53],
  Kuwait: [29.38, 47.99],
  Uzbekistan: [41.31, 69.24],
  Azerbaijan: [40.41, 49.87],
  Nigeria: [9.08, 8.68],
  Ghana: [7.95, -1.02],
  Algeria: [28.03, 1.66],
  "Côte d'Ivoire": [7.54, -5.55],
  Egypt: [26.82, 30.8],
  Kyrgyzstan: [41.2, 74.77],
  Ethiopia: [9.15, 40.49],
  Oman: [21.47, 55.98],
  Armenia: [40.07, 45.04],
  Bahrain: [26.07, 50.56],
  Jordan: [31.24, 36.51],
  Georgia: [42.32, 43.36],
  Vietnam: [14.06, 108.28],
  Philippines: [12.88, 121.77],
  Mexico: [23.63, -102.55],
  Brazil: [-14.24, -51.93],
  Chile: [-33.45, -70.67],
  Colombia: [4.57, -74.3],
  Morocco: [31.79, -7.09],
  China: [35.86, 104.2]
};

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
    const isLeadProfileSource = sources.some((source) => source.sourceKind === "lead_profile");
    return `
      <div class="email-evidence-item">
        <a class="email-address" href="mailto:${escapeHtml(record.email)}">${escapeHtml(record.email)}</a>
        <span class="verified-badge">${isLeadProfileSource ? "线索主页来源" : "已核验"}</span>
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
    ["汽车业务匹配分", (lead) => lead.scoreDimensions?.automotiveFit || 0],
    ["目标地区匹配分", (lead) => lead.scoreDimensions?.countryFit || 0],
    ["中国新能源分", (lead) => lead.scoreDimensions?.chineseNev || 0],
    ["华为系列分", (lead) => lead.scoreDimensions?.huaweiFit || 0],
    ["联系方式完整分", (lead) => lead.scoreDimensions?.contactCompleteness || 0],
    ["官网可信度分", (lead) => lead.scoreDimensions?.websiteTrust || 0],
    ["进口分销能力分", (lead) => lead.scoreDimensions?.tradeQualification || 0],
    ["经营活跃度分", (lead) => lead.scoreDimensions?.businessCapacity || 0],
    ["决策人信息分", (lead) => lead.scoreDimensions?.decisionMaker || 0],
    ["采购合作意向分", (lead) => lead.scoreDimensions?.purchaseIntent || 0],
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

const customerImportTemplateColumns = [
  "公司名称",
  "国家",
  "城市",
  "客户类型",
  "联系人",
  "职位",
  "邮箱",
  "电话",
  "WhatsApp",
  "客户官网",
  "来源",
  "主推车型",
  "销售阶段",
  "下一步动作",
  "计划跟进日期",
  "备注"
];

const customerImportHeaderAliases = {
  company: ["公司名称", "公司", "客户", "company", "company name"],
  country: ["国家", "country"],
  city: ["城市", "city"],
  type: ["客户类型", "类型", "customer type", "type"],
  contactName: ["联系人", "联系人姓名", "contact", "contact name"],
  contactRole: ["职位", "联系人职务", "role", "title"],
  email: ["邮箱", "电子邮箱", "全部已核验邮箱", "email", "e-mail"],
  phone: ["电话", "全部电话", "phone", "telephone"],
  whatsapp: ["whatsapp", "全部 whatsapp", "全部whatsapp"],
  customerWebsite: ["客户官网", "官网", "website", "customer website"],
  source: ["来源", "原始线索来源", "source"],
  model: ["主推车型", "推荐车型", "车型", "model"],
  stage: ["销售阶段", "阶段", "stage"],
  next: ["下一步动作", "下一步", "next action"],
  nextFollowAt: ["计划跟进日期", "跟进日期", "next follow date"],
  website: ["备注", "客户官网内容", "客户信息", "notes", "note"]
};

function downloadCustomerImportTemplate() {
  const example = [
    "示例-请删除此行",
    "UAE",
    "Dubai",
    "Auto importer",
    "Ahmed",
    "Purchasing Manager",
    "buyer@example.com",
    "+971500000000",
    "+971500000000",
    "https://example.com",
    "展会",
    "问界 M9",
    "准备联系",
    "发送 WhatsApp 首次开发信",
    "",
    "在此填写客户背景或采购需求"
  ];
  downloadFile(
    `\uFEFF${customerImportTemplateColumns.map(csvCell).join(",")}\r\n${example.map(csvCell).join(",")}`,
    "客户池导入模板.csv",
    "text/csv;charset=utf-8"
  );
}

function detectCsvDelimiter(text) {
  const firstLine = String(text || "").split(/\r?\n/, 1)[0] || "";
  const candidates = [",", "\t", ";"];
  let best = ",";
  let bestCount = -1;
  candidates.forEach((candidate) => {
    let count = 0;
    let quoted = false;
    for (let index = 0; index < firstLine.length; index += 1) {
      const char = firstLine[index];
      if (char === '"') {
        if (quoted && firstLine[index + 1] === '"') index += 1;
        else quoted = !quoted;
      } else if (!quoted && char === candidate) {
        count += 1;
      }
    }
    if (count > bestCount) {
      best = candidate;
      bestCount = count;
    }
  });
  return best;
}

function parseCustomerCsv(text) {
  const source = String(text || "").replace(/^\uFEFF/, "");
  const delimiter = detectCsvDelimiter(source);
  const rows = [];
  let row = [];
  let cell = "";
  let quoted = false;
  for (let index = 0; index < source.length; index += 1) {
    const char = source[index];
    if (quoted) {
      if (char === '"' && source[index + 1] === '"') {
        cell += '"';
        index += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        cell += char;
      }
    } else if (char === '"') {
      quoted = true;
    } else if (char === delimiter) {
      row.push(cell);
      cell = "";
    } else if (char === "\n") {
      row.push(cell.replace(/\r$/, ""));
      if (row.some((value) => String(value).trim())) rows.push(row);
      row = [];
      cell = "";
    } else {
      cell += char;
    }
  }
  row.push(cell.replace(/\r$/, ""));
  if (row.some((value) => String(value).trim())) rows.push(row);
  return rows;
}

function cleanImportedCell(value) {
  const text = String(value ?? "").trim();
  return /^'[=+\-@]/.test(text) ? text.slice(1) : text;
}

async function decodeCustomerImportFile(file) {
  const bytes = new Uint8Array(await file.arrayBuffer());
  if (bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf) {
    return new TextDecoder("utf-8").decode(bytes);
  }
  try {
    return new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  } catch {
    return new TextDecoder("gb18030").decode(bytes);
  }
}

function customerImportColumnMap(headerRow) {
  const normalizedHeaders = headerRow.map((value) => cleanImportedCell(value).toLowerCase());
  return Object.fromEntries(Object.entries(customerImportHeaderAliases).map(([field, aliases]) => [
    field,
    normalizedHeaders.findIndex((header) => aliases.includes(header))
  ]));
}

function customerImportValue(row, columnMap, field) {
  const index = Number(columnMap[field]);
  return index >= 0 ? cleanImportedCell(row[index]) : "";
}

function customerDuplicateKeys(lead) {
  const company = String(lead?.company || "").trim().toLowerCase().replace(/\s+/g, " ");
  const country = String(lead?.country || "").trim().toLowerCase().replace(/\s+/g, " ");
  const website = canonicalLeadUrl(lead?.customerWebsite || "");
  const email = String(lead?.email || "").trim().toLowerCase();
  return [
    company && country ? `company:${company}|${country}` : "",
    website ? `website:${website}` : "",
    email ? `email:${email}` : ""
  ].filter(Boolean);
}

function setCustomerImportStatus(message, state = "") {
  const status = $("#customerImportStatus");
  if (!status) return;
  status.textContent = message;
  status.dataset.state = state;
}

async function importCustomersCsv(file) {
  if (!file) return;
  if (!/\.csv$/i.test(file.name || "") && !/csv/i.test(file.type || "")) {
    throw new Error("请选择 CSV 文件。");
  }
  const rows = parseCustomerCsv(await decodeCustomerImportFile(file));
  if (rows.length < 2) throw new Error("模板中没有可导入的客户数据。");
  const columnMap = customerImportColumnMap(rows[0]);
  if (columnMap.company < 0 || columnMap.country < 0) {
    throw new Error("模板必须包含“公司名称”和“国家”两列。");
  }
  const duplicateKeys = new Set(customers.flatMap(customerDuplicateKeys));
  const imported = [];
  let duplicateCount = 0;
  let invalidCount = 0;
  rows.slice(1).forEach((row) => {
    const company = customerImportValue(row, columnMap, "company");
    const country = customerImportValue(row, columnMap, "country");
    if (/^示例(?:-|－)/.test(company)) return;
    if (!company || !country) {
      invalidCount += 1;
      return;
    }
    const email = customerImportValue(row, columnMap, "email").split(/\s*[;；]\s*/, 1)[0];
    if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      invalidCount += 1;
      return;
    }
    const customerWebsite = normalizeUserEnteredUrl(customerImportValue(row, columnMap, "customerWebsite"));
    const requestedStage = customerImportValue(row, columnMap, "stage");
    const stage = salesStages.includes(requestedStage) ? requestedStage : "准备联系";
    const importedAt = new Date().toISOString();
    const lead = normalizeLead({
      company,
      country,
      city: customerImportValue(row, columnMap, "city"),
      type: customerImportValue(row, columnMap, "type") || "Auto business",
      contactName: customerImportValue(row, columnMap, "contactName"),
      contactRole: customerImportValue(row, columnMap, "contactRole"),
      email,
      phone: customerImportValue(row, columnMap, "phone"),
      whatsapp: customerImportValue(row, columnMap, "whatsapp"),
      customerWebsite,
      source: customerImportValue(row, columnMap, "source") || "CSV 导入",
      sourceUrl: customerWebsite,
      sourceTitle: company,
      sourceType: "客户池批量导入",
      origin: "批量导入",
      model: customerImportValue(row, columnMap, "model") || "问界 M9",
      stage,
      next: customerImportValue(row, columnMap, "next") || defaultNextAction(stage),
      nextFollowAt: customerImportValue(row, columnMap, "nextFollowAt"),
      website: customerImportValue(row, columnMap, "website"),
      isManualLead: true,
      isManualEntryOnly: true,
      isImportedLead: true,
      skipInformationVerification: true,
      manualApproval: true,
      manualApprovalAt: importedAt,
      createdAt: importedAt,
      confidenceLabel: "批量导入",
      preferredChannel: customerImportValue(row, columnMap, "whatsapp") ? "WhatsApp" : "Email",
      sourceCoverage: {
        total: 0,
        official: 0,
        independentDomains: 0,
        contactable: Boolean(email || customerImportValue(row, columnMap, "phone") || customerImportValue(row, columnMap, "whatsapp")),
        missingFields: [],
        decision: "客户池批量导入"
      }
    });
    const keys = customerDuplicateKeys(lead);
    if (keys.some((key) => duplicateKeys.has(key))) {
      duplicateCount += 1;
      return;
    }
    keys.forEach((key) => duplicateKeys.add(key));
    imported.push(lead);
  });
  if (imported.length) {
    customers = [...imported, ...customers];
    refreshAllLeadViews();
  }
  return { imported: imported.length, duplicates: duplicateCount, invalid: invalidCount };
}

function loadUiSettings() {
  try {
    const raw = localStorage.getItem(UI_SETTINGS_KEY);
    if (!raw) return { ...DEFAULT_UI_SETTINGS };
    const parsed = JSON.parse(raw);
    return {
      brightness: Math.min(120, Math.max(70, Number(parsed.brightness) || DEFAULT_UI_SETTINGS.brightness)),
      theme: parsed.theme === "dark" ? "dark" : DEFAULT_UI_SETTINGS.theme
    };
  } catch {
    return { ...DEFAULT_UI_SETTINGS };
  }
}

function persistUiSettings(settings) {
  localStorage.setItem(UI_SETTINGS_KEY, JSON.stringify(settings));
}

function setSwitchState(button, active) {
  if (!button) return;
  button.setAttribute("aria-pressed", active ? "true" : "false");
}

function closeBrightnessPopover() {
  const popover = $("#brightnessPopover");
  const toggle = $("#brightnessToggle");
  if (!popover || !toggle) return;
  popover.hidden = true;
  toggle.setAttribute("aria-expanded", "false");
}

function toggleBrightnessPopover() {
  const popover = $("#brightnessPopover");
  const toggle = $("#brightnessToggle");
  if (!popover || !toggle) return;
  const open = popover.hidden;
  popover.hidden = !open;
  toggle.setAttribute("aria-expanded", open ? "true" : "false");
}

function applyBrightness(value) {
  const brightness = Math.min(120, Math.max(70, Number(value) || 100));
  if (brightness < 100) {
    document.documentElement.style.setProperty("--brightness-overlay-color", "0, 0, 0");
    document.documentElement.style.setProperty("--brightness-overlay-opacity", String((100 - brightness) / 100));
  } else {
    document.documentElement.style.setProperty("--brightness-overlay-color", "255, 255, 255");
    document.documentElement.style.setProperty("--brightness-overlay-opacity", String((brightness - 100) / 100));
  }
  const label = $("#brightnessValue");
  if (label) label.textContent = `${brightness}%`;
}

function applyUiSettings(settings = loadUiSettings()) {
  const root = document.documentElement;
  root.dataset.theme = settings.theme;
  applyBrightness(settings.brightness);

  const brightnessRange = $("#brightnessRange");
  if (brightnessRange) brightnessRange.value = String(settings.brightness);
  setSwitchState($("#themeToggle"), settings.theme === "dark");
  setSwitchState($("#fullscreenToggle"), Boolean(document.fullscreenElement));
  const themeLabel = $("#themeToggleText");
  if (themeLabel) themeLabel.textContent = settings.theme === "dark" ? "日" : "夜";
}

async function toggleFullscreen() {
  if (document.fullscreenElement) {
    await document.exitFullscreen();
  } else {
    await document.documentElement.requestFullscreen();
  }
}

function bindUiSettings() {
  let settings = loadUiSettings();

  $("#brightnessToggle")?.addEventListener("click", (event) => {
    event.stopPropagation();
    toggleBrightnessPopover();
  });

  $("#brightnessRange")?.addEventListener("input", (event) => {
    settings = { ...settings, brightness: Number(event.target.value) };
    applyUiSettings(settings);
    persistUiSettings(settings);
  });

  $("#themeToggle")?.addEventListener("click", () => {
    settings = { ...settings, theme: settings.theme === "dark" ? "light" : "dark" };
    applyUiSettings(settings);
    persistUiSettings(settings);
  });

  $("#fullscreenToggle")?.addEventListener("click", () => {
    toggleFullscreen().catch((error) => console.error("Fullscreen toggle failed:", error));
  });

  document.addEventListener("fullscreenchange", () => {
    setSwitchState($("#fullscreenToggle"), Boolean(document.fullscreenElement));
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest("#brightnessMenu")) closeBrightnessPopover();
  });

  document.addEventListener("change", (event) => {
    const input = event.target.closest(".user-country-checklist input[type='checkbox']");
    if (!input) return;
    syncCountryNoneCheckbox(input.closest(".user-country-checklist"), input);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeBrightnessPopover();
  });
}

function loadSavedState() {
  const fallback = {
    reviewLeads: [],
    customers: [],
    websiteLeads: [],
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
    if (Number(parsed._cacheVersion || 0) !== LOCAL_STATE_CACHE_VERSION || parsed._cloudDirty !== true) {
      localStorage.removeItem(STORAGE_KEY);
      return fallback;
    }
    return {
      reviewLeads: limitDuplicateCustomerWebsites(filterReviewLeadsForBusinessFit(parsed.reviewLeads)),
      customers: Array.isArray(parsed.customers) ? parsed.customers : [],
      websiteLeads: Array.isArray(parsed.websiteLeads) ? parsed.websiteLeads : [],
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
    websiteLeads,
    rejectedLeads,
    quotes: quoteHistory,
    afterSalesOrders,
    deletedRecords
  };
}

function persistLocalState(dirty = localStateDirty) {
  localStateDirty = dirty;
  if (!localStateDirty) {
    localStorage.removeItem(STORAGE_KEY);
    return;
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    ...workspaceStateSnapshot(),
    ownerUsername: currentSession?.username || "",
    _cloudVersion: cloudStateVersion,
    _cloudDirty: true,
    _cacheVersion: LOCAL_STATE_CACHE_VERSION
  }));
}

function normalizeUserEnteredUrl(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";
  return safeHttpUrl(/^[a-z][a-z\d+.-]*:\/\//i.test(raw) ? raw : `https://${raw}`);
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

function rememberHiddenDiscoveryJob(jobId) {
  if (!jobId) return;
  hiddenDiscoveryJobIds.add(String(jobId));
  localStorage.setItem(`${STORAGE_KEY}:hidden-discovery-jobs`, JSON.stringify([...hiddenDiscoveryJobIds].slice(-1000)));
}

function forgetDeletedRecordsForLeads(leads) {
  const keys = new Set(
    (Array.isArray(leads) ? leads : [])
      .flatMap((lead) => [
        recordIdentity(lead, "reviewLeads"),
        recordIdentity(lead, "customers"),
        recordIdentity(lead, "rejectedLeads")
      ])
      .filter(Boolean)
  );
  if (!keys.size) return 0;
  const before = deletedRecords.length;
  deletedRecords = deletedRecords.filter((record) => !keys.has(record.key));
  return before - deletedRecords.length;
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
    reviewLeads: limitDuplicateCustomerWebsites(
      mergeRecordLists(remoteState?.reviewLeads, localState?.reviewLeads, "reviewLeads")
        .filter((record) => !deletedKeys.has(recordIdentity(record, "reviewLeads")))
        .filter((record) => !isIrrelevantReviewLead(record))
    ),
    customers: mergeRecordLists(remoteState?.customers, localState?.customers, "customers")
      .filter((record) => !deletedKeys.has(recordIdentity(record, "customers"))),
    websiteLeads: mergeRecordLists(remoteState?.websiteLeads, localState?.websiteLeads, "websiteLeads")
      .filter((record) => !deletedKeys.has(recordIdentity(record, "websiteLeads"))),
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
    ? limitDuplicateCustomerWebsites(filterReviewLeadsForBusinessFit(state.reviewLeads)
        .filter((record) => !deletedKeys.has(recordIdentity(record, "reviewLeads")))
        .map(normalizeLead))
    : [];
  customers = Array.isArray(state?.customers)
    ? state.customers.filter((record) => !deletedKeys.has(recordIdentity(record, "customers"))).map(normalizeLead)
    : [];
  websiteLeads = Array.isArray(state?.websiteLeads)
    ? state.websiteLeads.filter((record) => !deletedKeys.has(recordIdentity(record, "websiteLeads")))
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
    renderWebsiteLeads();
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

const leadCountryEvidencePatterns = {
  UAE: /(?:\+971\b|\.ae(?:\b|\/)|\b(?:united arab emirates|uae|dubai|abu dhabi|sharjah|ajman|jebel ali|al ain)\b)/i,
  "Saudi Arabia": /(?:\+966\b|\.sa(?:\b|\/)|\b(?:saudi arabia|riyadh|jeddah|dammam|khobar)\b)/i,
  Kazakhstan: /(?:\+7\s*(?:6|7)\d|\.kz(?:\b|\/)|\b(?:kazakhstan|almaty|astana|aktau|shymkent)\b)/i,
  Russia: /(?:\.ru(?:\b|\/)|\b(?:russia|moscow|st\.? petersburg|kazan|novosibirsk)\b)/i,
  Qatar: /(?:\+974\b|\.qa(?:\b|\/)|\b(?:qatar|doha|lusail|al rayyan)\b)/i,
  Kuwait: /(?:\+965\b|\.kw(?:\b|\/)|\b(?:kuwait|salmiya|shuwaikh|hawally)\b)/i,
  Uzbekistan: /(?:\+998\b|\.uz(?:\b|\/)|\b(?:uzbekistan|tashkent|samarkand|bukhara)\b)/i,
  Azerbaijan: /(?:\+994\b|\.az(?:\b|\/)|\b(?:azerbaijan|baku|ganja|sumqayit)\b)/i,
  Nigeria: /(?:\+234\b|\.ng(?:\b|\/)|\b(?:nigeria|lagos|abuja|port harcourt)\b)/i,
  Ghana: /(?:\+233\b|\.gh(?:\b|\/)|\b(?:ghana|accra|kumasi|tema)\b)/i,
  Algeria: /(?:\+213\b|\.dz(?:\b|\/)|\b(?:algeria|algerie|algiers|oran|constantine)\b)/i,
  "Côte d'Ivoire": /(?:\+225\b|\.ci(?:\b|\/)|\b(?:c[oô]te d['’]ivoire|ivory coast|abidjan|yamoussoukro)\b)/i,
  Egypt: /(?:\+20\b|\.eg(?:\b|\/)|\b(?:egypt|cairo|alexandria|giza)\b)/i,
  Kyrgyzstan: /(?:\+996\b|\.kg(?:\b|\/)|\b(?:kyrgyzstan|bishkek|osh)\b)/i,
  Ethiopia: /(?:\+251\b|\.et(?:\b|\/)|\b(?:ethiopia|addis ababa|dire dawa)\b)/i,
  Oman: /(?:\+968\b|\.om(?:\b|\/)|\b(?:oman|muscat|salalah|sohar)\b)/i,
  Armenia: /(?:\+374\b|\.am(?:\b|\/)|\b(?:armenia|yerevan|gyumri)\b)/i,
  Bahrain: /(?:\+973\b|\.bh(?:\b|\/)|\b(?:bahrain|manama|riffa|muharraq)\b)/i,
  Jordan: /(?:\+962\b|\.jo(?:\b|\/)|\b(?:jordan|amman|zarqa|irbid)\b)/i,
  Georgia: /(?:\+995\b|\.ge(?:\b|\/)|\b(?:georgia|tbilisi|batumi|rustavi)\b)/i,
  Vietnam: /(?:\+84\b|\.vn(?:\b|\/)|\b(?:vietnam|viet nam|hanoi|ho chi minh|da nang)\b)/i,
  Philippines: /(?:\+63\b|\.ph(?:\b|\/)|\b(?:philippines|manila|cebu|davao)\b)/i,
  Mexico: /(?:\+52\b|\.mx(?:\b|\/)|\b(?:mexico|monterrey|guadalajara)\b)/i,
  Brazil: /(?:\+55\b|\.br(?:\b|\/)|\b(?:brazil|brasil|s[aã]o paulo|rio de janeiro|bras[ií]lia)\b)/i,
  Chile: /(?:\+56\b|\.cl(?:\b|\/)|\b(?:chile|santiago|valpara[ií]so|concepci[oó]n)\b)/i,
  Colombia: /(?:\+57\b|\.co(?:\b|\/)|\b(?:colombia|bogot[aá]|medell[ií]n|cali)\b)/i,
  Morocco: /(?:\+212\b|\.ma(?:\b|\/)|\b(?:morocco|maroc|casablanca|rabat|tangier)\b)/i,
  China: /(?:\+86\b|\.cn(?:\b|\/)|\b(?:china|beijing|shanghai|guangzhou|shenzhen)\b|中国|北京|上海|广州|深圳)/i
};

function hasLeadCountryEvidence(raw = {}) {
  const key = countryKey(raw.country || "");
  const pattern = leadCountryEvidencePatterns[key];
  if (!pattern) return false;
  const evidence = Array.isArray(raw.evidenceSources) ? raw.evidenceSources : [];
  const aiSnippets = Array.isArray(raw.aiReview?.countryEvidenceSnippets)
    ? raw.aiReview.countryEvidenceSnippets
    : [];
  const value = [
    raw.customerWebsite,
    raw.sourceUrl,
    raw.source,
    raw.sourceExcerpt,
    raw.email,
    raw.phone,
    raw.whatsapp,
    ...aiSnippets,
    ...evidence.flatMap((item) => [item?.url, item?.title, item?.excerpt])
  ].filter(Boolean).join(" ");
  return pattern.test(value);
}

function evaluateLeadScore(text, options = {}) {
  const value = String(text || "").toLowerCase();
  const contactCount = [options.email, options.phone, options.whatsapp].filter(Boolean).length;
  const hasHuaweiFit = /huawei|harmonyos|harmony intelligent mobility|\bhima\b|\baito\b|luxeed|stelato|maextro|\bm9\b|\bm8\b|\bs800\b|\bs9\b|\br7\b|问界|智界|享界|尊界|鸿蒙智行|华为汽车|华为系/.test(value);
  const dimensions = {
    automotiveFit: /vehicle importer|car importer|automotive importer|parallel import|car distributor|vehicle distributor|authorized dealer|dealership|car dealer|auto dealer|car showroom|vehicle showroom|auto trading|automotive trading|vehicle sales|fleet sales|汽车进口|汽车经销|汽车展厅|汽车贸易|汽车销售|车队采购/.test(value)
      ? 20
      : /automotive|vehicles|cars|motors|new cars|used cars|汽车|车辆|新车|二手车/.test(value) ? 12 : 0,
    countryFit: options.countryMatch ? 20 : 0,
    chineseNev: hasHuaweiFit || /chinese ev|china ev|chinese electric vehicle|chinese new energy vehicle|byd|geely|zeekr|chery|jetour|gac aion|nio|xpeng|li auto|leapmotor|hongqi|changan|deepal|voyah|avatr|denza|中国新能源|中国电动车|中国电动汽车|中国新能源汽车|比亚迪|吉利|极氪|奇瑞|捷途|广汽埃安|蔚来|小鹏|理想|零跑|红旗|长安|深蓝|岚图|阿维塔|腾势/.test(value) ? 10 : 0,
    huaweiFit: hasHuaweiFit ? 10 : 0,
    contactCompleteness: contactCount >= 3 ? 15 : contactCount === 2 ? 10 : contactCount === 1 || options.hasContact ? 5 : 0,
    websiteTrust: options.hasOfficialWebsite ? 10 : 0,
    tradeQualification: /import.{0,8}(license|licence|permit)|export.{0,8}(license|licence|permit)|licensed importer|customs (registration|registered|code)|trade license|commercial registration|进出口资质|进出口许可证|进口许可证|出口许可证|海关注册|海关备案|报关资质|贸易许可证|授权进口商/.test(value)
      ? 8
      : /vehicle importer|car importer|parallel import|import and export|汽车进口|平行进口/.test(value) ? 5 : 0,
    purchaseIntent: 0,
    businessCapacity: /branches|locations|regional network|集团|分店|区域网络/.test(value)
      ? 4
      : /multi-brand|brand portfolio|多品牌/.test(value)
        ? 3
        : /luxury|premium|supercar|豪华|高端/.test(value) ? 2 : 0,
    decisionMaker: options.contactName || options.contactRole || /owner|founder|director|general manager|procurement manager|purchasing manager|老板|创始人|总经理|采购经理/.test(value) ? 3 : 0,
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
  let score = Math.max(0, Math.min(100, Object.values(dimensions).reduce((sum, points) => sum + points, 0)));
  if (!dimensions.automotiveFit || !dimensions.countryFit) score = Math.min(score, 49);
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

function userAssignedCountries() {
  return Array.isArray(currentSession?.assignedCountries) ? currentSession.assignedCountries : [];
}

function discoveryDisabledForSession() {
  if (currentSession?.role === "admin") return false;
  return userAssignedCountries().includes(ASSIGNED_COUNTRY_NONE);
}

function discoveryDisabledReason() {
  return "该账号未开通自动找客户功能";
}

function countryAllowedForSession(country) {
  if (currentSession?.role === "admin") return true;
  const assigned = userAssignedCountries();
  if (assigned.includes(ASSIGNED_COUNTRY_NONE)) return false;
  if (!assigned.length) return true;
  const key = countryKey(country?.name || country || "");
  return assigned.some((item) => countryKey(item) === key);
}

function visibleForeignCountries() {
  return countries.filter((country) => countryAllowedForSession(country));
}

function renderUserCountryOptions() {
  const container = $("#userAssignedCountries");
  if (!container) return;
  container.innerHTML = countryCheckboxListHtml("new-user-country", []);
}

function countryCheckboxListHtml(name, selected = []) {
  const selectedKeys = new Set((Array.isArray(selected) ? selected : []).map(countryKey));
  const noneChecked = (Array.isArray(selected) ? selected : []).includes(ASSIGNED_COUNTRY_NONE);
  const noneId = `${name}-none`;
  const noneOption = `
    <label class="user-country-option user-country-option-none" for="${escapeHtml(noneId)}">
      <input id="${escapeHtml(noneId)}" type="checkbox" name="${escapeHtml(name)}" value="${ASSIGNED_COUNTRY_NONE}" data-country-none ${noneChecked ? "checked" : ""}>
      <span>无</span>
    </label>
  `;
  return noneOption + countries.map((country) => {
    const id = `${name}-${countryKey(country.name).replace(/[^a-z0-9]+/gi, "-")}`;
    return `
      <label class="user-country-option" for="${escapeHtml(id)}">
        <input id="${escapeHtml(id)}" type="checkbox" name="${escapeHtml(name)}" value="${escapeHtml(country.name)}" ${!noneChecked && selectedKeys.has(countryKey(country.name)) ? "checked" : ""}>
        <span>${escapeHtml(country.name)}</span>
      </label>
    `;
  }).join("");
}

function selectedUserCountryValues(container) {
  const checked = Array.from(container?.querySelectorAll("input[type='checkbox']:checked") || []);
  if (checked.some((input) => input.value === ASSIGNED_COUNTRY_NONE)) return [ASSIGNED_COUNTRY_NONE];
  return checked
    .map((input) => input.value)
    .filter(Boolean);
}

function syncCountryNoneCheckbox(container, changedInput) {
  if (!container || !changedInput?.checked) return;
  const inputs = Array.from(container.querySelectorAll("input[type='checkbox']"));
  if (changedInput.value === ASSIGNED_COUNTRY_NONE) {
    inputs.forEach((input) => {
      if (input !== changedInput) input.checked = false;
    });
  } else {
    inputs.forEach((input) => {
      if (input.value === ASSIGNED_COUNTRY_NONE) input.checked = false;
    });
  }
}

function assignedCountrySummary(values = []) {
  const assigned = Array.isArray(values) ? values : [];
  if (assigned.includes(ASSIGNED_COUNTRY_NONE)) return "无";
  if (!assigned.length) return "全部国外国家";
  if (assigned.length <= 2) return assigned.join("、");
  return `${assigned.slice(0, 2).join("、")} 等 ${assigned.length} 个国家`;
}

function scheduleSalesUsers() {
  return adminUsers.filter((user) =>
    user?.role === "user"
    && user?.status !== "disabled"
    && !user?.builtIn
  );
}

function allSalesScheduleAssignments(targetUsername = "") {
  const selectedUsername = String(targetUsername || $("#scheduleTargetUsername")?.value || "").trim();
  return scheduleSalesUsers().flatMap((user) => {
    if (selectedUsername && user.username !== selectedUsername) return [];
    const assigned = (Array.isArray(user.assignedCountries) ? user.assignedCountries : [])
      .map((country) => String(country || "").trim())
      .filter(Boolean);
    if (!assigned.length || assigned.includes(ASSIGNED_COUNTRY_NONE)) return [];
    return assigned.map((country) => ({ username: user.username, country }));
  });
}

function renderScheduleTargetOptions() {
  const users = scheduleSalesUsers();
  const targetSelect = $("#scheduleTargetUsername");
  const currentTarget = String(targetSelect?.value || "").trim();
  if (targetSelect) {
    targetSelect.innerHTML = [
      `<option value="">全部销售</option>`,
      ...users.map((user) => {
        const assigned = (Array.isArray(user.assignedCountries) ? user.assignedCountries : [])
          .map((country) => String(country || "").trim())
          .filter(Boolean);
        const unavailable = !assigned.length || assigned.includes(ASSIGNED_COUNTRY_NONE);
        return `<option value="${escapeHtml(user.username)}"${unavailable ? " disabled" : ""}>${escapeHtml(user.username)}${unavailable ? "（未分配地区）" : ` · ${escapeHtml(assignedCountrySummary(assigned))}`}</option>`;
      })
    ].join("");
    targetSelect.value = users.some((user) => user.username === currentTarget) ? currentTarget : "";
  }
  const selectedTarget = String(targetSelect?.value || "").trim();
  const assignments = allSalesScheduleAssignments(selectedTarget);
  const coveredUsers = new Set(assignments.map((item) => item.username));
  const relevantUsers = selectedTarget ? users.filter((user) => user.username === selectedTarget) : users;
  const excludedUsers = relevantUsers.filter((user) => !coveredUsers.has(user.username));
  const title = $("#finderV2BulkTitle");
  if (title) title.textContent = selectedTarget || "全部启用销售";
  const summary = $("#scheduleCoverageSummary");
  if (summary) {
    summary.textContent = assignments.length
      ? `${coveredUsers.size} 名销售 · ${assignments.length} 个“销售 × 国家”每日任务`
      : "暂无已明确分配负责地区的销售";
  }
  const coverage = $("#scheduleCoverageList");
  if (coverage) {
    coverage.classList.toggle("warning", Boolean(excludedUsers.length));
    coverage.textContent = !users.length
      ? "请先在用户管理中创建销售账号并分配负责地区。"
      : excludedUsers.length
      ? `已跳过 ${excludedUsers.length} 名未分配地区的销售：${excludedUsers.map((user) => user.username).join("、")}。系统不会为其创建或执行任务。`
      : selectedTarget
      ? `${selectedTarget} 的 ${assignments.length} 个负责地区将创建定时任务。`
      : "所有启用销售都已纳入自动任务。";
  }
  const submit = $("#scheduleForm button[type='submit']");
  if (submit) {
    submit.disabled = !assignments.length;
    submit.title = assignments.length ? "" : "请先在用户管理中为销售分配明确负责国家";
  }
}

function updateAllSalesScheduleTimeLabel() {
  const value = String($("#scheduleRunTime")?.value || "06:00");
  const label = $("#scheduleDailyTime");
  if (label) label.textContent = `每天 ${value} 开始 · 每批3个`;
}

function leadRegionVerification(lead) {
  const ai = lead.aiReview && typeof lead.aiReview === "object" ? lead.aiReview : {};
  const target = [lead.country, lead.city].filter(Boolean).join(" · ") || "未指定";
  const countryEvidence = String(ai.countryEvidence || "none").toLowerCase();
  const conflict = countryEvidence === "conflict";
  const mapVerified = /google maps|openstreetmap/i.test(`${lead.origin || ""} ${lead.sourceType || ""}`) && Boolean(lead.country);
  const evidenceVerified = hasLeadCountryEvidence(lead);
  const aiVerified = ai.targetCountryMatch === true && countryEvidence === "explicit";
  const verified = !conflict && (aiVerified || mapVerified || evidenceVerified);
  const snippets = Array.isArray(ai.countryEvidenceSnippets) ? ai.countryEvidenceSnippets.filter(Boolean) : [];
  const pattern = leadCountryEvidencePatterns[countryKey(lead.country || "")];
  const sourceEvidence = (lead.evidenceSources || []).find((item) => pattern?.test([
    item?.title,
    item?.excerpt,
    item?.url
  ].filter(Boolean).join(" ")));
  const verifiedLocation = verified
    ? [ai.verifiedCountry || lead.country, ai.verifiedCity || lead.city].filter(Boolean).join(" · ")
    : conflict ? "与目标区域冲突" : "尚未获得明确地区证据";
  const evidence = snippets[0]
    || (mapVerified ? `${lead.origin || "地图来源"}企业地点数据` : "")
    || sourceEvidence?.excerpt
    || sourceEvidence?.title
    || (evidenceVerified ? "公开网址、电话区号或页面地址与目标区域匹配" : "等待官网、地图地址、当地电话或AI明确证据");
  return {
    target,
    verifiedLocation,
    evidence,
    status: conflict ? "conflict" : verified ? "verified" : "pending",
    statusLabel: conflict ? "地区冲突" : verified ? "已核实" : "待核实"
  };
}

function leadCustomerProfile(lead) {
  const ai = lead.aiReview && typeof lead.aiReview === "object" ? lead.aiReview : {};
  const profile = ai.customerProfile && typeof ai.customerProfile === "object" ? ai.customerProfile : {};
  const text = [
    lead.type,
    lead.accountType,
    ...(lead.businessSignals || []),
    ...(lead.intentSignals || []),
    lead.sourceExcerpt,
    ai.businessType,
    ai.reason
  ].filter(Boolean).join(" ").toLowerCase();
  const buyerType = profile.buyerType || ai.businessType || lead.type || lead.accountType || "汽车行业客户";
  const positioning = profile.businessPositioning
    || (/luxury|premium|supercar|豪华|高端/.test(text) ? "高端及豪华汽车销售" : "汽车经销、进口或车队业务");
  const inferredNeeds = [];
  if (/import|distribut|dealer|进口|分销|经销/.test(text)) inferredNeeds.push("中国新能源车型进口与经销合作");
  if (/fleet|rental|车队|租赁/.test(text)) inferredNeeds.push("批量采购、车队交付与售后支持");
  if (/luxury|premium|supercar|豪华|高端/.test(text)) inferredNeeds.push("高端智能新能源车型及差异化配置");
  if ((lead.recommendedModels || []).length) inferredNeeds.push(`车型方向：${lead.recommendedModels.slice(0, 3).join("、")}`);
  const likelyNeeds = Array.isArray(profile.likelyNeeds) && profile.likelyNeeds.length
    ? profile.likelyNeeds.slice(0, 4)
    : inferredNeeds.slice(0, 4);
  const businessCapacity = Number(lead.scoreDimensions?.businessCapacity || 0);
  const purchaseCapacity = profile.purchaseCapacity
    || (businessCapacity >= 4 ? "中高" : businessCapacity >= 2 ? "中" : "待核实");
  const contactStrategy = profile.contactStrategy
    || (lead.contactName || lead.contactRole
      ? `优先联系${[lead.contactName, lead.contactRole].filter(Boolean).join(" · ")}，发送车型与经销合作资料`
      : lead.email || lead.phone || lead.whatsapp
        ? "先通过现有公开联系方式确认采购负责人，再发送车型与报价资料"
        : "先从官网或公司主页补充采购负责人和有效联系方式");
  const region = leadRegionVerification(lead);
  const riskNotes = Array.isArray(profile.riskNotes) && profile.riskNotes.length
    ? profile.riskNotes.slice(0, 3)
    : [
        ...(lead.sourceCoverage?.missingFields || []).slice(0, 2).map((field) => `缺少${field}`),
        ...(region.status === "verified" ? [] : [region.statusLabel])
      ];
  const summary = profile.summary
    || `${buyerType}，业务定位为${positioning}；当前采购规模与明确采购周期仍需联系后确认。`;
  return { buyerType, positioning, likelyNeeds, purchaseCapacity, contactStrategy, riskNotes, summary };
}

function leadSkipsAiAndVerification(lead) {
  return Boolean(lead?.isManualEntryOnly || lead?.isWebsiteLead || lead?.skipInformationVerification);
}

function leadSourceBadgeHtml(lead) {
  if (lead?.isWebsiteLead) return '<span class="website-source-badge">独立站来源</span>';
  if (lead?.isImportedLead) return '<span class="imported-lead-badge">批量导入</span>';
  if (lead?.isManualLead) return '<span class="manual-lead-badge">手动添加</span>';
  return "";
}

function customerProfileHtml(lead) {
  if (leadSkipsAiAndVerification(lead)) return "";
  const profile = leadCustomerProfile(lead);
  return `
    <section class="lead-customer-profile">
      <div class="customer-profile-head">
        <strong>AI 客户画像</strong>
        <span>基于公开线索与AI复核生成</span>
      </div>
      <p class="customer-profile-summary">${escapeHtml(profile.summary)}</p>
      <dl>
        <div><dt>客户类型</dt><dd>${escapeHtml(profile.buyerType)}</dd></div>
        <div><dt>业务定位</dt><dd>${escapeHtml(profile.positioning)}</dd></div>
        <div><dt>采购能力</dt><dd>${escapeHtml(profile.purchaseCapacity)}</dd></div>
        <div><dt>潜在需求</dt><dd>${escapeHtml(profile.likelyNeeds.join("；") || "待核实")}</dd></div>
        <div class="profile-wide"><dt>联系策略</dt><dd>${escapeHtml(profile.contactStrategy)}</dd></div>
        <div class="profile-wide"><dt>待核实项</dt><dd>${escapeHtml(profile.riskNotes.join("；") || "暂无明显缺口")}</dd></div>
      </dl>
    </section>
  `;
}

function renderCountries() {
  const marketCountries = visibleForeignCountries();
  const countryCardHtml = (country) => `
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
  `;
  const primaryCountries = marketCountries.filter((country) => country.marketGroup !== "other");
  const otherCountries = marketCountries.filter((country) => country.marketGroup === "other");
  $("#countryGrid").innerHTML = discoveryDisabledForSession()
    ? `<p class="empty">${escapeHtml(discoveryDisabledReason())}。</p>`
    : [
      ...primaryCountries.map(countryCardHtml),
      ...(otherCountries.length ? [`
        <div class="country-region-heading">
          <div>
            <span class="eyebrow">扩展市场</span>
            <h3>其他可开发区域</h3>
          </div>
          <p>优先选择左舵、适合中国出口车型的东南亚、拉美、海湾及北非市场。</p>
        </div>
      `, ...otherCountries.map(countryCardHtml)] : [])
    ].join("");
  const select = $("#finderCountry");
  const current = select.value;
  const selectCountries = marketCountries.length ? marketCountries : countries;
  if (discoveryDisabledForSession()) {
    select.innerHTML = `<option value="">${escapeHtml(discoveryDisabledReason())}</option>`;
    select.disabled = true;
  } else {
  const selectPrimaryCountries = selectCountries.filter((country) => country.marketGroup !== "other");
  const selectOtherCountries = selectCountries.filter((country) => country.marketGroup === "other");
  const optionHtml = (country) => `<option value="${escapeHtml(country.name)}">${escapeHtml(country.name)}</option>`;
  select.innerHTML = `
    <optgroup label="重点目标国家">${selectPrimaryCountries.map(optionHtml).join("")}</optgroup>
    ${selectOtherCountries.length ? `<optgroup label="其他可开发区域">${selectOtherCountries.map(optionHtml).join("")}</optgroup>` : ""}
  `;
  if (selectCountries.some((country) => country.name === current)) {
    select.value = current;
  } else if (selectCountries[0]) {
    select.value = selectCountries[0].name;
  }
    select.disabled = false;
  }
  const finderSubmit = $("#finderForm button[type='submit']");
  if (finderSubmit) {
    finderSubmit.disabled = discoveryDisabledForSession();
    finderSubmit.title = discoveryDisabledForSession() ? discoveryDisabledReason() : "";
  }
  const personalScheduleSubmit = $("#personalScheduleForm button[type='submit']");
  if (personalScheduleSubmit) {
    personalScheduleSubmit.disabled = discoveryDisabledForSession();
    personalScheduleSubmit.title = discoveryDisabledForSession() ? discoveryDisabledReason() : "";
  }
  const domesticSelect = $("#finderDomesticRegion");
  if (domesticSelect) {
    const domesticCurrent = domesticSelect.value;
    domesticSelect.innerHTML = domesticRegions.map((region) =>
      `<option value="${escapeHtml(region.value)}">${escapeHtml(region.label)}</option>`
    ).join("");
    domesticSelect.value = domesticRegions.some((region) => region.value === domesticCurrent) ? domesticCurrent : "";
  }
  renderScheduleTargetOptions();
  updateFinderMarketControls();
}

function reviewReasonParts(lead) {
  const fullReason = String(lead.contactReason || lead.reason || "").trim();
  const marker = /\s*AI\u590d\u6838\s*[:\uFF1A]\s*/i;
  const markerMatch = fullReason.match(marker);
  let recommendation = fullReason;
  let aiReason = String(lead.aiReview?.reason || "").trim();
  if (markerMatch) {
    const markerIndex = markerMatch.index ?? -1;
    if (markerIndex >= 0) {
      recommendation = fullReason.slice(0, markerIndex).trim();
      aiReason = aiReason || fullReason.slice(markerIndex + markerMatch[0].length).trim();
    }
  }
  return { recommendation, aiReason };
}

function reviewAiResultHtml(lead) {
  const { aiReason } = reviewReasonParts(lead);
  return aiReason
    ? `<p class="review-title-ai"><strong>AI复核：</strong><span>${escapeHtml(aiReason)}</span></p>`
    : "";
}

function scoreDimensionHtml(label, value, maximum) {
  const score = Number(value || 0);
  return `<span class="${score > 0 ? "has-score" : ""}">${escapeHtml(label)} <strong>${escapeHtml(score)}/${escapeHtml(maximum)}</strong></span>`;
}

function selectedDomesticRegion(value = "") {
  return domesticRegions.find((item) => item.value === value) || domesticRegions[0];
}

function selectedFinderMarket(form = $("#finderForm")) {
  const domesticRegion = String(form?.domesticRegion?.value || "").trim();
  if (domesticRegion) {
    const region = selectedDomesticRegion(domesticRegion);
    return {
      isDomestic: true,
      country: "China 中国",
      domesticRegion,
      label: `China 中国 · ${domesticRegion}`,
      cities: region.cities,
      targets: region.targets,
    };
  }
  const countryName = String(form?.country?.value || countries[0]?.name || "UAE 阿联酋").trim();
  const country = countries.find((item) => item.name === countryName) || countries[0];
  return {
    isDomestic: false,
    country: country.name,
    domesticRegion: "",
    label: country.name,
    cities: country.cities,
    targets: country.targets,
  };
}

function updateFinderMarketControls() {
  const form = $("#finderForm");
  if (!form) return;
  const domesticSelected = Boolean(String(form.domesticRegion?.value || "").trim());
  if (form.country) {
    form.country.disabled = domesticSelected;
    form.country.title = domesticSelected ? "已选择国内区域，国外目标国家不参与本次搜索" : "";
  }
  if (form.sourceMode) {
    const combinedOption = [...form.sourceMode.options].find((option) => option.value === "combined");
    if (domesticSelected) {
      if (combinedOption) combinedOption.textContent = "综合搜索（国内平台 + 官网）";
      form.sourceMode.value = "combined";
      form.sourceMode.disabled = true;
      form.sourceMode.title = "国内线索统一使用综合搜索";
    } else {
      if (combinedOption) combinedOption.textContent = "综合搜索（地图 + 官网）";
      form.sourceMode.disabled = false;
      form.sourceMode.title = "";
    }
  }
}

function finderGoalText(countryName, model = "", domesticRegion = "") {
  if (domesticRegion) {
    const region = selectedDomesticRegion(domesticRegion);
    const city = (region.cities || "全国").split(" / ")[0];
    return `寻找中国${domesticRegion === "全国" ? "" : domesticRegion}${city ? `（${city}及周边）` : ""}的${region.targets}，重点筛选中国新能源、华为系车型、联系方式完整且汽车相关的真实客户。`;
  }
  const country = countries.find((item) => item.name === countryName) || countries[0];
  const city = country.cities.split(" / ")[0];
  const selectedModel = String(model || $("#finderForm")?.model?.value || DEFAULT_FINDER_MODEL).trim();
  const modelText = selectedModel ? `，适合优先推荐${selectedModel}` : "";
  return `寻找${city}及周边的${country.targets}，适合销售华为系新能源汽车${modelText}。`;
}

function syncFinderGoalToSelection() {
  const form = $("#finderForm");
  if (!form) return;
  updateFinderMarketControls();
  form.goal.value = finderGoalText(form.country.value, form.model.value, form.domesticRegion?.value || "");
  updateFinderKeywordsFromForm();
  updateSocialProspectingQueries();
}

function showDomesticDiscoveryNotice() {
  window.alert(
    "国内线索搜索正在测试中，当前数据线索较少，结果可能不准确。"
  );
}

function chooseMarket(countryName) {
  const country = countries.find((item) => item.name === countryName);
  if (!country) return;
  $("#finderCountry").value = country.name;
  const domesticSelect = $("#finderDomesticRegion");
  if (domesticSelect) domesticSelect.value = "";
  syncFinderGoalToSelection();
  showSection("lead-finder");
}

function countryKey(value) {
  const text = String(value || "");
  if (text.startsWith("Saudi Arabia")) return "Saudi Arabia";
  if (text.startsWith("Côte d'Ivoire")) return "Côte d'Ivoire";
  return text.split(" ")[0];
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
  $("#keywords").innerHTML = words.slice(0, 6).map((word) => `<span>${word}</span>`).join("");
}

function discoveryJobLeadMatches(lead, jobId) {
  return jobId === "all" || String(lead.discoveryJobId || "") === String(jobId || "");
}

function activeDiscoveryJob() {
  if (activeDiscoveryJobFilter === "all") return null;
  return discoveryJobs.find((job) => String(job.id) === String(activeDiscoveryJobFilter)) || null;
}

function discoveryJobPreviewLeads(job) {
  const found = Array.isArray(job?.result?.leads) ? job.result.leads : [];
  return found.map((lead) => normalizeLead({
    ...lead,
    sourceMode: lead.sourceMode || job?.payload?.sourceMode || job?.sourceMode || "",
    discoverySource: lead.discoverySource || job?.payload?.sourceMode || job?.sourceMode || "",
    discoveryJobId: job?.id || "",
    discoveryJobLabel: discoveryJobLabel(job)
  }));
}

function discoveryResultLeadKey(lead) {
  const id = String(lead?.id || "").trim();
  if (id) return `id:${id}`;
  return [
    normalizedLeadIdentityText(lead?.company),
    normalizedLeadIdentityText(lead?.country),
    canonicalLeadUrl(lead?.sourceUrl || lead?.customerWebsite || lead?.source)
  ].join("|");
}

function discoveryJobDisplayLeads(job) {
  const imported = reviewLeads.filter((lead) => discoveryJobLeadMatches(lead, job?.id));
  const preview = discoveryJobPreviewLeads(job);
  if (!preview.length) return imported.map((lead) => ({ ...lead, discoveryImported: true }));

  const importedByKey = new Map(imported.map((lead) => [discoveryResultLeadKey(lead), lead]));
  const displayed = preview.map((lead) => {
    const importedLead = importedByKey.get(discoveryResultLeadKey(lead));
    if (importedLead) {
      importedByKey.delete(discoveryResultLeadKey(lead));
      return { ...importedLead, discoveryImported: true };
    }
    return { ...lead, discoveryImported: false };
  });
  importedByKey.forEach((lead) => displayed.push({ ...lead, discoveryImported: true }));
  return displayed;
}

function renderLeads() {
  const job = activeDiscoveryJob();
  const filteredLeads = job
    ? discoveryJobDisplayLeads(job)
    : reviewLeads.filter((lead) => discoveryJobLeadMatches(lead, activeDiscoveryJobFilter));
  const importedCount = job ? filteredLeads.filter((lead) => lead.discoveryImported).length : filteredLeads.length;
  const summary = $("#candidateLeadSummary");
  if (summary) {
    summary.textContent = job
      ? `${discoveryJobLabel(job)}：发现 ${filteredLeads.length} 条，已进入审核 ${importedCount} 条`
      : "点击客户卡片可跳到审核详情";
  }
  $("#leadList").innerHTML = filteredLeads.length ? filteredLeads.map((lead) => `
    <article class="lead-card" ${lead.discoveryImported === false ? "" : `data-candidate-lead="${escapeHtml(lead.id || "")}" role="button" tabindex="0"`} title="${lead.discoveryImported === false ? "未达到自动导入规则" : "查看线索审核详情"}">
      <h3>${escapeHtml(lead.company)}</h3>
      <div class="lead-meta">
        <span>${escapeHtml(lead.country)} / ${escapeHtml(lead.city)}</span>
        <span>${escapeHtml(lead.type)}</span>
        <span>${escapeHtml(lead.origin || "公开网页")}</span>
        <span>${escapeHtml(lead.sourceType || "公开商业网站")}</span>
        ${job ? `<span>${lead.discoveryImported === false ? "未自动导入" : "已进入审核"}</span>` : ""}
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
const FINDER_PROGRESS_LIST_LIMIT = 3;
const MAX_ACTIVE_DISCOVERY_JOBS = 3;

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

function startButtonLoading(button, label) {
  if (!button) return () => undefined;
  stopButtonLoading(button);
  const originalText = button.textContent;
  button.disabled = true;
  let dotCount = 0;
  const render = () => {
    dotCount = (dotCount % 3) + 1;
    button.textContent = `${label}${".".repeat(dotCount)}`;
  };
  render();
  const timer = window.setInterval(render, 450);
  loadingButtonTimers.set(button, { timer, originalText });
  return (finalText = originalText, { disabled = false, autoResetMs = 0 } = {}) => {
    stopButtonLoading(button);
    button.textContent = finalText;
    button.disabled = disabled;
    if (autoResetMs) {
      window.setTimeout(() => {
        if (document.body.contains(button)) button.textContent = originalText;
      }, autoResetMs);
    }
  };
}

function stopButtonLoading(button) {
  const state = loadingButtonTimers.get(button);
  if (!state) return;
  window.clearInterval(state.timer);
  loadingButtonTimers.delete(button);
}

function activeDiscoveryJobs() {
  return discoveryJobs.filter((job) => ["queued", "running"].includes(job.status));
}

function normalizedDiscoveryJobProgress(job = {}) {
  const raw = Math.max(0, Math.min(100, Number(job.progress || 0)));
  if (job.status === "completed" || job.imported) return { percent: 100, stage: "done", state: "complete" };
  if (job.status === "failed" || job.status === "canceled") return { percent: 100, stage: "done", state: "error" };
  if (job.status === "queued") return { percent: Math.max(5, Math.min(raw || 5, 12)), stage: "search", state: "running" };
  const stage = finderStageOrder.includes(job.stage) ? job.stage : "search";
  const stageMinimum = { search: 12, extract: 36, verify: 70, done: 100 }[stage] || 12;
  const stageMaximum = { search: 35, extract: 69, verify: 94, done: 100 }[stage] || 94;
  return {
    percent: Math.max(stageMinimum, Math.min(raw || stageMinimum, stageMaximum)),
    stage,
    state: "running"
  };
}

function discoveryJobElapsedText(job = {}) {
  const start = new Date(job.createdAt || job.updatedAt || "");
  if (Number.isNaN(start.getTime())) return job.status === "queued" ? "等待执行" : "";
  if (["completed", "failed", "canceled"].includes(job.status)) {
    return formatJobTime(job.updatedAt || job.createdAt);
  }
  const seconds = Math.max(0, Math.floor((Date.now() - start.getTime()) / 1000));
  if (seconds < 60) return `已用时 ${seconds} 秒`;
  return `已用时 ${Math.floor(seconds / 60)} 分 ${seconds % 60} 秒`;
}

function renderJobProgressSteps(job = {}, progress = normalizedDiscoveryJobProgress(job)) {
  const activeIndex = finderStageOrder.indexOf(progress.stage);
  return finderStageOrder.map((stage, index) => {
    const labels = { search: "搜索", extract: "提取", verify: "核验", done: "保存" };
    const complete = activeIndex > index || (progress.stage === "done" && progress.percent === 100 && index <= activeIndex);
    const active = index === activeIndex && !complete && progress.state === "running";
    return `<span class="${complete ? "complete" : active ? "active" : ""}"><i>${complete ? "✓" : index + 1}</i>${escapeHtml(labels[stage])}</span>`;
  }).join("");
}

function renderFinderProgressList() {
  const box = $("#finderProgressList");
  if (!box) return;
  const stateLabels = discoveryJobStateLabels();
  const jobs = activeDiscoveryJobs()
    .sort((a, b) => new Date(b.createdAt || b.updatedAt || 0) - new Date(a.createdAt || a.updatedAt || 0))
    .slice(0, FINDER_PROGRESS_LIST_LIMIT);
  box.innerHTML = jobs.length ? jobs.map((job, index) => {
    const progress = normalizedDiscoveryJobProgress(job);
    const count = discoveryJobRawCount(job);
    const importedCount = discoveryJobImportedCount(job);
    const title = `${job.country || "未指定市场"} · ${job.model || "未指定车型"}`;
    const resultText = job.status === "completed"
      ? (job.imported ? `已导入 ${importedCount} 条` : `发现 ${count} 条`)
      : stateLabels[job.status] || job.status || "处理中";
    return `
      <article class="finder-progress-card ${escapeHtml(progress.state)} ${escapeHtml(job.status || "")}" data-finder-progress-job="${escapeHtml(job.id || "")}">
        <div class="finder-progress-card-head">
          <div>
            <span>#${index + 1} · ${escapeHtml(discoverySourceLabel(job.sourceMode))}</span>
            <strong>${escapeHtml(title)}</strong>
          </div>
          <div>
            <b>${progress.percent}%</b>
            <small>${escapeHtml(resultText)}</small>
          </div>
        </div>
        <div class="finder-progress-track compact" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${progress.percent}">
          <div style="width:${progress.percent}%"></div>
        </div>
        <div class="finder-progress-mini-steps">${renderJobProgressSteps(job, progress)}</div>
        <p>${escapeHtml(job.error || job.message || "任务已进入云端队列。")}<small>${escapeHtml(discoveryJobElapsedText(job))}</small></p>
      </article>
    `;
  }).join("") : "";
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
  const value = $("#reviewStatusFilter")?.value;
  return ["approved", "rejected"].includes(value) ? value : "pending";
}

function reviewSourceLeads() {
  const mode = reviewStatusMode();
  if (mode === "approved") return customers;
  if (mode === "rejected") return rejectedLeads;
  return reviewLeads;
}

function reviewModeLabel(mode = reviewStatusMode()) {
  if (mode === "approved") return "已审核客户";
  if (mode === "rejected") return "已拒绝线索";
  return "待审核线索";
}

function scheduledLeadsImportedToday() {
  const today = new Date();
  return reviewLeads.filter((lead) => {
    if (!String(lead.discoveryJobLabel || "").includes("系统定时获客")) return false;
    const importedAt = new Date(lead.discoveryJobImportedAt || "");
    return Number.isFinite(importedAt.getTime())
      && importedAt.getFullYear() === today.getFullYear()
      && importedAt.getMonth() === today.getMonth()
      && importedAt.getDate() === today.getDate();
  });
}

function renderScheduledLeadMorningNotice() {
  const notice = $("#scheduledLeadMorningNotice");
  if (!notice) return;
  const leads = currentSession?.role === "admin" ? [] : scheduledLeadsImportedToday();
  notice.hidden = !leads.length;
  if (!leads.length) return;
  const countries = Array.from(new Set(leads.map((lead) => lead.country).filter(Boolean)));
  const hour = new Date().getHours();
  const title = $("#scheduledLeadNoticeTitle");
  const text = $("#scheduledLeadNoticeText");
  if (title) title.textContent = hour < 12 ? "早上好，今日定时获客已送达" : "今日定时获客已送达";
  if (text) {
    text.textContent = `系统已为你新增 ${leads.length} 条待审核线索${countries.length ? `，来自 ${countries.slice(0, 3).join("、")}${countries.length > 3 ? ` 等 ${countries.length} 个国家` : ""}` : ""}。`;
  }
}

function renderReview(options = {}) {
  const detailOnly = Boolean(options.detailOnly);
  // Keep the review queue stable. Scores are decision support, not a reason to
  // move the card the reviewer is currently working on after manual calibration.
  const currentOpenDetails = document.querySelector("#reviewGrid details.review-more[open]");
  const currentOpenKey = currentOpenDetails?.dataset.reviewDetailKey || "";
  const currentOpenContent = currentOpenDetails?.querySelector("[data-review-detail-content]");
  if (currentOpenKey && currentOpenContent) {
    reviewDetailScrollPositions.set(currentOpenKey, currentOpenContent.scrollTop);
  }
  const previousWindowScrollY = window.scrollY;
  const reviewMode = reviewStatusMode();
  if (reviewMode === "pending") purgeIrrelevantReviewLeads();
  renderScheduledLeadMorningNotice();
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
  if (summary) summary.textContent = `显示 ${rankedLeads.length} / ${sourceLeads.length} 条 · ${reviewModeLabel(reviewMode)}${reviewMode === "pending" && reviewSelectedIds.size ? ` · 已选 ${reviewSelectedIds.size} 条` : ""}`;
  const selectVisibleButton = $("#selectVisibleReviewLeads");
  if (selectVisibleButton) {
    selectVisibleButton.disabled = reviewMode !== "pending" || !rankedLeads.length;
    selectVisibleButton.textContent = rankedLeads.length && selectedVisibleCount === rankedLeads.length ? "取消选择当前结果" : "全选当前结果";
  }
  const deleteSelectedButton = $("#deleteSelectedReviewLeads");
  if (deleteSelectedButton) {
    deleteSelectedButton.disabled = reviewMode !== "pending" || !reviewSelectedIds.size;
    deleteSelectedButton.textContent = `删除已选（${reviewSelectedIds.size}）`;
  }
  if (!rankedLeads.length) {
    const emptyText = reviewMode === "approved"
      ? "暂无已审核客户。客户池中的客户会显示在这里。"
      : reviewMode === "rejected"
        ? "暂无已拒绝线索。被拒绝的线索会显示在这里。"
        : "暂无待审核线索。一键获客抓到的客户会先出现在这里。";
    $("#reviewGrid").innerHTML = `<p class="empty">${emptyText}</p>`;
    return;
  }
  const rankedLeadRows = rankedLeads.map((record, rankIndex) => ({ ...record, rankIndex }));
  if (!selectedReviewLeadId || !visibleIds.has(selectedReviewLeadId)) {
    selectedReviewLeadId = `${reviewMode}:${rankedLeadRows[0].lead.id || rankedLeadRows[0].index}`;
  }
  const selectedRecord = rankedLeadRows.find(({ lead, index }) => `${reviewMode}:${lead.id || index}` === selectedReviewLeadId) || rankedLeadRows[0];
  const reviewListHtml = detailOnly ? "" : rankedLeadRows.map(({ lead, index, rankIndex }) => {
    const rowId = `${reviewMode}:${lead.id || index}`;
    const phoneCount = evidenceValues(lead.phoneSources, lead.phone).length + evidenceValues(lead.whatsappSources, lead.whatsapp).length;
    const missing = (lead.sourceCoverage?.missingFields || []).join("、") || "齐全";
    return `
      <article class="review-list-row ${rowId === selectedReviewLeadId ? "active" : ""}" data-review-lead-row="${escapeHtml(rowId)}" tabindex="0">
        ${reviewMode === "pending" ? `<label class="review-select"><input type="checkbox" data-review-select="${escapeHtml(lead.id)}" ${reviewSelectedIds.has(lead.id) ? "checked" : ""}><span>选择</span></label>` : `<span class="review-approved-mark">${escapeHtml(reviewModeLabel(reviewMode))}</span>`}
        <div class="review-list-main">
          <div class="review-list-company-line">
            <strong><span class="review-row-number">${rankIndex + 1}</span>${escapeHtml(lead.company)}</strong>
            ${leadSourceBadgeHtml(lead)}
          </div>
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
    const isDetailOpen = openReviewDetailKey === editId;
    const regionVerification = leadRegionVerification(lead);
    const skipVerification = leadSkipsAiAndVerification(lead);
    const entryLabel = lead.isWebsiteLead ? "客户主动提交" : "手动填写";
    return `
    <article class="review-card">
      <div class="review-title-row">
        <div class="review-title-main">
          <div class="review-card-meta">
            ${reviewMode === "pending" ? `<label class="review-select"><input type="checkbox" data-review-select="${escapeHtml(lead.id)}" ${reviewSelectedIds.has(lead.id) ? "checked" : ""}><span>选择</span></label>` : `<span class="tag">${escapeHtml(reviewModeLabel(reviewMode))}</span>`}
            <span class="tag">#${rankIndex + 1} · ${skipVerification ? entryLabel : lead.researchAt ? "已完成公开信息尽调" : "待全网补全"}</span>
            <span class="review-captured-at">${escapeHtml(formatReviewLeadTime(lead))} · ${escapeHtml(lead.source || lead.origin || "未知来源")}</span>
          </div>
          <div class="review-lead-name-row">
            <h3>${escapeHtml(lead.company)}</h3>
            ${leadSourceBadgeHtml(lead)}
            ${skipVerification ? "" : reviewAiResultHtml(lead)}
          </div>
          <p>${escapeHtml(skipVerification ? (lead.isWebsiteLead ? "此线索由客户通过独立站表单主动提交，不执行公开信息核验。" : "此客户由人工填写，未执行公开信息核验。") : lead.researchSummary || "当前仅有原始发现来源，等待系统自动核验。")}</p>
        </div>
        <div class="review-title-side">
          ${reviewMode === "pending" ? "" : `<span class="review-approved-status">${reviewMode === "approved" ? "已进入客户池" : "已拒绝，保留为历史记录"}</span>`}
        </div>
      </div>
      <div class="review-decision">
        <div class="decision-main">
          <span>系统建议</span>
          <strong>${escapeHtml(skipVerification ? (lead.isWebsiteLead ? "独立站主动询盘" : "手动录入客户") : lead.sourceCoverage?.decision || (lead.researchAt ? "建议人工复核" : "等待自动尽调"))}</strong>
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
          <dt>目标区域</dt>
          <dd>${escapeHtml(regionVerification.target)}</dd>
        </div>
        <div>
          <dt>${skipVerification ? "区域信息" : "区域核实"}</dt>
          <dd>${skipVerification ? `<span class="region-verification-status verified">${escapeHtml(entryLabel)}</span>${escapeHtml([lead.country, lead.city].filter(Boolean).join(" · ") || "未填写")}` : `<span class="region-verification-status ${regionVerification.status}">${escapeHtml(regionVerification.statusLabel)}</span>${escapeHtml(regionVerification.verifiedLocation)}`}</dd>
        </div>
        <div class="region-evidence">
          <dt>${skipVerification ? "信息来源" : "区域依据"}</dt>
          <dd>${escapeHtml(skipVerification ? (lead.isWebsiteLead ? "YIMING AUTO 独立站表单" : "人工录入，不执行自动核验") : regionVerification.evidence)}</dd>
        </div>
        <div>
          <dt>客户官网</dt>
          <dd>${safeHttpUrl(lead.customerWebsite) ? `<a href="${escapeHtml(safeHttpUrl(lead.customerWebsite))}" target="_blank" rel="noopener noreferrer">${escapeHtml(lead.customerWebsite)}</a>` : escapeHtml(lead.customerWebsite || "未发现")}</dd>
        </div>
        <div>
          <dt>联系人</dt>
          <dd>${escapeHtml([lead.contactName, lead.contactRole].filter(Boolean).join(" · ") || "未发现")}</dd>
        </div>
        <div class="key-email">
          <dt>${skipVerification ? (lead.isWebsiteLead ? "邮箱（客户提交）" : "邮箱（手动填写）") : "已核验邮箱"}</dt>
          <dd>${skipVerification ? (lead.email ? `<a class="email-address" href="mailto:${escapeHtml(lead.email)}">${escapeHtml(lead.email)}</a>` : `<span class="email-empty">未填写</span>`) : renderEmailEvidence(lead)}</dd>
        </div>
        <div>
          <dt>电话 / WhatsApp</dt>
          <dd>${renderContactSummary(lead)}</dd>
        </div>
        <div>
          <dt>${skipVerification ? "录入方式" : "可信度"}</dt>
          <dd><strong>${skipVerification ? (lead.isWebsiteLead ? "独立站客户提交" : "手动添加") : `${escapeHtml(lead.confidenceLabel || "待确认")} · ${escapeHtml(lead.confidence || 0)}%`}</strong></dd>
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
      ${customerProfileHtml(lead)}
      ${(lead.reviewNotes || (lead.attachments || []).length) ? `
        <section class="lead-review-notes">
          ${lead.reviewNotes ? `<p><strong>人工备注</strong>${escapeHtml(lead.reviewNotes)}</p>` : ""}
          ${(lead.attachments || []).length ? `<div class="lead-attachment-list">${leadAttachmentListHtml(lead.attachments)}</div>` : ""}
        </section>
      ` : ""}
      <div class="score-breakdown">
        <span>评分依据${lead.manualScoreAdjustment ? ` · 人工校准 ${lead.manualScoreAdjustment > 0 ? "+" : ""}${escapeHtml(lead.manualScoreAdjustment)}` : ""}</span>
        <div class="score-dimensions">
          ${Number(lead.scoreModelVersion || 0) >= 8 ? `
            ${scoreDimensionHtml("汽车业务", lead.scoreDimensions?.automotiveFit, 20)}
            ${scoreDimensionHtml("地区匹配", lead.scoreDimensions?.countryFit, 20)}
            ${scoreDimensionHtml("联系方式", lead.scoreDimensions?.contactCompleteness, 15)}
            ${scoreDimensionHtml("官网可信", lead.scoreDimensions?.websiteTrust, 10)}
            ${scoreDimensionHtml("中国新能源", lead.scoreDimensions?.chineseNev, 10)}
            ${scoreDimensionHtml("华为系列", lead.scoreDimensions?.huaweiFit, 10)}
            ${scoreDimensionHtml("进口分销", lead.scoreDimensions?.tradeQualification, 8)}
            ${scoreDimensionHtml("经营活跃", lead.scoreDimensions?.businessCapacity, 4)}
            ${scoreDimensionHtml("决策人", lead.scoreDimensions?.decisionMaker, 3)}
          ` : `
            ${scoreDimensionHtml("进出口资质", lead.scoreDimensions?.tradeQualification, 10)}
            ${scoreDimensionHtml("客户匹配", lead.scoreDimensions?.customerFit, 27)}
            ${scoreDimensionHtml("采购意向", lead.scoreDimensions?.purchaseIntent, 20)}
            ${scoreDimensionHtml("经营能力", lead.scoreDimensions?.businessCapacity, 14)}
            ${scoreDimensionHtml("车型匹配", lead.scoreDimensions?.modelFit, 12)}
            ${scoreDimensionHtml("可触达性", lead.scoreDimensions?.contactability, 7)}
          `}
          ${Number(lead.scoreDimensions?.penalty || 0) < 0
            ? `<span class="penalty">风险扣分 <strong>${escapeHtml(lead.scoreDimensions.penalty)}</strong></span>`
            : ""}
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
          <button class="ghost" type="button" data-review-edit="${index}" data-review-edit-id="${escapeHtml(editId)}">编辑</button>
        ` : reviewMode === "approved" ? `<button class="primary" type="button" data-section="crm">回到客户池</button>` : `<span class="review-approved-status">已拒绝线索</span>`}
      </div>
      ${reviewMode === "pending" && rejectingReviewLeadId === editId ? rejectReasonPanelHtml(index, lead) : ""}
      ${reviewMode === "rejected" && lead.rejectReason ? `<div class="reject-reason-readonly"><strong>拒绝原因</strong><p>${escapeHtml(lead.rejectReason)}</p></div>` : ""}
      ${reviewMode === "rejected" ? `<div class="restore-rejected-actions"><button class="primary" type="button" data-review-action="restore" data-index="${index}">退回未审核</button></div>` : ""}
      ${reviewMode === "pending" && isEditing ? renderLeadEditForm(lead, index, editId) : ""}
      ${skipVerification ? "" : `<details class="review-more" data-review-detail-key="${escapeHtml(editId)}" data-review-detail-id="${escapeHtml(lead.id || index)}" data-review-detail-index="${index}" data-review-detail-mode="${reviewMode}" ${isDetailOpen ? "open" : ""}>
        <summary>
          <span>查看全部来源与核验详情</span>
          <small class="review-source-badges">
            <b>${lead.sourceCoverage?.total || lead.evidenceSources?.length || 0} 个来源</b>
            <b>${(lead.socialProfiles || []).length} 个社媒账号</b>
          </small>
        </summary>
        <div class="review-more-content" data-review-detail-content></div>
      </details>`}
    </article>
  `;
  }).join("");
  const existingDetail = detailOnly ? $("#reviewGrid .review-workbench-detail") : null;
  if (existingDetail) {
    existingDetail.innerHTML = selectedDetailHtml;
    $$("#reviewGrid [data-review-lead-row]").forEach((row) => {
      const active = row.dataset.reviewLeadRow === selectedReviewLeadId;
      row.classList.toggle("active", active);
      row.setAttribute("aria-selected", String(active));
    });
  } else {
    $("#reviewGrid").innerHTML = `
      <div class="review-workbench">
        <aside class="review-workbench-list" aria-label="待审核线索列表">
          <div class="review-workbench-list-head">
            <strong>${escapeHtml(reviewModeLabel(reviewMode))}</strong>
            <span>${rankedLeadRows.length} 条</span>
          </div>
          <div class="review-list-scroll">${reviewListHtml}</div>
        </aside>
        <section class="review-workbench-detail">${selectedDetailHtml}</section>
      </div>
    `;
  }
  if (openReviewDetailKey) {
    const openDetails = $$("#reviewGrid details.review-more[open]").find(
      (details) => details.dataset.reviewDetailKey === openReviewDetailKey
    );
    const openContent = openDetails?.querySelector("[data-review-detail-content]");
    if (openContent) {
      const savedScrollTop = reviewDetailScrollPositions.get(openReviewDetailKey) || 0;
      hydrateReviewDetail(openDetails, savedScrollTop);
      requestAnimationFrame(() => window.scrollTo({ top: previousWindowScrollY, behavior: "auto" }));
    } else {
      openReviewDetailKey = "";
    }
  }
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

function formatBytes(bytes = 0) {
  const value = Number(bytes || 0);
  if (value >= 1024 * 1024) return `${(value / 1024 / 1024).toFixed(1)} MB`;
  if (value >= 1024) return `${Math.round(value / 1024)} KB`;
  return `${value} B`;
}

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(reader.error || new Error("文件读取失败"));
    reader.readAsDataURL(file);
  });
}

async function leadAttachmentsFromInput(input, existing = []) {
  const files = Array.from(input?.files || []);
  const keptExisting = Array.isArray(existing) ? existing.slice(0, maxLeadAttachmentCount) : [];
  const available = Math.max(0, maxLeadAttachmentCount - keptExisting.length);
  const accepted = files.slice(0, available).filter((file) => file.size <= maxLeadAttachmentBytes);
  const skipped = files.length - accepted.length;
  const next = [...keptExisting];
  for (const file of accepted) {
    next.push({
      id: `att-${Date.now().toString(36)}-${Math.random().toString(16).slice(2)}`,
      name: file.name,
      type: file.type || "application/octet-stream",
      size: file.size,
      dataUrl: await readFileAsDataUrl(file),
      createdAt: new Date().toISOString()
    });
  }
  return { attachments: next.slice(0, maxLeadAttachmentCount), skipped };
}

function leadAttachmentListHtml(attachments = []) {
  const items = Array.isArray(attachments) ? attachments : [];
  if (!items.length) return `<p class="lead-attachment-empty">暂无附件。</p>`;
  return items.map((item) => {
    const isImage = String(item.type || "").startsWith("image/");
    const suffix = String(item.name || "FILE").split(".").pop()?.slice(0, 4).toUpperCase() || "FILE";
    return `
      <a class="lead-attachment-chip" href="${escapeHtml(item.dataUrl || "#")}" target="_blank" rel="noopener noreferrer" title="${escapeHtml(item.name || "")}">
        ${isImage ? `<img src="${escapeHtml(item.dataUrl || "")}" alt="">` : `<span>${escapeHtml(suffix)}</span>`}
        <b>${escapeHtml(item.name || "附件")}</b>
        <small>${escapeHtml(formatBytes(item.size))}</small>
      </a>
    `;
  }).join("");
}

function rejectReasonPanelHtml(index, lead) {
  const currentReason = lead.rejectReason || "";
  const isPreset = rejectReasonOptions.includes(currentReason);
  return `
    <div class="reject-reason-panel" data-reject-reason-panel="${index}">
      <strong>请选择拒绝原因</strong>
      <div class="reject-reason-options">
        ${rejectReasonOptions.map((reason, optionIndex) => `
          <label>
            <input type="radio" name="rejectReason-${index}" value="${escapeHtml(reason)}" ${currentReason === reason || (!currentReason && optionIndex === 0) ? "checked" : ""}>
            <span>${escapeHtml(reason)}</span>
          </label>
        `).join("")}
        <label>
          <input type="radio" name="rejectReason-${index}" value="__other" ${currentReason && !isPreset ? "checked" : ""}>
          <span>其他原因</span>
        </label>
      </div>
      <textarea data-reject-other rows="3" placeholder="手动填写其他拒绝原因">${escapeHtml(currentReason && !isPreset ? currentReason : "")}</textarea>
      <div class="reject-reason-actions">
        <button class="danger-button" type="button" data-review-reject-confirm="${index}">确认拒绝</button>
        <button class="ghost" type="button" data-review-reject-cancel>取消</button>
      </div>
    </div>
  `;
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
        <label class="lead-edit-wide">人工备注
          <textarea name="reviewNotes" rows="4" placeholder="可记录人工判断、截图说明、客户补充信息">${escapeHtml(lead.reviewNotes || "")}</textarea>
        </label>
        <label class="lead-edit-wide lead-file-field">照片 / 附件备注
          <input name="attachments" type="file" accept="${escapeHtml(leadAttachmentAccept)}" multiple>
          <small>支持图片、PDF、Word、Excel、CSV、TXT、MD、RTF；单个不超过 ${formatBytes(maxLeadAttachmentBytes)}，最多 ${maxLeadAttachmentCount} 个。新上传会追加到已有附件。</small>
        </label>
        <div class="lead-edit-wide lead-attachment-list">${leadAttachmentListHtml(lead.attachments)}</div>
      </div>
      <div class="lead-edit-actions">
        <button class="primary" type="submit">保存修改</button>
        <button class="ghost" type="button" data-review-edit-cancel>取消</button>
      </div>
    </form>
  `;
}

async function saveReviewLeadEdit(index, form) {
  const lead = reviewLeads[index];
  if (!lead || !form) return;
  const data = Object.fromEntries(new FormData(form).entries());
  const emails = splitLeadEditLines(data.emails).map((item) => item.toLowerCase());
  const phones = splitLeadEditLines(data.phones);
  const whatsapps = splitLeadEditLines(data.whatsapps);
  const recommendedModels = splitLeadEditLines(data.recommendedModels);
  const signals = splitLeadEditLines(data.signals);
  const source = manualEvidenceSource(lead);
  const attachmentInput = form.querySelector('input[name="attachments"]');
  const { attachments } = await leadAttachmentsFromInput(attachmentInput, lead.attachments || []);
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
    emailSources,
    phone: phones[0] || "",
    phoneSources: manualValueSources(phones, lead),
    whatsapp: whatsapps[0] || "",
    whatsappSources: manualValueSources(whatsapps, lead),
    recommendedModels: recommendedModels.length ? recommendedModels : lead.recommendedModels,
    intentSignals: signals,
    businessSignals: [],
    reviewNotes: String(data.reviewNotes || "").trim(),
    attachments,
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
              <p>这里展示系统已经采集到的公司官方账号和公开个人决策人账号。</p>
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
          `).join("") : `<p class="empty">尚未建立公开证据链。</p>`}
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
  const mode = details?.dataset?.reviewDetailMode;
  const leads = mode === "approved" ? customers : mode === "rejected" ? rejectedLeads : reviewLeads;
  return leads.find((lead) => String(lead.id || "") === id) || leads[index] || null;
}

function clearReviewDetail(details) {
  const content = details?.querySelector("[data-review-detail-content]");
  if (!content) return;
  content.textContent = "";
  content.classList.remove("is-loading");
  delete content.dataset.loaded;
  delete content.dataset.hydrating;
}

function closeOpenReviewDetails(except = null) {
  $$("#reviewGrid details.review-more[open]").forEach((details) => {
    if (details !== except) details.removeAttribute("open");
  });
}

function hydrateReviewDetail(details, restoreScrollTop = 0) {
  const content = details?.querySelector("[data-review-detail-content]");
  if (!content) return;
  if (content.dataset.loaded === "true") {
    requestAnimationFrame(() => { content.scrollTop = restoreScrollTop; });
    return;
  }
  const hydrationId = String(++reviewDetailHydrationId);
  content.dataset.hydrating = hydrationId;
  content.classList.add("is-loading");
  content.innerHTML = `<div class="review-detail-loading" role="status"><span></span><b>正在加载来源与核验详情</b></div>`;
  requestAnimationFrame(() => requestAnimationFrame(() => {
    if (!details.open || content.dataset.hydrating !== hydrationId) return;
    const lead = reviewDetailLead(details);
    content.innerHTML = lead
      ? renderReviewDetailContent(lead)
      : `<p class="empty">详情已刷新，请重新打开线索。</p>`;
    content.classList.remove("is-loading");
    content.dataset.loaded = "true";
    delete content.dataset.hydrating;
    content.scrollTop = restoreScrollTop;
  }));
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
  ["linkedin", "LinkedIn 公司 / 个人主页"]
];

function classifySourceText(value) {
  const concreteValue = String(value || "").toLowerCase();
  if (!concreteValue) return "";
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
  return "";
}

function reviewSourceKey(lead) {
  const primaryValue = [
    lead.platform,
    lead.origin,
    lead.sourceType,
    lead.sourceTitle,
    lead.source,
    lead.sourceUrl
  ].filter(Boolean).join(" ");
  const primaryKey = classifySourceText(primaryValue);
  if (primaryKey) return primaryKey;
  const evidenceValue = (lead.evidenceSources || []).flatMap((source) => [
    source.sourceName,
    source.sourceType,
    source.url
  ]).filter(Boolean).join(" ");
  const evidenceKey = classifySourceText(evidenceValue);
  if (evidenceKey) return evidenceKey;
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

function reviewLeadSearchText(lead) {
  return [
    lead.company,
    lead.customerWebsite,
    lead.website,
    lead.email,
    lead.phone,
    lead.whatsapp,
    lead.country,
    lead.city,
    lead.origin,
    lead.source,
    lead.sourceUrl,
    lead.sourceTitle,
    lead.sourceType,
    lead.platform,
    lead.discoveryJobLabel,
    lead.contactName,
    lead.contactRole,
    lead.contactReason,
    lead.reason,
    lead.reviewNotes,
    lead.rejectReason,
    ...(lead.emailSources || []).flatMap((item) => [item.email, ...(item.sources || []).map((source) => source.url)]),
    ...(lead.phoneSources || []).map((item) => item.value),
    ...(lead.whatsappSources || []).map((item) => item.value),
    ...(lead.recommendedModels || []),
    ...(lead.intentSignals || []),
    ...(lead.businessSignals || []),
    ...(lead.evidenceSources || []).flatMap((source) => [
      source.sourceName,
      source.sourceType,
      source.url,
      source.excerpt
    ])
  ].filter(Boolean).join(" ").toLowerCase();
}

function reviewSourceHost(value) {
  try {
    return new URL(/^https?:\/\//i.test(String(value || "")) ? String(value || "") : `https://${value}`).hostname
      .replace(/^www\./, "")
      .toLowerCase();
  } catch {
    return "";
  }
}

function reviewConcreteSourceOptions(lead) {
  const options = new Map();
  const add = (label, value = "") => {
    const text = String(label || "").trim();
    const host = reviewSourceHost(value || text);
    const cleanLabel = text && !/^https?:\/\//i.test(text) ? text : host;
    const key = (host || cleanLabel).toLowerCase();
    const blockedHosts = ["google.", "youtube.", "youtu.be", "openstreetmap.org", "facebook.", "instagram.", "tiktok.", "linkedin.", "twitter.", "x.com"];
    if (!key || ["google", "google maps", "openstreetmap", "youtube", "facebook", "instagram"].includes(key)) return;
    if (host && blockedHosts.some((item) => host.includes(item))) return;
    if (["公开网页", "公开来源", "原始来源", "综合搜索", "Local automotive directory", "公开商业信息网站", "车商官网或汽车行业网站"].includes(cleanLabel)) return;
    options.set(`specific:${key}`, cleanLabel || key);
  };
  add(lead.origin, lead.sourceUrl || lead.source);
  add(lead.sourceTitle, lead.sourceUrl || lead.source);
  add(lead.sourceType, lead.sourceUrl || lead.source);
  add(lead.sourceUrl || lead.source);
  (lead.evidenceSources || []).forEach((source) => {
    add(source.sourceName || source.name, source.url);
    add(source.url);
  });
  (lead.emailSources || []).forEach((item) => {
    (item.sources || []).forEach((source) => add(source.name, source.url));
  });
  (lead.phoneSources || []).forEach((item) => {
    (item.sources || []).forEach((source) => add(source.name, source.url));
  });
  (lead.whatsappSources || []).forEach((item) => {
    (item.sources || []).forEach((source) => add(source.name, source.url));
  });
  return [...options.entries()];
}

function reviewLeadConcreteSourceKeys(lead) {
  return new Set(reviewConcreteSourceOptions(lead).map(([value]) => value));
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
  const current = sourceSelect?.value?.startsWith("specific:") ? "all" : (sourceSelect?.value || "all");
  const available = new Set(sourceLeads.map(reviewSourceKey));
  if (sourceSelect) {
    const options = reviewSourceOptions
      .filter(([value]) => available.has(value) || value === current)
      .map(([value, label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`)
      .join("");
    sourceSelect.innerHTML = `<option value="all">\u5168\u90e8\u6765\u6e90</option>${options || reviewSourceOptions.map(([value, label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`).join("")}`;
    sourceSelect.value = current === "all" || available.has(current) ? current : "all";
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
    countrySelect.innerHTML = `<option value="all">\u5168\u90e8\u56fd\u5bb6</option>${countryOptionHtml}`;
    countrySelect.value = currentCountry === "all" || countryOptions.has(currentCountry) ? currentCountry : "all";
  }

  if (discoverySelect) {
    const currentDiscovery = discoverySelect.value || "all";
    const options = discoveryJobFilterOptions(sourceLeads);
    discoverySelect.innerHTML = `<option value="all">\u5168\u90e8\u641c\u7d22\u8bb0\u5f55</option>${options.map(([value, label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`).join("")}`;
    discoverySelect.value = currentDiscovery === "all" || options.some(([value]) => value === currentDiscovery) ? currentDiscovery : "all";
  }
}

function reviewLeadMatchesFilters(lead) {
  const discoveryFilter = $("#reviewDiscoveryFilter")?.value || "all";
  const timeFilter = $("#reviewTimeFilter")?.value || "all";
  const sourceFilter = $("#reviewSourceFilter")?.value || "all";
  const countryFilter = $("#reviewCountryFilter")?.value || "all";
  const tierFilter = $("#reviewTierFilter")?.value || "all";
  const searchQuery = String($("#reviewSearchInput")?.value || "").trim().toLowerCase();
  const source = reviewSourceKey(lead);
  if (discoveryFilter !== "all" && String(lead.discoveryJobId || "") !== discoveryFilter) return false;
  if (sourceFilter !== "all") {
    if (sourceFilter.startsWith("specific:")) {
      if (!reviewLeadConcreteSourceKeys(lead).has(sourceFilter)) return false;
    } else if (source !== sourceFilter) {
      return false;
    }
  }
  if (countryFilter !== "all" && reviewLeadCountryKey(lead) !== countryFilter) return false;
  if (tierFilter !== "all" && lead.scoreTier !== tierFilter) return false;
  if (searchQuery && !reviewLeadSearchText(lead).includes(searchQuery)) return false;
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

function websiteLeadStatusLabel(status) {
  return {
    new: "新提交",
    imported: "已导入审核",
    done: "已处理"
  }[status] || "新提交";
}

function websiteLeadModelLabel(lead) {
  return lead.modelLine || lead.model || "未指定车型";
}

function websiteLeadCommercialDetails(lead) {
  return [
    lead.buyerType ? `采购方：${lead.buyerType}` : "",
    lead.modelVersion ? `版本：${lead.modelVersion}` : "",
    lead.purchaseTimeline ? `周期：${lead.purchaseTimeline}` : "",
    lead.tradeTerm ? `条款：${lead.tradeTerm}` : ""
  ].filter(Boolean).join(" · ");
}

function websiteLeadDetectedCountryLabel(lead) {
  const code = String(lead?.detectedCountry || "").trim().toUpperCase();
  if (!/^[A-Z]{2}$/.test(code)) return "";
  try {
    const name = new Intl.DisplayNames(["zh-CN"], { type: "region" }).of(code);
    return name && name !== code ? `${name} (${code})` : code;
  } catch {
    return code;
  }
}

function websiteLeadToReviewLead(lead) {
  const text = [
    lead.company,
    lead.country,
    websiteLeadModelLabel(lead),
    lead.quantity ? `数量 ${lead.quantity}` : "",
    lead.message,
    lead.contact
  ].filter(Boolean).join(" ");
  return normalizeLead({
    id: `review-${lead.id || Date.now()}`,
    company: lead.company || "官网询盘客户",
    country: lead.country || "",
    city: "",
    type: "Official website inquiry",
    source: lead.sourceUrl || "https://www.yiming-auto.com/#contact",
    origin: "独立站来源",
    sourceType: "独立站客户表单",
    sourceTitle: `${lead.company || "Website inquiry"} · ${websiteLeadModelLabel(lead)}`,
    sourceUrl: lead.sourceUrl || "https://www.yiming-auto.com/#contact",
    sourceExcerpt: lead.message || text,
    evidenceSources: [{
      title: "YIMING AUTO official website form",
      url: lead.sourceUrl || "https://www.yiming-auto.com/#contact",
      excerpt: text,
      sourceName: "Official website",
      sourceType: "Inbound inquiry"
    }],
    email: lead.email || "",
    whatsapp: lead.whatsapp || "",
    model: lead.model || websiteLeadModelLabel(lead),
    website: text,
    isWebsiteLead: true,
    skipInformationVerification: true,
    aiReview: {},
    confidence: 0,
    confidenceLabel: "客户主动提交",
    sourceCoverage: {
      total: 1,
      official: 1,
      independentDomains: 0,
      contactable: Boolean(lead.email || lead.whatsapp || lead.contact),
      missingFields: [],
      decision: "独立站主动询盘"
    },
    reason: `官网主动询盘：${lead.country || "未填写地区"}，${websiteLeadModelLabel(lead)}，预计 ${lead.quantity || 1} 台。`,
    next: "先确认国家、车型、数量、配置和交付时间，再生成开发信或报价。",
    createdAt: lead.createdAt || lead.receivedAt || new Date().toISOString(),
    websiteLeadId: lead.id || ""
  });
}

function renderWebsiteLeads() {
  const count = $("#websiteLeadCount");
  if (count) count.textContent = websiteLeads.filter((lead) => lead.status !== "done").length;
  const tbody = $("#websiteLeadRows");
  if (!tbody) return;
  tbody.innerHTML = websiteLeads.length ? websiteLeads.map((lead, index) => `
    <tr>
      <td><strong>${escapeHtml(lead.company || "未填写")}</strong><br><span>${escapeHtml(lead.contact || lead.email || lead.whatsapp || "无联系方式")}</span></td>
      <td>${escapeHtml(lead.country || "-")}${lead.detectedCountry ? `<br><small>访客定位：${escapeHtml(websiteLeadDetectedCountryLabel(lead))} · ${escapeHtml((lead.detectedLanguage || "en").toUpperCase())}</small>` : ""}</td>
      <td>${escapeHtml(websiteLeadModelLabel(lead))}<br><span>${escapeHtml(String(lead.quantity || 1))} 台</span></td>
      <td>${escapeHtml(lead.message || "-")}${websiteLeadCommercialDetails(lead) ? `<br><small>${escapeHtml(websiteLeadCommercialDetails(lead))}</small>` : ""}</td>
      <td><span class="website-lead-status ${escapeHtml(lead.status || "new")}">${escapeHtml(websiteLeadStatusLabel(lead.status))}</span><br><small>${escapeHtml(formatJobTime(lead.receivedAt || lead.createdAt))}</small></td>
      <td>
        <div class="crm-actions">
          <button type="button" data-website-lead-action="import" data-index="${index}">导入审核</button>
          <button type="button" data-website-lead-action="done" data-index="${index}">标记处理</button>
          <button type="button" data-website-lead-action="delete" data-index="${index}">删除</button>
        </div>
      </td>
    </tr>
  `).join("") : `<tr><td colspan="6">暂无独立站提交线索。客户在官网表单提交后会出现在这里。</td></tr>`;
}

function importWebsiteLead(index) {
  const lead = websiteLeads[index];
  if (!lead) return;
  const reviewLead = websiteLeadToReviewLead(lead);
  const exists = [...reviewLeads, ...customers].some((item) =>
    String(item.websiteLeadId || item.id || "") === String(lead.id || "")
  );
  if (!exists) reviewLeads.unshift(reviewLead);
  websiteLeads[index] = { ...lead, status: "imported", importedAt: new Date().toISOString() };
  selectedReviewLeadId = `pending:${reviewLead.id}`;
  refreshAllLeadViews();
  showSection("review");
}

function updateWebsiteLeadStatus(index, status) {
  const lead = websiteLeads[index];
  if (!lead) return;
  websiteLeads[index] = { ...lead, status, updatedAt: new Date().toISOString() };
  refreshAllLeadViews();
}

function deleteWebsiteLead(index) {
  const lead = websiteLeads[index];
  if (!lead) return;
  rememberDeletedRecord(lead, "websiteLeads");
  websiteLeads.splice(index, 1);
  refreshAllLeadViews();
}

function crmLeadSearchText(lead) {
  return [
    lead.company,
    lead.country,
    lead.city,
    lead.type,
    lead.model,
    lead.email,
    lead.phone,
    lead.whatsapp,
    lead.website,
    lead.source,
    lead.stage,
    lead.next
  ].filter(Boolean).join(" ").toLowerCase();
}

function crmPhoneHref(value) {
  const raw = String(value || "").trim();
  const digits = raw.replace(/[^\d+]/g, "");
  if (!digits || digits.replace(/\D/g, "").length < 5) return "";
  return `tel:${digits}`;
}

function crmWhatsappHref(value) {
  const raw = String(value || "").trim();
  const digits = raw.replace(/\D/g, "");
  if (!digits || digits.length < 5) return "";
  return `https://wa.me/${digits}`;
}

function crmWebsiteHref(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";
  return /^https?:\/\//i.test(raw) ? raw : `https://${raw}`;
}

function crmLeadContactSummary(lead) {
  const contacts = [];
  const email = primaryEmailForLead(lead);
  if (email) contacts.push({ type: "email", label: "邮箱", value: email, href: `mailto:${encodeURIComponent(email)}` });
  if (lead.phone) contacts.push({ type: "phone", label: "电话", value: lead.phone, href: crmPhoneHref(lead.phone) });
  if (lead.whatsapp) contacts.push({ type: "whatsapp", label: "WhatsApp", value: lead.whatsapp, href: crmWhatsappHref(lead.whatsapp), external: true });
  if (lead.website) contacts.push({ type: "website", label: "官网", value: lead.website, href: crmWebsiteHref(lead.website), external: true });
  return contacts.slice(0, 4).map(({ type, label, value, href, external }) => href ? `
    <a data-contact-type="${escapeHtml(type)}" href="${escapeHtml(href)}" title="${escapeHtml(value)}"${external ? ` target="_blank" rel="noopener noreferrer"` : ""}>${escapeHtml(label)}</a>
  ` : `
    <span data-contact-type="${escapeHtml(type)}" title="${escapeHtml(value)}">${escapeHtml(label)}</span>
  `).join("") || `<span class="muted">缺少联系方式</span>`;
}

function crmLeadPriorityNote(lead) {
  const score = Number(lead.score || 0);
  if (score >= 80) return "优先联系，可直接生成开发信";
  if (score >= 65) return "适合跟进，建议人工确认需求";
  if (score >= 50) return "一般线索，先补联系方式和官网证据";
  return "低分线索，建议重新核验后再推进";
}

function crmFollowSortValue(lead, today) {
  if (["已成交", "已流失"].includes(lead.stage)) return 999999;
  if (!lead.nextFollowAt) return 0;
  const leadDate = new Date(`${lead.nextFollowAt}T00:00:00`).getTime();
  const todayDate = new Date(`${today}T00:00:00`).getTime();
  if (!Number.isFinite(leadDate) || !Number.isFinite(todayDate)) return 999998;
  return Math.round((leadDate - todayDate) / 86400000);
}

function crmRecentValue(lead) {
  const raw = lead.approvedAt || lead.researchAt || lead.createdAt || lead.updatedAt || "";
  const time = new Date(raw).getTime();
  return Number.isFinite(time) ? time : 0;
}

function sortCrmCustomers(rows, today) {
  return rows.sort((a, b) => {
    if (crmSortBy === "score") return Number(b.lead.score || 0) - Number(a.lead.score || 0);
    if (crmSortBy === "follow") return crmFollowSortValue(a.lead, today) - crmFollowSortValue(b.lead, today);
    if (crmSortBy === "recent") return crmRecentValue(b.lead) - crmRecentValue(a.lead);
    const tierRank = { A: 4, B: 3, C: 2, D: 1 };
    const aRank = (tierRank[a.lead.scoreTier] || 0) * 1000 + Number(a.lead.score || 0) - Math.max(0, crmFollowSortValue(a.lead, today));
    const bRank = (tierRank[b.lead.scoreTier] || 0) * 1000 + Number(b.lead.score || 0) - Math.max(0, crmFollowSortValue(b.lead, today));
    return bRank - aRank;
  });
}

function syncCrmControls() {
  const stageSelect = $("#crmStageFilter");
  if (stageSelect) {
    const current = crmStageFilter;
    stageSelect.innerHTML = `<option value="all">全部阶段</option>${salesStages.map((stage) =>
      `<option value="${escapeHtml(stage)}">${escapeHtml(stage)}</option>`
    ).join("")}`;
    stageSelect.value = [...stageSelect.options].some((option) => option.value === current) ? current : "all";
    crmStageFilter = stageSelect.value;
  }
  const searchInput = $("#crmSearchInput");
  if (searchInput && searchInput.value !== crmSearchQuery) searchInput.value = crmSearchQuery;
  const tierSelect = $("#crmTierFilter");
  if (tierSelect) tierSelect.value = crmTierFilter;
  const sortSelect = $("#crmSortBy");
  if (sortSelect) sortSelect.value = crmSortBy;
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
  syncCrmControls();
  const normalizedSearch = crmSearchQuery.trim().toLowerCase();
  const filteredCustomers = sortCrmCustomers(customers.map((lead, index) => ({ lead, index })).filter(({ lead }) => {
    if (crmViewFilter === "due") return !["已成交", "已流失"].includes(lead.stage) && (!lead.nextFollowAt || lead.nextFollowAt <= today);
    if (crmViewFilter === "overdue") return !["已成交", "已流失"].includes(lead.stage) && lead.nextFollowAt && lead.nextFollowAt < today;
    if (crmViewFilter === "missing") return !["已成交", "已流失"].includes(lead.stage) && !lead.nextFollowAt;
    if (crmViewFilter === "priority") return ["A", "B"].includes(lead.scoreTier);
    return true;
  }).filter(({ lead }) => {
    if (crmTierFilter !== "all" && lead.scoreTier !== crmTierFilter) return false;
    if (crmStageFilter !== "all" && lead.stage !== crmStageFilter) return false;
    if (normalizedSearch && !crmLeadSearchText(lead).includes(normalizedSearch)) return false;
    return true;
  }), today);
  const viewHint = $("#crmViewHint");
  if (viewHint) viewHint.textContent = {
    all: `显示全部 ${customers.length} 位客户池客户。`,
    due: `优先处理今天需要推进的 ${dueCustomers.length} 位客户。`,
    overdue: `共有 ${overdueCustomers.length} 位客户已超过计划跟进日期。`,
    missing: `共有 ${missingCustomers.length} 位客户尚未设定下一次跟进日期。`,
    priority: `显示评分为 A / B 的 ${priorityCustomers.length} 位高价值客户。`
  }[crmViewFilter];
  $("#crmRows").innerHTML = filteredCustomers.length ? filteredCustomers.map(({ lead, index }) => `
    <tr class="crm-row">
      <td>
        <div class="crm-customer-title">
          <button class="link-button crm-customer-link" type="button" data-crm-action="review" data-index="${index}">${escapeHtml(lead.company)}</button>
          ${leadSourceBadgeHtml(lead)}
        </div>
        <div class="crm-contact-line">${escapeHtml(lead.contactName || primaryEmailForLead(lead) || lead.phone || "暂无联系人")}</div>
        <div class="crm-contact-chips">${crmLeadContactSummary(lead)}</div>
      </td>
      <td>
        <strong>${escapeHtml(lead.country || "未知国家")}</strong><br>
        <span>${escapeHtml(lead.city || "未填城市")}</span>
        <small>${escapeHtml(lead.source || "未知来源")}</small>
      </td>
      <td>${escapeHtml(lead.type)}</td>
      <td>${escapeHtml(lead.model)}</td>
      <td>
        <span class="score ${scoreVisualClass(lead.score)}">${lead.score} · ${escapeHtml(lead.scoreTier || "D")}级</span>
        <small class="crm-priority-note">${escapeHtml(crmLeadPriorityNote(lead))}</small>
      </td>
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
  `).join("") : `<tr><td colspan="9">当前筛选条件下没有符合条件的客户。</td></tr>`;
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
  renderWebsiteLeads();
  renderFollowTasks();
  renderKpis();
  renderQuoteHistory();
  renderQuoteCustomerSelect();
  renderAfterSales();
  saveState();
}

function primaryLeadPageEmailRecord(raw) {
  const primaryUrls = new Set([
    raw?.sourceUrl,
    ...(Array.isArray(raw?.socialProfiles)
      ? raw.socialProfiles
          .filter((profile) => /原线索|手动网址解析/.test(String(profile?.relationship || "")))
          .map((profile) => profile?.url)
      : [])
  ].map(canonicalLeadUrl).filter(Boolean));
  if (!primaryUrls.size) return null;
  return (Array.isArray(raw?.unverifiedEmailCandidates) ? raw.unverifiedEmailCandidates : []).find((record) => (
    /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(String(record?.email || "").trim())
    && (record.sources || []).some((source) => primaryUrls.has(canonicalLeadUrl(source?.url)))
  )) || null;
}

function normalizeLead(raw) {
  const isWebsiteLead = Boolean(
    raw.isWebsiteLead
    || raw.websiteLeadId
    || /official website form|独立站客户表单/i.test(String(raw.sourceType || ""))
    || /official website|独立站来源/i.test(String(raw.origin || ""))
  );
  const primaryPageEmail = raw.email ? null : primaryLeadPageEmailRecord(raw);
  const effectiveEmail = raw.email || primaryPageEmail?.email || "";
  const promotedEmailSources = primaryPageEmail ? [{
    email: primaryPageEmail.email,
    sources: (primaryPageEmail.sources || []).map((source) => ({
      ...source,
      name: "线索主页来源",
      sourceKind: "lead_profile",
      verified: true
    }))
  }] : [];
  const website = raw.website || raw.reason || `${raw.company || "Unknown"} ${raw.type || ""}`;
  const fallbackEvaluation = evaluateLeadScore(
    `${raw.company} ${raw.type} ${raw.country} ${website}`,
    {
      model: raw.model,
      email: effectiveEmail,
      phone: raw.phone,
      whatsapp: raw.whatsapp,
      hasContact: Boolean(effectiveEmail || raw.phone || raw.whatsapp),
      hasOfficialWebsite: Boolean(raw.customerWebsite),
      contactName: raw.contactName,
      contactRole: raw.contactRole,
      countryMatch: Boolean(
        raw.aiReview?.targetCountryMatch
        || Number(raw.scoreDimensions?.countryFit || 0) > 0
        || hasLeadCountryEvidence(raw)
      )
    }
  );
  const scoreModelVersion = Number(raw.scoreModelVersion || 0);
  const baseScore = scoreModelVersion >= 11
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
        automotiveFit: "汽车业务匹配",
        countryFit: "目标地区匹配",
        chineseNev: "中国新能源相关",
        huaweiFit: "华为系列相关",
        contactCompleteness: "联系方式完整",
        websiteTrust: "官网可信度",
        tradeQualification: "进口分销能力",
        businessCapacity: "经营活跃度",
        decisionMaker: "决策人信息",
        purchaseIntent: "采购合作意向",
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
    email: effectiveEmail,
    emailSources: Array.isArray(raw.emailSources) && raw.emailSources.length
      ? raw.emailSources
      : promotedEmailSources.length
        ? promotedEmailSources
        : effectiveEmail
          ? [{
              email: effectiveEmail,
              sources: raw.sourceUrl || raw.source
                ? [{ url: raw.sourceUrl || raw.source, name: raw.origin || "原始来源" }]
                : []
            }]
          : [],
    unverifiedEmailCandidates: Array.isArray(raw.unverifiedEmailCandidates)
      ? raw.unverifiedEmailCandidates.filter((record) => String(record?.email || "").toLowerCase() !== effectiveEmail.toLowerCase())
      : [],
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
    isManualLead: Boolean(raw.isManualLead),
    isManualEntryOnly: Boolean(raw.isManualEntryOnly),
    isImportedLead: Boolean(raw.isImportedLead),
    isWebsiteLead,
    websiteLeadId: raw.websiteLeadId || "",
    skipInformationVerification: Boolean(raw.skipInformationVerification || isWebsiteLead),
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
    aiReview: raw.aiReview && typeof raw.aiReview === "object" ? { ...raw.aiReview } : {},
    autoImportEligible: raw.autoImportEligible !== false,
    rejectReason: raw.rejectReason || "",
    rejectedAt: raw.rejectedAt || "",
    reviewNotes: raw.reviewNotes || "",
    attachments: Array.isArray(raw.attachments) ? raw.attachments : [],
    sourceTranslation: raw.sourceTranslation || "",
    googleRating: Number(raw.googleRating || 0),
    googleReviews: Number(raw.googleReviews || 0),
    businessStatus: raw.businessStatus || "",
    baseScore,
    scoreModelVersion: scoreModelVersion >= 11 ? scoreModelVersion : 11,
    manualScoreAdjustment,
    scoreTier,
    scoreDimensions: scoreModelVersion >= 11 && raw.scoreDimensions
      ? raw.scoreDimensions
      : fallbackEvaluation.dimensions,
    scoreBreakdown: scoreModelVersion >= 11 && Array.isArray(raw.scoreBreakdown) && raw.scoreBreakdown.length
      ? raw.scoreBreakdown
      : fallbackBreakdown,
    scoreBasis: scoreModelVersion >= 11 && raw.scoreBasis
      ? raw.scoreBasis
      : "100分线索模型：汽车业务20、地区匹配20、联系方式15、官网10、中国新能源10、华为系列10、进口分销8、经营活跃4、决策人3，另计风险扣分",
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

function rejectLead(index, reason = "") {
  const lead = reviewLeads.splice(index, 1)[0];
  if (!lead) return;
  rejectedLeads.unshift({
    ...lead,
    stage: "已拒绝",
    rejectReason: reason || lead.rejectReason || "未填写原因",
    rejectedAt: new Date().toISOString()
  });
  rejectingReviewLeadId = "";
  refreshAllLeadViews();
}

function restoreRejectedLead(index) {
  const lead = rejectedLeads.splice(index, 1)[0];
  if (!lead) return;
  const restored = normalizeLead({
    ...lead,
    stage: "待审核",
    rejectReason: "",
    rejectedAt: "",
    restoredAt: new Date().toISOString()
  });
  reviewLeads.unshift(restored);
  selectedReviewLeadId = `pending:${restored.id || 0}`;
  reviewSelectedIds = new Set();
  $("#reviewStatusFilter") && ($("#reviewStatusFilter").value = "pending");
  refreshAllLeadViews();
}

async function researchLead(index, options = {}) {
  const lead = reviewLeads[index];
  if (!lead || lead.researching || leadSkipsAiAndVerification(lead)) return;
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
    .filter(({ lead }) => !lead.researchAt && !leadSkipsAiAndVerification(lead));
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

function uniqueKeywords(words) {
  const seen = new Set();
  return words
    .map((word) => String(word || "").replace(/\s+/g, " ").trim())
    .filter((word) => {
      if (!word) return false;
      const key = word.toLowerCase();
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
}

function countrySearchName(country) {
  const text = String(country || "UAE");
  if (/China|中国/i.test(text)) return "China";
  return countryKey(text);
}

function countrySearchCities(country, options = {}) {
  if (/China|中国/i.test(String(country || ""))) {
    const region = selectedDomesticRegion(options.domesticRegion || "");
    const fromRegion = (region.cities || domesticRegions[1].cities).split("/").map((city) => city.trim()).filter(Boolean);
    return uniqueKeywords(fromRegion).slice(0, region.value === "全国" ? 7 : 6);
  }
  const key = countrySearchName(country);
  const configured = countries.find((item) => countryKey(item.name) === key)?.cities || "";
  const fallback = {
    UAE: ["Dubai", "Abu Dhabi", "Sharjah"],
    "Saudi Arabia": ["Riyadh", "Jeddah", "Dammam"],
    Kazakhstan: ["Almaty", "Astana"],
    Russia: ["Moscow", "St. Petersburg"],
    Qatar: ["Doha"],
    Kuwait: ["Kuwait City", "Shuwaikh", "Hawalli"],
    Uzbekistan: ["Tashkent"],
    Azerbaijan: ["Baku"],
    Bahrain: ["Manama", "Riffa", "Muharraq"],
    Jordan: ["Amman", "Zarqa", "Irbid"],
    Georgia: ["Tbilisi", "Batumi", "Rustavi"],
    Vietnam: ["Ho Chi Minh City", "Hanoi", "Da Nang"],
    Philippines: ["Metro Manila", "Cebu", "Davao"],
    Mexico: ["Mexico City", "Monterrey", "Guadalajara"],
    Brazil: ["São Paulo", "Rio de Janeiro", "Brasília"],
    Chile: ["Santiago", "Valparaíso", "Concepción"],
    Colombia: ["Bogotá", "Medellín", "Cali"],
    Morocco: ["Casablanca", "Rabat", "Tangier"]
  }[key] || [key];
  const fromConfig = configured.split("/").map((city) => city.trim()).filter(Boolean);
  return uniqueKeywords([...fromConfig, ...fallback]).slice(0, 4);
}

function domesticSearchTerms(goal) {
  const text = String(goal || "");
  if (/租赁|出租|车队|fleet|rental|chauffeur/i.test(text)) return ["汽车租赁公司", "企业车队采购", "商务接待车队", "新能源车队"];
  if (/政府|项目|招标|government|tender/i.test(text)) return ["公务车采购", "政府用车项目", "新能源汽车采购", "招标"];
  if (/企业|采购|公司用车|corporate|procurement/i.test(text)) return ["企业用车采购", "公司车辆采购", "商务车队", "批量采购"];
  if (/平行进口|进口|外贸|出口|import|parallel/i.test(text)) return ["汽车外贸公司", "新能源汽车出口", "平行进口车商", "汽车贸易公司"];
  return ["汽车经销商", "新能源车商", "多品牌展厅", "汽车贸易公司"];
}

function intentSearchTerms(goal) {
  const text = String(goal || "");
  if (/租赁|出租|车队|fleet|rental|chauffeur/i.test(text)) return ["car rental company", "fleet operator", "chauffeur fleet", "fleet procurement"];
  if (/政府|项目|招标|government|tender/i.test(text)) return ["government vehicle tender", "public fleet procurement", "official vehicle project"];
  if (/企业|采购|公司用车|corporate|procurement/i.test(text)) return ["corporate fleet procurement", "company vehicle buyer", "business car tender"];
  if (/求购|正在买|询价|报价|RFQ|wanted|rfq/i.test(text)) return ["vehicle buying request", "car RFQ", "wanted electric SUV", "bulk order"];
  if (/平行进口|进口|外贸|import|parallel/i.test(text)) return ["parallel import cars", "vehicle importer", "auto trading", "import export"];
  if (/豪华|高端|展厅|showroom|luxury|premium/i.test(text)) return ["luxury car showroom", "premium car dealer", "high-end auto dealer"];
  return ["automotive importer", "car dealer showroom", "vehicle distributor"];
}

function modelSearchTerms(model) {
  const modelName = productProfiles[model]?.english || model;
  const lower = String(modelName).toLowerCase();
  const categoryTerms = /s800|s9/.test(lower)
    ? ["luxury executive sedan", "premium EV sedan"]
    : /r7/.test(lower)
      ? ["electric coupe SUV", "smart EV showroom"]
      : ["luxury SUV", "premium electric SUV", "Chinese EV SUV"];
  return [modelName, ...categoryTerms];
}

function generateSmartKeywords(goal, country, model, options = {}) {
  const countryName = countrySearchName(country);
  const cities = countrySearchCities(country, options);
  const primaryCity = String(options.cityFocus || "").trim() || cities[0] || countryName;
  const modelTerms = modelSearchTerms(model);
  const modelName = modelTerms[0];
  const intentTerms = intentSearchTerms(goal);
  const depth = String(options.searchDepth || "standard");
  if (countryName === "China") {
    const region = selectedDomesticRegion(options.domesticRegion || "");
    const domesticRegion = region.value && region.value !== "全国" ? region.value : "中国";
    const domesticTerms = domesticSearchTerms(goal);
    const sourceSites = [
      "site:baidu.com",
      "site:map.baidu.com",
      "site:amap.com",
      "site:qcc.com",
      "site:tianyancha.com",
      "site:aiqicha.baidu.com",
      "site:1688.com",
      "site:dealer.autohome.com.cn",
      "site:dealer.yiche.com",
      "site:dongchedi.com"
    ];
    const core = [
      `${domesticRegion} 汽车经销商 新能源 联系方式`,
      `${domesticRegion} 华为系 汽车 经销商 联系人`,
      `${domesticRegion} 鸿蒙智行 问界 尊界 经销商`,
      `${domesticRegion} 中国新能源 汽车贸易公司 电话 邮箱`,
      `${domesticRegion} 汽车外贸公司 新能源车 出口 联系方式`,
      `${domesticRegion} 多品牌汽车展厅 新能源 SUV`,
      `${domesticRegion} 企业车队 新能源汽车 采购`
    ];
    const cityTerms = cities.flatMap((city) => [
      `${city} 汽车经销商 新能源 联系方式`,
      `${city} 华为系 问界 尊界 汽车贸易`,
      `${city} 汽车外贸公司 新能源车 出口`
    ]);
    const intentQueries = domesticTerms.flatMap((term) => [
      `${primaryCity} ${term} 联系人 电话`,
      `${domesticRegion} ${term} 官网`
    ]);
    const sourceQueries = sourceSites.flatMap((site) =>
      domesticTerms.slice(0, 2).map((term) => `${site} ${primaryCity} ${term} 联系方式`)
    );
    const deepQueries = depth === "deep" ? [
      `${domesticRegion} 汽车集团 新能源 经销商 邮箱`,
      `${domesticRegion} 二网车商 新能源车 联系电话`,
      `${primaryCity} 高端汽车展厅 华为系 新能源`,
      `${domesticRegion} 汽车供应链 外贸 新能源车 出口`,
      `${primaryCity} 企业采购 新能源 SUV 车队`
    ] : [];
    return uniqueKeywords([...core, ...cityTerms, ...intentQueries, ...sourceQueries, ...deepQueries]).slice(0, depth === "deep" ? 28 : 18);
  }
  const core = [
    `${primaryCity} automotive importer vehicle distributor`,
    `${primaryCity} car dealer showroom auto trading`,
    `${countryName} parallel import car dealer`,
    `${countryName} vehicle procurement RFQ fleet purchase`,
    `${countryName} new brand dealership distribution opportunity`,
    `${countryName} Chinese EV importer distributor`
  ];
  const cityTerms = cities.flatMap((city) => [
    `${city} car dealer`,
    `${city} auto showroom`,
    `${city} vehicle importer`
  ]);
  const intentQueries = intentTerms.flatMap((term) => [
    `${primaryCity} ${term}`,
    `${countryName} ${term}`
  ]);
  const modelQueries = modelTerms.flatMap((term) => [
    `${term} dealer ${countryName}`,
    `${term} importer ${primaryCity}`,
    `${modelName} market fit ${primaryCity}`
  ]);
  const deepQueries = depth === "deep" ? [
    `${countryName} authorized car distributor`,
    `${primaryCity} multi brand car showroom`,
    `${countryName} luxury SUV importer`,
    `${primaryCity} Chinese electric vehicle dealer`,
    `${countryName} automotive group contact email`,
    `${primaryCity} car showroom WhatsApp`
  ] : [];
  return uniqueKeywords([...core, ...cityTerms, ...intentQueries, ...modelQueries, ...deepQueries]).slice(0, depth === "deep" ? 24 : 14);
}

function generateKeywords(goal, country, model, options = {}) {
  return generateSmartKeywords(goal, country, model, options);
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

function normalizeFinderPayload(raw = {}, form = $("#finderForm")) {
  const market = selectedFinderMarket(form);
  const model = String(raw.model || DEFAULT_FINDER_MODEL).trim() || DEFAULT_FINDER_MODEL;
  return {
    ...raw,
    country: market.country,
    marketLabel: market.label,
    domesticRegion: market.domesticRegion,
    model,
    sourceMode: market.isDomestic ? "combined" : (raw.sourceMode || "combined"),
    cityFocus: raw.cityFocus || "",
  };
}

function updateFinderKeywordsFromForm() {
  const form = $("#finderForm");
  if (!form || !$("#keywords")) return [];
  const data = normalizeFinderPayload(Object.fromEntries(new FormData(form).entries()), form);
  const words = generateKeywords(data.goal, data.country, data.model, {
    searchDepth: data.searchDepth,
    domesticRegion: data.domesticRegion
  });
  renderKeywords(words);
  return words;
}

function updateSocialProspectingQueries() {
  const form = $("#finderForm");
  if (!form || !$("#socialSearchQuery")) return;
  const market = selectedFinderMarket(form);
  const place = (market.cities || market.country).split(" / ")[0];
  const countryName = market.isDomestic ? "China" : String(form.country.value || "UAE").split(" ")[0];
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
  const extraLinks = $("#extraSocialSearchLinks");
  if (extraLinks) extraLinks.innerHTML = "";
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
  if (market.isDomestic) {
    facebookQueries = [
      `${place} 汽车经销商`,
      `${place} 新能源车商`,
      `${place} 华为系 汽车`,
      `${market.domesticRegion} 汽车贸易公司`
    ];
    instagramTags = [`${place}汽车`, `${place}新能源车`, `华为系汽车`, `汽车贸易`];
    businessTerms = ["汽车经销商", "新能源车商", "汽车贸易公司", "华为系汽车"];
    roleTerms = ["总经理", "采购负责人", "销售总监", "外贸经理"];
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

function salesCountryKey(value = "") {
  const text = String(value || "").trim();
  if (!text) return "";
  const known = Object.keys(salesCountryCoordinates).find((country) =>
    text.toLowerCase() === country.toLowerCase()
    || text.toLowerCase().startsWith(`${country.toLowerCase()} `)
    || text.toLowerCase().includes(country.toLowerCase())
  );
  return known || text.split(/\s+/)[0];
}

function salesCountryLabel(country) {
  return countries.find((item) => salesCountryKey(item.name) === country)?.name || country;
}

function salesRecordDate(record = {}) {
  return record.updatedAt || record.lastContactAt || record.approvedAt || record.researchAt
    || record.importedAt || record.discoveredAt || record.createdAt || "";
}

function salesDateInRange(value, range) {
  if (range === "all") return true;
  const date = new Date(value || "");
  return !Number.isNaN(date.getTime()) && date.getTime() >= Date.now() - Number(range) * 86400000;
}

function salesSourceName(record = {}) {
  const text = [
    record.origin, record.platform, record.sourceMode, record.discoverySource,
    record.sourceType, record.source, record.sourceUrl
  ].filter(Boolean).join(" ").toLowerCase();
  if (text.includes("facebook")) return "Facebook";
  if (text.includes("instagram")) return "Instagram";
  if (text.includes("tiktok")) return "TikTok";
  if (text.includes("youtube")) return "YouTube";
  if (text.includes("linkedin")) return "LinkedIn";
  if (text.includes("google") || text.includes("maps")) return "Google Maps";
  if (text.includes("openstreetmap") || text.includes("osm")) return "OpenStreetMap";
  return "官网 / 目录";
}

function emptySalesCountry(country) {
  return {
    country, leads: 0, pending: 0, customers: 0, contactable: 0, quoted: 0,
    completed: 0, quoteAmount: 0, overdue: 0, missingContact: 0,
    sources: {}, models: {}, owners: {}, latestActivity: ""
  };
}

function addSalesCount(target, key, value = 1) {
  if (key) target[key] = Number(target[key] || 0) + Number(value || 0);
}

function localSalesCountryAggregates(range = "all") {
  const aggregates = {};
  const ensure = (country) => aggregates[country] || (aggregates[country] = emptySalesCountry(country));
  const customerCountryById = new Map();
  const customerCountryByName = new Map();
  const today = new Date().toISOString().slice(0, 10);
  [
    ...reviewLeads.map((lead) => ({ lead, pending: true })),
    ...customers.map((lead) => ({ lead, pending: false }))
  ].forEach(({ lead, pending }) => {
    if (!salesDateInRange(salesRecordDate(lead), range)) return;
    const country = salesCountryKey(lead.country);
    if (!country) return;
    const item = ensure(country);
    item.leads += 1;
    item.pending += pending ? 1 : 0;
    item.customers += pending ? 0 : 1;
    item.contactable += lead.email || lead.phone || lead.whatsapp ? 1 : 0;
    item.missingContact += lead.email || lead.phone || lead.whatsapp ? 0 : 1;
    item.completed += lead.stage === "已成交" ? 1 : 0;
    item.overdue += !pending && !["已成交", "已流失"].includes(lead.stage)
      && lead.nextFollowAt && lead.nextFollowAt < today ? 1 : 0;
    addSalesCount(item.sources, salesSourceName(lead));
    (lead.recommendedModels || [lead.model]).filter(Boolean).slice(0, 4)
      .forEach((model) => addSalesCount(item.models, model));
    addSalesCount(item.owners, currentSession?.username || "当前账号");
    const activity = salesRecordDate(lead);
    if (activity > item.latestActivity) item.latestActivity = activity;
    if (!pending) {
      if (lead.id) customerCountryById.set(String(lead.id), country);
      if (lead.company) customerCountryByName.set(String(lead.company).toLowerCase(), country);
    }
  });
  quoteHistory.forEach((quote) => {
    if (!salesDateInRange(salesRecordDate(quote), range)) return;
    const country = salesCountryKey(quote.country)
      || customerCountryById.get(String(quote.customerId || ""))
      || customerCountryByName.get(String(quote.customer || "").toLowerCase())
      || Object.keys(salesCountryCoordinates).find((key) =>
        String(quote.destination || "").toLowerCase().includes(key.toLowerCase())
      );
    if (!country) return;
    const item = ensure(country);
    item.quoted += 1;
    item.quoteAmount += Number(quote.total || 0);
    if (quote.model) addSalesCount(item.models, quote.model);
    const activity = salesRecordDate(quote);
    if (activity > item.latestActivity) item.latestActivity = activity;
  });
  return aggregates;
}

function effectiveSalesCountryAggregates() {
  if (currentSession?.role === "admin" && adminKpiSnapshot?.countryAggregates) {
    return Object.fromEntries(Object.entries(adminKpiSnapshot.countryAggregates).map(([country, item]) => [
      country,
      { country, ...(item.periods?.[salesMapRange] || item.periods?.all || item) }
    ]));
  }
  return localSalesCountryAggregates(salesMapRange);
}

function formatOverviewMoney(value) {
  const amount = Number(value || 0);
  if (amount >= 1000000) return `$${(amount / 1000000).toFixed(1)}M`;
  if (amount >= 1000) return `$${Math.round(amount / 1000)}K`;
  return `$${Math.round(amount).toLocaleString("en-US")}`;
}

function sortedSalesEntries(values = {}) {
  return Object.entries(values || {}).sort((a, b) => Number(b[1]) - Number(a[1]));
}

function renderSalesCountryPanel(country, item) {
  const panel = $("#salesCountryPanel");
  if (!panel || !item) return;
  const sources = sortedSalesEntries(item.sources).slice(0, 6);
  const sourceMax = Math.max(1, ...sources.map((entry) => Number(entry[1] || 0)));
  const models = sortedSalesEntries(item.models).slice(0, 5);
  const owners = sortedSalesEntries(item.owners).slice(0, 5);
  panel.innerHTML = `
    <div class="country-panel-head">
      <span>当前市场</span>
      <h2>${escapeHtml(salesCountryLabel(country))}</h2>
      <p>最近活动：${escapeHtml(formatSyncTime(item.latestActivity))}</p>
    </div>
    <div class="country-stat-grid">
      <div><span>全部线索</span><strong>${Number(item.leads || 0)}</strong></div>
      <div><span>可联系</span><strong>${Number(item.contactable || 0)}</strong></div>
      <div><span>已报价</span><strong>${Number(item.quoted || 0)}</strong></div>
      <div><span>已成交</span><strong>${Number(item.completed || 0)}</strong></div>
    </div>
    <div class="country-detail-block">
      <h3>线索来源</h3>
      ${sources.length ? sources.map(([source, count]) => `
        <div class="country-source-row"><span>${escapeHtml(source)}</span>
          <i style="width:${Math.max(8, Number(count) / sourceMax * 100)}%"></i><b>${Number(count)}</b>
        </div>`).join("") : "<p>暂无来源数据</p>"}
    </div>
    <div class="country-detail-block">
      <h3>推荐车型</h3>
      <div class="country-models">${models.length
        ? models.map(([model, count]) => `<span>${escapeHtml(model)} · ${Number(count)}</span>`).join("")
        : "<span>暂无车型数据</span>"}</div>
    </div>
    <div class="country-detail-block">
      <h3>负责销售</h3>
      <div class="country-owners">${owners.length
        ? owners.map(([owner, count]) => `<span>${escapeHtml(owner)} · ${Number(count)}</span>`).join("")
        : "<span>未分配</span>"}</div>
    </div>
    <div class="country-panel-actions">
      <button type="button" data-overview-action="review-country" data-country="${escapeHtml(country)}">查看该国线索</button>
      <button type="button" data-overview-action="discover-country" data-country="${escapeHtml(country)}">继续开发市场</button>
    </div>`;
}

function salesMarkerColor(item) {
  if (Number(item.completed || 0) > 0) return "#2e9b69";
  if (Number(item.quoted || 0) > 0) return "#d79a2b";
  return "#3c82c4";
}

function renderSalesMap(aggregates) {
  const container = $("#salesWorldMap");
  if (!container) return;
  const entries = Object.entries(aggregates)
    .filter(([country, item]) => salesCountryCoordinates[country] && Number(item[salesMapMetric] || 0) > 0)
    .sort((a, b) => Number(b[1][salesMapMetric] || 0) - Number(a[1][salesMapMetric] || 0));
  if (!window.L) {
    container.innerHTML = `<div class="sales-map-fallback">${entries.map(([country, item]) => `
      <button type="button" data-sales-country="${escapeHtml(country)}">
        <strong>${escapeHtml(salesCountryLabel(country))}</strong>
        <span>${Number(item[salesMapMetric] || 0)} 条</span>
      </button>`).join("") || "<p>当前没有可显示的国家数据。</p>"}</div>`;
    return;
  }
  if (!salesMap) {
    salesMap = L.map(container, { minZoom: 1, maxZoom: 6, zoomSnap: .25, worldCopyJump: true })
      .setView([24, 35], 2);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png", {
      maxZoom: 6,
      attribution: "&copy; OpenStreetMap &copy; CARTO"
    }).addTo(salesMap);
    salesMap.salesLayers = L.layerGroup().addTo(salesMap);
  }
  salesMap.salesLayers.clearLayers();
  entries.forEach(([country, item], index) => {
    const value = Number(item[salesMapMetric] || 0);
    const marker = L.circleMarker(salesCountryCoordinates[country], {
      radius: Math.min(25, 7 + Math.sqrt(value) * 1.8),
      color: "#fff",
      weight: 2,
      fillColor: salesMarkerColor(item),
      fillOpacity: .88
    }).addTo(salesMap.salesLayers);
    const labelLayout = {
      UAE: { direction: "right", offset: [20, 17] },
      Qatar: { direction: "left", offset: [-18, -17] },
      Kuwait: { direction: "top", offset: [0, -22] },
      Bahrain: { direction: "right", offset: [32, -12] },
      Oman: { direction: "bottom", offset: [20, 24] },
      Jordan: { direction: "left", offset: [-16, -10] },
      "Saudi Arabia": { direction: "right", offset: [25, 55] },
      Uzbekistan: { direction: "right", offset: [7, 0] },
      Azerbaijan: { direction: "left", offset: [-7, 0] }
    }[country] || {
      direction: index % 2 ? "right" : "top",
      offset: index % 2 ? [7, 0] : [0, -7]
    };
    marker.bindTooltip(`${salesCountryLabel(country)} · ${value}`, {
      permanent: true,
      direction: labelLayout.direction,
      className: "sales-map-label",
      offset: labelLayout.offset
    });
    marker.on("click", () => {
      selectedSalesCountry = country;
      renderSalesCountryPanel(country, item);
      salesMap.flyTo(salesCountryCoordinates[country], Math.max(2.25, salesMap.getZoom()), { duration: .45 });
    });
  });
  window.requestAnimationFrame(() => salesMap?.invalidateSize());
}

function renderSalesAlerts(aggregates) {
  const box = $("#salesAlertList");
  if (!box) return;
  const alerts = Object.entries(aggregates).flatMap(([country, item]) => {
    const rows = [];
    if (Number(item.overdue || 0)) rows.push({
      priority: Number(item.overdue),
      title: `${salesCountryLabel(country)} 有 ${Number(item.overdue)} 位客户逾期未跟进`,
      detail: "建议销售今天优先联系，避免线索失去时效。"
    });
    if (Number(item.missingContact || 0) >= 3) rows.push({
      priority: Number(item.missingContact),
      title: `${salesCountryLabel(country)} 有 ${Number(item.missingContact)} 条线索缺少联系方式`,
      detail: "建议在线索审核中补全邮箱、电话或 WhatsApp。"
    });
    if (Number(item.quoted || 0) > Number(item.completed || 0)) rows.push({
      priority: Number(item.quoted) - Number(item.completed),
      title: `${salesCountryLabel(country)} 有 ${Number(item.quoted) - Number(item.completed)} 个报价待推进`,
      detail: "检查客户反馈、付款条件和下一次跟进日期。"
    });
    return rows;
  }).sort((a, b) => b.priority - a.priority).slice(0, 3);
  box.innerHTML = alerts.length ? alerts.map((alert) => `
    <article class="sales-alert-item">
      <strong><b>!</b> ${escapeHtml(alert.title)}</strong>
      <span>${escapeHtml(alert.detail)}</span>
    </article>`).join("") : `
    <article class="sales-alert-item">
      <strong>当前没有紧急事项</strong>
      <span>系统未发现逾期跟进、联系方式缺失或未推进报价。</span>
    </article>`;
}

function renderSalesOverview() {
  if (!$("#salesWorldMap")) return;
  const aggregates = effectiveSalesCountryAggregates();
  const totals = Object.values(aggregates).reduce((sum, item) => ({
    leads: sum.leads + Number(item.leads || 0),
    contactable: sum.contactable + Number(item.contactable || 0),
    quoted: sum.quoted + Number(item.quoted || 0),
    completed: sum.completed + Number(item.completed || 0),
    quoteAmount: sum.quoteAmount + Number(item.quoteAmount || 0)
  }), { leads: 0, contactable: 0, quoted: 0, completed: 0, quoteAmount: 0 });
  $("#globalLeadCount").textContent = totals.leads.toLocaleString("zh-CN");
  $("#globalContactableCount").textContent = totals.contactable.toLocaleString("zh-CN");
  $("#globalQuotedCount").textContent = totals.quoted.toLocaleString("zh-CN");
  $("#globalCompletedCount").textContent = totals.completed.toLocaleString("zh-CN");
  $("#globalQuoteAmount").textContent = formatOverviewMoney(totals.quoteAmount);
  renderSalesMap(aggregates);
  renderSalesAlerts(aggregates);
  if (!selectedSalesCountry || !aggregates[selectedSalesCountry]) {
    selectedSalesCountry = Object.entries(aggregates)
      .sort((a, b) => Number(b[1].leads || 0) - Number(a[1].leads || 0))[0]?.[0] || "";
  }
  if (selectedSalesCountry && aggregates[selectedSalesCountry]) {
    renderSalesCountryPanel(selectedSalesCountry, aggregates[selectedSalesCountry]);
  }
}

function bindSalesOverview() {
  if (salesOverviewBound) return;
  salesOverviewBound = true;
  $("#overviewRange")?.addEventListener("change", (event) => {
    salesMapRange = event.currentTarget.value || "all";
    renderSalesOverview();
  });
  $(".map-metric-tabs")?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-map-metric]");
    if (!button) return;
    salesMapMetric = button.dataset.mapMetric || "leads";
    $$(".map-metric-tabs [data-map-metric]").forEach((item) =>
      item.classList.toggle("active", item === button)
    );
    renderSalesOverview();
  });
  $("#salesWorldMap")?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-sales-country]");
    if (!button) return;
    const aggregates = effectiveSalesCountryAggregates();
    selectedSalesCountry = button.dataset.salesCountry;
    renderSalesCountryPanel(selectedSalesCountry, aggregates[selectedSalesCountry]);
  });
  $("#salesCountryPanel")?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-overview-action]");
    if (!button) return;
    const country = button.dataset.country || "";
    if (button.dataset.overviewAction === "discover-country") {
      chooseMarket(salesCountryLabel(country));
      return;
    }
    showSection("review");
    renderReviewFilterOptions();
    const filter = $("#reviewCountryFilter");
    const option = [...(filter?.options || [])].find((item) => salesCountryKey(item.value) === country);
    if (filter && option) filter.value = option.value;
    renderReview();
  });
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

function userRoleLabel(role) {
  if (role === "admin") return "管理员";
  if (role === "operator") return "运营";
  return "销售";
}

function userRoleOptions(selectedRole = "user") {
  return [
    ["user", "销售"],
    ["operator", "运营"],
    ["admin", "管理员"]
  ].map(([value, label]) =>
    `<option value="${value}" ${value === selectedRole ? "selected" : ""}>${label}</option>`
  ).join("");
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
        <td><strong>${escapeHtml(user.username || "-")}</strong><br><small>${escapeHtml(userRoleLabel(user.role))}</small></td>
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
  renderSalesOverview();
}

function bindNavigation() {
  if (navigationBound) return;
  navigationBound = true;
  $$("[data-section]").forEach((button) => {
    button.addEventListener("click", () => showSection(button.dataset.section));
  });
  bindMobileNavigation();
}

const mobileSectionTitles = {
  overview: "全球销售总览",
  market: "市场选择",
  "lead-finder": "自动找客户",
  "lead-finder-v2": "自动找客户2.0",
  review: "线索审核",
  crm: "客户池 CRM",
  "website-leads": "独立站线索",
  email: "智能开发信",
  follow: "今日跟进",
  quote: "CIF 报价",
  risk: "售后与风险",
  kpi: "KPI 看板",
  "account-settings-page": "账号设置",
  "user-management": "用户管理",
  "system-settings": "系统设置"
};

function setMobileNavigation(open) {
  const isOpen = Boolean(open);
  document.body.classList.toggle("mobile-nav-open", isOpen);
  $("#appSidebar")?.classList.toggle("mobile-open", isOpen);
  const toggle = $("#mobileNavToggle");
  const backdrop = $("#mobileNavBackdrop");
  if (toggle) {
    toggle.setAttribute("aria-expanded", String(isOpen));
    toggle.setAttribute("aria-label", isOpen ? "关闭主菜单" : "打开主菜单");
  }
  if (backdrop) backdrop.hidden = !isOpen;
  if (!isOpen) {
    window.requestAnimationFrame(() => salesMap?.invalidateSize());
  }
}

function updateMobileSectionTitle(id) {
  const title = $("#mobileSectionTitle");
  if (title) title.textContent = mobileSectionTitles[id] || "海外销售工作台";
}

function bindMobileNavigation() {
  const toggle = $("#mobileNavToggle");
  if (!toggle || toggle.dataset.bound === "true") return;
  toggle.dataset.bound = "true";
  toggle.addEventListener("click", () => {
    setMobileNavigation(toggle.getAttribute("aria-expanded") !== "true");
  });
  $("#mobileNavBackdrop")?.addEventListener("click", () => setMobileNavigation(false));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setMobileNavigation(false);
  });
  window.addEventListener("resize", () => {
    if (window.innerWidth > 700) setMobileNavigation(false);
  });
}

function showSection(id) {
  if (id === "lead-finder-v2" && currentSession && currentSession.role !== "admin") {
    id = "overview";
  }
  $$(".section").forEach((section) => section.classList.toggle("active", section.id === id));
  $$(".nav button").forEach((button) => button.classList.toggle("active", button.dataset.section === id));
  $("#userManagementNav")?.classList.toggle("active", id === "user-management");
  $("#systemSettingsNav")?.classList.toggle("active", id === "system-settings");
  $("#accountSettingsToggle")?.classList.toggle("active", id === "account-settings-page");
  if (window.location.hash !== `#${id}`) {
    history.replaceState(null, "", `#${id}`);
  }
  updateMobileSectionTitle(id);
  setMobileNavigation(false);
  window.scrollTo({ top: 0, behavior: "smooth" });
  if (id === "overview") {
    window.requestAnimationFrame(() => {
      renderSalesOverview();
      salesMap?.invalidateSize();
    });
  }
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
  return Boolean(job?.scheduleId)
    || discoverySchedules.some((schedule) => schedule.lastJobId && schedule.lastJobId === job.id);
}

function isAllSalesSchedule(schedule) {
  return schedule?.payload?.scheduleMode === "all_sales";
}

function isFinderV2Job(job) {
  if (job?.distributionType === "scheduled_sales_delivery") return true;
  return discoverySchedules.some((schedule) =>
    isAllSalesSchedule(schedule)
    && String(schedule.id || "") === String(job?.scheduleId || "")
  );
}

function discoveryJobRawCount(job) {
  return Number(job?.result?.rawCount ?? job?.result?.count ?? job?.result?.leads?.length ?? 0);
}

function discoveryJobLinkedLeadCount(jobId) {
  const normalizedJobId = String(jobId || "");
  if (!normalizedJobId) return 0;
  return [...reviewLeads, ...customers, ...rejectedLeads]
    .filter((lead) => String(lead?.discoveryJobId || "") === normalizedJobId)
    .length;
}

function discoveryJobImportedCount(job) {
  const linkedCount = discoveryJobLinkedLeadCount(job?.id);
  const importedCount = job?.result?.importedCount;
  if (importedCount !== undefined && importedCount !== null && importedCount !== "") {
    return Math.max(Number(importedCount) || 0, linkedCount);
  }
  if (linkedCount) return linkedCount;
  return discoveryJobRawCount(job);
}

function discoveryJobSkippedCount(job) {
  const stored = job?.result?.skippedCount;
  if (stored !== undefined && stored !== null && stored !== "") {
    return Math.max(0, Number(stored) || 0);
  }
  return Math.max(0, discoveryJobRawCount(job) - discoveryJobImportedCount(job));
}

function discoveryJobSkipBreakdownText(job) {
  const skipped = job?.result?.skipBreakdown;
  if (!skipped || typeof skipped !== "object") return "";
  return [
    ["未达自动导入", skipped.ineligible],
    ["账号已有", skipped.existing],
    ["已拒绝", skipped.rejected],
    ["官网重复", skipped.duplicateWebsite]
  ].filter(([, count]) => Number(count) > 0)
    .map(([label, count]) => `${label} ${Number(count)}`)
    .join(" · ");
}

function discoveryJobResultText(job) {
  const count = discoveryJobRawCount(job);
  if (job.imported) {
    const importedCount = discoveryJobImportedCount(job);
    const skippedCount = discoveryJobSkippedCount(job);
    if (importedCount) {
      return skippedCount
        ? `发现 ${count} 条 · 导入 ${importedCount} 条 · 跳过 ${skippedCount} 条`
        : `已导入 ${importedCount} 条`;
    }
    if (count) return `发现 ${count} 条`;
    return "已导入 0 条";
  }
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
    .filter((schedule) => !isAllSalesSchedule(schedule) && !schedule.lastJobId)
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
  const jobCards = discoveryJobs
    .filter((job) => currentSession?.role !== "admin" || !isFinderV2Job(job))
    .map((job) => ({
    kind: job.distributionType === "admin_search_copy"
      ? "管理员搜索导入"
      : job.distributionType === "scheduled_sales_delivery"
        ? "系统定时获客"
      : isScheduledDiscoveryJob(job) ? "定时抓取" : "自动抓取",
    id: job.id || "",
    status: stateLabels[job.status] || job.status || "未知",
    state: job.status || "",
    time: job.createdAt || job.updatedAt,
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
    const importedCount = discoveryJobImportedCount(job);
    const canImport = job.status === "completed" && !job.imported && count > 0;
    const isAutoImporting = autoImportingDiscoveryJobs.has(job.id);
    const canRetry = ["failed", "canceled"].includes(job.status);
    const canCancel = ["queued", "running"].includes(job.status);
    const diagnostics = job.result?.diagnostics;
    const actionLabel = job.imported
      ? `已导入 ${importedCount} 条`
      : isAutoImporting
        ? `自动导入中`
      : canImport
        ? (job.manualImportOnly ? "手动导入" : "等待自动导入")
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
            <span>${escapeHtml(job.distributionType === "admin_search_copy" ? "管理员搜索导入" : discoverySourceLabel(job.sourceMode))}</span>
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
            ${actionAttribute} ${canRetry || canCancel || (canImport && !isAutoImporting) ? "" : "disabled"}>
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
  renderFinderProgressList();
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

function scheduleTimingLabel(schedule) {
  const runTime = String(schedule?.payload?.scheduleRunTime || "");
  return runTime && /^\d{2}:\d{2}$/.test(runTime)
    ? `每天 ${runTime}`
    : scheduleIntervalLabel(schedule?.intervalMinutes);
}

function groupAllSalesDiscoverySchedules(schedules = discoverySchedules) {
  const grouped = new Map();
  schedules
    .filter((schedule) => schedule.payload?.scheduleMode === "all_sales")
    .sort((left, right) => {
      const leftUsername = String(left.targetUsername || "未指定销售");
      const rightUsername = String(right.targetUsername || "未指定销售");
      const usernameOrder = leftUsername.localeCompare(rightUsername, "zh-CN", {
        numeric: true,
        sensitivity: "base"
      });
      if (usernameOrder) return usernameOrder;
      const countryOrder = String(left.country || "").localeCompare(String(right.country || ""), "zh-CN");
      if (countryOrder) return countryOrder;
      return String(left.sourceMode || "").localeCompare(String(right.sourceMode || ""), "zh-CN");
    })
    .forEach((schedule) => {
      const username = schedule.targetUsername || "未指定销售";
      if (!grouped.has(username)) grouped.set(username, []);
      grouped.get(username).push(schedule);
    });
  return Array.from(grouped.entries());
}

function scheduledJobMatchesStatsPeriod(job, period = "7d") {
  if (period === "all") return true;
  const timestamp = new Date(job.updatedAt || job.createdAt || "");
  if (Number.isNaN(timestamp.getTime())) return false;
  const now = new Date();
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  if (period === "today") return timestamp >= todayStart;
  if (period === "yesterday") {
    const yesterdayStart = new Date(todayStart);
    yesterdayStart.setDate(yesterdayStart.getDate() - 1);
    return timestamp >= yesterdayStart && timestamp < todayStart;
  }
  const days = period === "30d" ? 30 : 7;
  const rangeStart = new Date(todayStart);
  rangeStart.setDate(rangeStart.getDate() - (days - 1));
  return timestamp >= rangeStart;
}

function renderFinderV2Stats() {
  const period = $("#scheduleStatsPeriod")?.value || "7d";
  const jobs = scheduledDiscoveryJobs.filter((job) => scheduledJobMatchesStatsPeriod(job, period));
  const completed = jobs.filter((job) => job.status === "completed").length;
  const failed = jobs.filter((job) => ["failed", "canceled"].includes(job.status)).length;
  const terminal = completed + failed;
  const imported = jobs.reduce((total, job) => total + Number(
    job.result?.importedCount ?? job.result?.delivery?.importedCount ?? 0
  ), 0);
  const enabled = discoverySchedules.filter((schedule) =>
    schedule.payload?.scheduleMode === "all_sales" && schedule.enabled
  ).length;
  const values = {
    scheduleEnabledCount: enabled,
    scheduleJobCount: jobs.length,
    scheduleCompletedCount: completed,
    scheduleFailedCount: failed,
    scheduleImportedCount: imported,
    scheduleSuccessRate: terminal ? `${Math.round((completed / terminal) * 100)}%` : "0%"
  };
  Object.entries(values).forEach(([id, value]) => {
    const element = document.getElementById(id);
    if (element) element.textContent = String(value);
  });
}

function renderDiscoverySchedules() {
  const box = $("#scheduleList");
  const allSalesSchedules = discoverySchedules.filter((schedule) => schedule.payload?.scheduleMode === "all_sales");
  const groupedSchedules = groupAllSalesDiscoverySchedules(allSalesSchedules);
  const status = $("#scheduleStatus");
  const enabledCount = allSalesSchedules.filter((schedule) => schedule.enabled).length;
  const pageCount = Math.max(1, Math.ceil(groupedSchedules.length / DISCOVERY_SCHEDULE_GROUPS_PAGE_SIZE));
  discoverySchedulePage = Math.max(1, Math.min(discoverySchedulePage, pageCount));
  const pageStart = (discoverySchedulePage - 1) * DISCOVERY_SCHEDULE_GROUPS_PAGE_SIZE;
  const visibleGroups = groupedSchedules.slice(pageStart, pageStart + DISCOVERY_SCHEDULE_GROUPS_PAGE_SIZE);
  if (status) status.textContent = allSalesSchedules.length
    ? `${enabledCount} 个启用 / ${allSalesSchedules.length} 个计划`
    : "未设置计划";
  renderFinderV2Stats();
  const pageLabel = $("#schedulePageLabel");
  if (pageLabel) {
    const currentUsername = visibleGroups[0]?.[0] || "";
    pageLabel.textContent = currentUsername
      ? `${currentUsername} · ${discoverySchedulePage} / ${pageCount}`
      : `${discoverySchedulePage} / ${pageCount}`;
  }
  const prevPage = $("#schedulePrevPage");
  const nextPage = $("#scheduleNextPage");
  if (prevPage) prevPage.disabled = discoverySchedulePage <= 1;
  if (nextPage) nextPage.disabled = discoverySchedulePage >= pageCount;
  if (box) box.innerHTML = visibleGroups.length ? visibleGroups.map(([username, schedules]) => `
    <section class="schedule-sales-group">
      <header>
        <strong>${escapeHtml(username)}</strong>
        <div class="schedule-sales-group-actions">
          <span>${schedules.length} 个计划</span>
          <button class="ghost compact" type="button" data-bulk-schedule="pause" data-schedule-sales="${escapeHtml(username)}"${schedules.some((schedule) => schedule.enabled) ? "" : " disabled"}>全部暂停</button>
          <button class="primary compact" type="button" data-bulk-schedule="start" data-schedule-sales="${escapeHtml(username)}"${schedules.some((schedule) => !schedule.enabled) ? "" : " disabled"}>全部启动</button>
        </div>
      </header>
      <div class="schedule-grid">
        ${schedules.map((schedule) => `
          <article class="schedule-item">
            <div>
              <div class="schedule-title">
                <strong>${escapeHtml(schedule.country || "未指定市场")}</strong>
                <span class="${schedule.enabled ? "enabled" : "paused"}">${schedule.enabled ? "已启用" : "已暂停"}</span>
              </div>
              <p>${escapeHtml(discoverySourceLabel(schedule.sourceMode))} · ${escapeHtml(scheduleTimingLabel(schedule))}</p>
              <small>下次执行：${escapeHtml(formatJobTime(schedule.nextRunAt))}${schedule.lastRunAt ? ` · 上次执行：${escapeHtml(formatJobTime(schedule.lastRunAt))}` : ""}${schedule.lastJobStatus ? ` · 最近状态：${escapeHtml(discoveryJobStateLabels()[schedule.lastJobStatus] || schedule.lastJobStatus)}${schedule.lastImportedCount !== undefined ? `，导入 ${Number(schedule.lastImportedCount || 0)} 条` : ""}` : ""}</small>
            </div>
            <div class="schedule-actions">
              <button class="ghost compact" type="button" data-toggle-schedule="${escapeHtml(schedule.id)}">
                ${schedule.enabled ? "暂停" : "启用"}
              </button>
              <button class="danger-button compact" type="button" data-delete-schedule="${escapeHtml(schedule.id)}">删除</button>
            </div>
          </article>
        `).join("")}
      </div>
    </section>
  `).join("") : `<p class="empty">暂无后台抓取计划。请在上方设置国家、来源和频率后保存。</p>`;
  renderPersonalDiscoverySchedules();
  renderScheduledDiscoveryRuns();
  renderDiscoveryHistory();
}

function scheduledRunMatchesStatus(job, filter) {
  if (filter === "all") return true;
  if (filter === "running") return ["queued", "running"].includes(job.status);
  return job.status === filter;
}

function renderScheduledDiscoveryRuns() {
  const box = $("#scheduledRunList");
  if (!box) return;
  const statusFilter = $("#scheduledRunStatusFilter")?.value || "all";
  const salesFilter = $("#scheduledRunSalesFilter");
  const currentSales = salesFilter?.value || "all";
  const salesNames = Array.from(new Set(
    scheduledDiscoveryJobs
      .map((job) => job.targetUsername || job.ownerUsername)
      .filter(Boolean)
  )).sort((a, b) => a.localeCompare(b, "zh-CN"));
  if (salesFilter) {
    salesFilter.innerHTML = `<option value="all">全部销售</option>${salesNames
      .map((name) => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`)
      .join("")}`;
    salesFilter.value = salesNames.includes(currentSales) ? currentSales : "all";
  }
  const selectedSales = salesFilter?.value || "all";
  const filtered = scheduledDiscoveryJobs.filter((job) => {
    const username = job.targetUsername || job.ownerUsername || "";
    return scheduledRunMatchesStatus(job, statusFilter)
      && (selectedSales === "all" || username === selectedSales);
  });
  const pageCount = Math.max(1, Math.ceil(filtered.length / SCHEDULED_RUNS_PAGE_SIZE));
  scheduledRunPage = Math.max(1, Math.min(scheduledRunPage, pageCount));
  const start = (scheduledRunPage - 1) * SCHEDULED_RUNS_PAGE_SIZE;
  const visible = filtered.slice(start, start + SCHEDULED_RUNS_PAGE_SIZE);
  const stateLabels = discoveryJobStateLabels();
  const count = $("#scheduledRunCount");
  if (count) count.textContent = `${filtered.length} 条`;
  const pageLabel = $("#scheduledRunPageLabel");
  if (pageLabel) pageLabel.textContent = `${scheduledRunPage} / ${pageCount}`;
  const prev = $("#scheduledRunPrev");
  const next = $("#scheduledRunNext");
  if (prev) prev.disabled = scheduledRunPage <= 1;
  if (next) next.disabled = scheduledRunPage >= pageCount;
  box.innerHTML = visible.length ? visible.map((job) => {
    const username = job.targetUsername || job.ownerUsername || "未指定销售";
    const importedCount = Number(job.result?.importedCount || 0);
    const rawCount = discoveryJobRawCount(job);
    const resultText = ["queued", "running"].includes(job.status)
      ? `${Number(job.progress || 0)}% · ${job.message || "后台执行中"}`
      : job.status === "failed"
        ? job.error || job.message || "执行失败"
        : `发现 ${rawCount} 条 · 导入 ${importedCount} 条`;
    return `
      <article class="scheduled-run-item ${escapeHtml(job.status || "")}">
        <div class="scheduled-run-state">
          <span>${escapeHtml(stateLabels[job.status] || job.status || "未知")}</span>
          <small>${escapeHtml(formatJobTime(job.updatedAt || job.createdAt))}</small>
        </div>
        <div class="scheduled-run-main">
          <strong>${escapeHtml(job.country || "未指定国家")} · ${escapeHtml(discoverySourceLabel(job.sourceMode))}</strong>
          <p>${escapeHtml(resultText)}</p>
        </div>
        <div class="scheduled-run-owner">
          <span>接收销售</span>
          <strong>${escapeHtml(username)}</strong>
        </div>
      </article>
    `;
  }).join("") : `<p class="empty">当前筛选下没有 2.0 执行记录。</p>`;
}

function renderPersonalDiscoverySchedules() {
  const box = $("#personalScheduleList");
  if (!box) return;
  const schedules = discoverySchedules.filter((schedule) => schedule.payload?.scheduleMode !== "all_sales");
  const status = $("#personalScheduleStatus");
  const enabledCount = schedules.filter((schedule) => schedule.enabled).length;
  if (status) {
    status.textContent = schedules.length ? `${enabledCount} 个启用 / ${schedules.length} 个任务` : "未设置任务";
  }
  box.innerHTML = schedules.length ? schedules.map((schedule) => `
    <article class="schedule-item">
      <div>
        <div class="schedule-title">
          <strong>${escapeHtml(schedule.country || "未指定市场")} · ${escapeHtml(discoverySourceLabel(schedule.sourceMode))}</strong>
          <span class="${schedule.enabled ? "enabled" : "paused"}">${schedule.enabled ? "已启用" : "已暂停"}</span>
        </div>
        <p>${escapeHtml(scheduleTimingLabel(schedule))} · 结果进入当前账号搜索记录</p>
        <small>下次执行：${escapeHtml(formatJobTime(schedule.nextRunAt))}${schedule.lastRunAt ? ` · 上次执行：${escapeHtml(formatJobTime(schedule.lastRunAt))}` : ""}</small>
      </div>
      <div class="schedule-actions">
        <button class="ghost compact" type="button" data-toggle-schedule="${escapeHtml(schedule.id)}">${schedule.enabled ? "暂停" : "启用"}</button>
        <button class="danger-button compact" type="button" data-delete-schedule="${escapeHtml(schedule.id)}">删除</button>
      </div>
    </article>
  `).join("") : `<p class="empty">暂无个人定时任务。设置上方找客户条件后保存即可。</p>`;
}

function currentFinderSchedulePayload() {
  const form = $("#finderForm");
  const data = normalizeFinderPayload(Object.fromEntries(new FormData(form).entries()), form);
  const words = generateKeywords(data.goal, data.country, data.model, {
    searchDepth: data.searchDepth,
    domesticRegion: data.domesticRegion
  });
  return {
    ...data,
    scheduleMode: "personal",
    resultLimit: 90,
    keywords: words.join(" | ")
  };
}

function scheduledDiscoveryPayload(form) {
  const formData = Object.fromEntries(new FormData(form).entries());
  const country = String(formData.country || "").trim();
  const model = "华为系新能源汽车";
  const sourceMode = String(formData.sourceMode || "combined");
  const searchDepth = String(formData.searchDepth || "standard");
  const goal = String(formData.goal || "").trim() || finderGoalText(country, model);
  const words = generateKeywords(goal, country, model, { searchDepth });
  return {
    planName: String(formData.planName || "").trim() || `${country} · ${discoverySourceLabel(sourceMode)}`,
    targetUsername: String(formData.targetUsername || "").trim(),
    goal,
    country,
    domesticRegion: "",
    model,
    sourceMode,
    accountScope: String(formData.accountScope || "both"),
    freshness: String(formData.freshness || "all"),
    searchDepth,
    resultLimit: Math.max(10, Math.min(90, Number(formData.resultLimit || 90))),
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

async function loadScheduledDiscoveryJobs() {
  if (currentSession?.role !== "admin") {
    scheduledDiscoveryJobs = [];
    return scheduledDiscoveryJobs;
  }
  const response = await apiFetch("/api/discover/scheduled-jobs", { cache: "no-store" });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  scheduledDiscoveryJobs = Array.isArray(result.jobs) ? result.jobs : [];
  renderFinderV2Stats();
  renderScheduledDiscoveryRuns();
  return scheduledDiscoveryJobs;
}

async function saveAllSalesDiscoverySchedule(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const submitButton = form.querySelector('button[type="submit"]');
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = "正在创建计划";
  }
  try {
    const formData = Object.fromEntries(new FormData(form).entries());
    const response = await apiFetch("/api/discover/schedules", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "save_all_sales",
        targetUsername: String(formData.targetUsername || "").trim(),
        sourceMode: String(formData.sourceMode || "combined"),
        runTime: String(formData.runTime || "06:00"),
        intervalMinutes: 1440,
        enabled: true
      })
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    discoverySchedulePage = 1;
    await loadDiscoverySchedules();
    await loadScheduledDiscoveryJobs().catch(() => undefined);
    await loadDiscoveryJobs().catch(() => undefined);
    renderScheduleTargetOptions();
    const status = $("#scheduleStatus");
    if (status) {
      status.textContent = `已覆盖 ${Number(result.salesCount || 0)} 名销售 · ${Number(result.scheduleCount || 0)} 个地区任务`;
    }
  } catch (error) {
    const status = $("#scheduleStatus");
    if (status) status.textContent = `创建失败：${error.message}`;
  } finally {
    if (submitButton) {
      submitButton.disabled = !allSalesScheduleAssignments().length;
      submitButton.textContent = "创建定时获客计划";
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

async function loadDiscoveryJobs(options = {}) {
  const { autoImport = true } = options;
  const response = await apiFetch("/api/discover/jobs", { cache: "no-store" });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  discoveryJobs = (Array.isArray(result.jobs) ? result.jobs : [])
    .filter((job) => !hiddenDiscoveryJobIds.has(String(job?.id || "")));
  const restoredAiReviews = backfillAiReviewsFromDiscoveryJobs();
  if (restoredAiReviews) {
    renderReview();
    saveState();
  }
  renderDiscoveryJobs();
  renderReviewFilterOptions();
  const active = discoveryJobs.find((job) => ["queued", "running"].includes(job.status));
  if (active) {
    const progress = normalizedDiscoveryJobProgress(active);
    setFinderProgress({
      percent: progress.percent,
      stage: progress.stage,
      state: progress.state,
      title: "云端获客任务运行中",
      elapsed: discoveryJobElapsedText(active) || "后台持续运行",
      message: active.message || "任务仍在云端执行，可以关闭当前页面。"
    });
  } else {
    const progressBox = $("#finderStatus")?.closest(".insight-box");
    if (progressBox?.dataset.progressState === "running") {
      setFinderProgress({
        percent: 100,
        stage: "done",
        state: "error",
        title: "没有正在运行的云端任务",
        message: "服务器没有找到正在执行的获客任务；如果页面还显示运行中，请刷新后重新执行。"
      });
    }
  }
  if (autoImport) autoImportCompletedDiscoveryJobs();
  return discoveryJobs;
}

async function markDiscoveryImported(jobId, counts = {}) {
  if (!jobId) return;
  await apiFetch("/api/discover/mark-imported", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      id: jobId,
      importedCount: counts.importedCount,
      rawCount: counts.rawCount,
      skippedCount: counts.skippedCount,
      skipBreakdown: counts.skipBreakdown
    })
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
    rememberHiddenDiscoveryJob(jobId);
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
  const prefix = job.distributionType === "admin_search_copy"
    ? "管理员搜索导入 · "
    : job.distributionType === "scheduled_sales_delivery"
      ? "系统定时获客 · "
      : "";
  return `${prefix}${job.country || "未指定市场"} · ${job.model || "未指定车型"} · ${formatJobTime(job.createdAt || job.updatedAt)}`;
}

async function setSalesDiscoverySchedulesEnabled(targetUsername, enabled) {
  const response = await apiFetch("/api/discover/schedules", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action: "bulk_set_enabled",
      targetUsername,
      enabled
    })
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  await loadDiscoverySchedules();
  const status = $("#scheduleStatus");
  if (status) status.textContent = `${targetUsername}：已${enabled ? "启动" : "暂停"} ${Number(result.updatedCount || 0)} 个计划`;
}

function backfillAiReviewsFromDiscoveryJobs() {
  const jobsById = new Map(discoveryJobs.map((job) => [String(job?.id || ""), job]));
  let restored = 0;
  [...reviewLeads, ...customers, ...rejectedLeads].forEach((lead) => {
    if (lead?.aiReview?.reason || !lead?.discoveryJobId) return;
    const job = jobsById.get(String(lead.discoveryJobId));
    const candidates = Array.isArray(job?.result?.leads) ? job.result.leads : [];
    const company = normalizedLeadIdentityText(lead.company);
    const companyMatches = candidates.filter((candidate) => (
      normalizedLeadIdentityText(candidate?.company) === company
      && candidate?.aiReview
      && typeof candidate.aiReview === "object"
      && Object.keys(candidate.aiReview).length
    ));
    if (!companyMatches.length) return;

    const leadUrls = new Set([
      lead.sourceUrl,
      lead.customerWebsite,
      lead.source
    ].map(canonicalLeadUrl).filter(Boolean));
    const matched = companyMatches.find((candidate) => [
      candidate?.sourceUrl,
      candidate?.customerWebsite,
      candidate?.source
    ].map(canonicalLeadUrl).filter(Boolean).some((url) => leadUrls.has(url)))
      || (companyMatches.length === 1 ? companyMatches[0] : null);
    if (!matched) return;
    lead.aiReview = { ...matched.aiReview };
    restored += 1;
  });
  return restored;
}

function mergeDiscoveryResult(result, sourceMode = "", job = null) {
  const found = Array.isArray(result?.leads) ? result.leads : [];
  const normalizedFound = found
    .map((lead) => normalizeLead({
      ...lead,
      sourceMode,
      discoverySource: sourceMode,
      discoveryJobId: job?.id || "",
      discoveryJobLabel: discoveryJobLabel(job),
      discoveryJobImportedAt: new Date().toISOString()
    }));
  forgetDeletedRecordsForLeads(normalizedFound);
  const existing = new Set(
    [...reviewLeads, ...customers].map((lead) => `${lead.company}|${lead.source}`.toLowerCase())
  );
  const rejectedFingerprintSet = new Set(
    rejectedLeads.flatMap((lead) => [...leadRejectionFingerprints(lead)])
  );
  const blockRejectedMemory = adminSettingsSnapshot?.controlCenter?.quality?.blockRejectedMemory !== false;
  const eligible = normalizedFound.filter((lead) => lead.autoImportEligible !== false);
  const nonExisting = eligible.filter((lead) => !existing.has(`${lead.company}|${lead.source}`.toLowerCase()));
  const notRejected = nonExisting.filter(
    (lead) => !blockRejectedMemory || !matchesRejectedLeadMemory(lead, rejectedFingerprintSet)
  );
  const fresh = limitDuplicateCustomerWebsites(notRejected, [...reviewLeads, ...customers, ...rejectedLeads]);
  if (fresh.length) {
    reviewLeads = [...fresh, ...reviewLeads];
    refreshAllLeadViews();
  }
  return {
    found,
    fresh,
    skipped: {
      ineligible: normalizedFound.length - eligible.length,
      existing: eligible.length - nonExisting.length,
      rejected: nonExisting.length - notRejected.length,
      duplicateWebsite: notRejected.length - fresh.length
    }
  };
}

async function savePersonalDiscoverySchedule(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const submitButton = form.querySelector('button[type="submit"]');
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = "正在保存";
  }
  try {
    const formData = Object.fromEntries(new FormData(form).entries());
    const response = await apiFetch("/api/discover/schedules", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "save_personal",
        payload: currentFinderSchedulePayload(),
        intervalMinutes: formData.intervalMinutes,
        startMode: formData.startMode,
        enabled: Boolean(formData.enabled)
      })
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    await loadDiscoverySchedules();
    const status = $("#personalScheduleStatus");
    if (status) status.textContent = "定时任务已保存";
  } catch (error) {
    const status = $("#personalScheduleStatus");
    if (status) status.textContent = `保存失败：${error.message}`;
  } finally {
    if (submitButton) {
      submitButton.disabled = discoveryDisabledForSession();
      submitButton.textContent = "保存定时任务";
    }
  }
}

function discoverySkippedMessage(merged) {
  const skipped = merged?.skipped || {};
  const reasons = [];
  if (skipped.ineligible) {
    reasons.push(`${skipped.ineligible} 条未达到自动入库规则（评分、国家或企业身份校验）`);
  }
  if (skipped.existing) reasons.push(`${skipped.existing} 条已在待审核或客户池`);
  if (skipped.rejected) reasons.push(`${skipped.rejected} 条命中已拒绝记录`);
  if (skipped.duplicateWebsite) reasons.push(`${skipped.duplicateWebsite} 条官网重复`);
  return reasons.length
    ? `${reasons.join("；")}，因此未自动导入。`
    : "本次结果没有可自动导入的新线索。";
}

function autoImportCompletedDiscoveryJobs() {
  const completed = discoveryJobs.filter((job) =>
    job?.id &&
    job.status === "completed" &&
    !job.manualImportOnly &&
    (
      !job.imported ||
      (
        job.imported &&
        discoveryJobRawCount(job) > 0 &&
        discoveryJobImportedCount(job) > 0 &&
        ![...reviewLeads, ...customers, ...rejectedLeads].some((lead) => String(lead.discoveryJobId || "") === String(job.id)) &&
        Date.now() - new Date(job.updatedAt || job.createdAt || Date.now()).getTime() < 48 * 60 * 60 * 1000
      )
    ) &&
    !autoImportingDiscoveryJobs.has(job.id)
  );
  completed.forEach((job) => {
    autoImportingDiscoveryJobs.add(job.id);
    importDiscoveryJob(job.id, { automatic: true }).finally(() => {
      autoImportingDiscoveryJobs.delete(job.id);
    });
  });
}

async function importDiscoveryJob(jobId, options = {}) {
  const { automatic = false } = options;
  const button = document.querySelector(`[data-import-job="${CSS.escape(jobId)}"]`);
  const finishButtonLoading = startButtonLoading(button, automatic ? "自动导入" : "正在导入");
  try {
    const response = await apiFetch(`/api/discover/status?${new URLSearchParams({ id: jobId })}`, {
      cache: "no-store"
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    const merged = mergeDiscoveryResult(result.job?.result || {}, result.job?.payload?.sourceMode || "", result.job);
    const importedCount = Math.max(merged.fresh.length, discoveryJobLinkedLeadCount(jobId));
    await markDiscoveryImported(jobId, {
      importedCount,
      rawCount: merged.found.length,
      skippedCount: Math.max(0, merged.found.length - importedCount),
      skipBreakdown: merged.skipped
    });
    setFinderProgress({
      percent: 100,
      stage: "done",
      state: "complete",
      title: `${automatic ? "搜索完成，已自动导入" : "已导入"} ${importedCount} 条线索`,
      message: importedCount
        ? "任务结果已进入线索审核，并已同步任务统计。"
        : discoverySkippedMessage(merged)
    });
    finishButtonLoading("已导入", { disabled: true });
    await loadDiscoveryJobs({ autoImport: false }).catch(() => undefined);
  } catch (error) {
    finishButtonLoading("导入失败", { disabled: false, autoResetMs: 1600 });
    setFinderProgress({
      percent: 100,
      stage: "done",
      state: "error",
      title: "任务结果导入失败",
      message: error.message
    });
    await loadDiscoveryJobs({ autoImport: false }).catch(() => undefined);
  }
}

async function runCloudDiscovery(data, words, onProgress) {
  const startResponse = await apiFetch("/api/discover/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      goal: data.goal,
      country: data.country,
      domesticRegion: data.domesticRegion,
      model: data.model,
      sourceMode: data.sourceMode,
      accountScope: data.accountScope,
      freshness: data.freshness,
      searchDepth: data.searchDepth,
      resultLimit: 90,
      keywords: words.join(" | ")
    })
  });
  const startResult = await startResponse.json().catch(() => ({}));
  if (!startResponse.ok || !startResult.ok || !startResult.job?.id) {
    throw new Error(startResult.error || `云端任务创建失败（HTTP ${startResponse.status}）`);
  }
  if (typeof onProgress === "function") {
    onProgress({
      ...startResult.job,
      message: startResult.job.reused
        ? "检测到相同搜索正在运行，已接入现有任务，未重复创建。"
        : (startResult.job.message || "云端获客任务已创建，正在等待执行。")
    });
  }

  const deadline = Date.now() + 8 * 60 * 1000;
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
      if (statusResponse.status === 404) {
        const missingError = new Error("云端任务记录不存在，可能是服务重启或任务已中断。请重新执行。");
        missingError.code = "JOB_MISSING";
        throw missingError;
      }
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
  const timeoutError = new Error("页面等待已超过 8 分钟，已停止等待。请缩小来源范围或重新执行。");
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
  $("#websiteLeadRows")?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-website-lead-action]");
    if (!button) return;
    const index = Number(button.dataset.index);
    if (button.dataset.websiteLeadAction === "import") importWebsiteLead(index);
    if (button.dataset.websiteLeadAction === "done") updateWebsiteLeadStatus(index, "done");
    if (button.dataset.websiteLeadAction === "delete") deleteWebsiteLead(index);
  });

  $("#finderHistoryPrev")?.addEventListener("click", () => {
    finderHistoryPage = Math.max(1, finderHistoryPage - 1);
    renderDiscoveryHistory();
  });

  $("#finderHistoryNext")?.addEventListener("click", () => {
    const historyCount = discoveryJobs.filter((job) =>
      currentSession?.role !== "admin" || !isFinderV2Job(job)
    ).length + discoverySchedules.filter((schedule) =>
      !isAllSalesSchedule(schedule) && !schedule.lastJobId
    ).length;
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
    const groupCount = groupAllSalesDiscoverySchedules().length;
    const pageCount = Math.max(1, Math.ceil(groupCount / DISCOVERY_SCHEDULE_GROUPS_PAGE_SIZE));
    discoverySchedulePage = Math.min(pageCount, discoverySchedulePage + 1);
    renderDiscoverySchedules();
  });

  $("#scheduledRunPrev")?.addEventListener("click", () => {
    scheduledRunPage = Math.max(1, scheduledRunPage - 1);
    renderScheduledDiscoveryRuns();
  });

  $("#scheduledRunNext")?.addEventListener("click", () => {
    scheduledRunPage += 1;
    renderScheduledDiscoveryRuns();
  });

  $("#scheduledRunStatusFilter")?.addEventListener("change", () => {
    scheduledRunPage = 1;
    renderScheduledDiscoveryRuns();
  });

  $("#scheduledRunSalesFilter")?.addEventListener("change", () => {
    scheduledRunPage = 1;
    renderScheduledDiscoveryRuns();
  });

  $("#refreshDiscoveryJobs")?.addEventListener("click", async (event) => {
    const button = event.currentTarget;
    const finishButtonLoading = startButtonLoading(button, "刷新中");
    await loadDiscoveryJobs().then(() => {
      finishButtonLoading("刷新成功", { autoResetMs: 1600 });
      setFinderStatus("刷新成功，任务列表已更新。");
    }).catch((error) => {
      finishButtonLoading("刷新失败", { autoResetMs: 1600 });
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

  $("#scheduleForm")?.addEventListener("submit", saveAllSalesDiscoverySchedule);
  $("#personalScheduleForm")?.addEventListener("submit", savePersonalDiscoverySchedule);
  $("#scheduleRunTime")?.addEventListener("input", updateAllSalesScheduleTimeLabel);
  $("#scheduleTargetUsername")?.addEventListener("change", renderScheduleTargetOptions);
  $("#showTodayScheduledLeads")?.addEventListener("click", () => {
    if ($("#reviewStatusFilter")) $("#reviewStatusFilter").value = "pending";
    if ($("#reviewTimeFilter")) $("#reviewTimeFilter").value = "today";
    renderReview();
  });

  $("#scheduleList")?.addEventListener("click", (event) => {
    const bulkButton = event.target.closest("[data-bulk-schedule]");
    if (bulkButton) {
      bulkButton.disabled = true;
      const enabled = bulkButton.dataset.bulkSchedule === "start";
      setSalesDiscoverySchedulesEnabled(bulkButton.dataset.scheduleSales, enabled).catch((error) => {
        const status = $("#scheduleStatus");
        if (status) status.textContent = `批量操作失败：${error.message}`;
        bulkButton.disabled = false;
      });
      return;
    }
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
    if (discoveryDisabledForSession()) {
      window.alert(`${discoveryDisabledReason()}。`);
      return;
    }
    const activeCount = activeDiscoveryJobs().length;
    if (activeCount >= MAX_ACTIVE_DISCOVERY_JOBS) {
      window.alert(`当前已有 ${activeCount} 个获客任务正在运行或排队，最多同时运行 ${MAX_ACTIVE_DISCOVERY_JOBS} 个。请等待其中一个完成后再启动新的任务。`);
      return;
    }
    const submitButton = event.currentTarget.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = "正在提交获客任务…";
    window.setTimeout(() => {
      submitButton.disabled = false;
      submitButton.textContent = "一键获客到待审核";
    }, 1500);
    discoveryJobPage = 1;
    finderHistoryPage = 1;
    const data = normalizeFinderPayload(Object.fromEntries(new FormData(event.currentTarget).entries()), event.currentTarget);
    const words = generateKeywords(data.goal, data.country, data.model, {
      searchDepth: data.searchDepth,
      domesticRegion: data.domesticRegion
    });
    renderKeywords(words);
    const searchProgress = startFinderSearchProgress();
    runCloudDiscovery(data, words, (job) => {
      searchProgress.stop();
      const progress = normalizedDiscoveryJobProgress(job);
      setFinderProgress({
        percent: progress.percent,
        stage: progress.stage,
        state: progress.state,
        title: job.reused ? "已接入已有获客任务" : "云端获客任务运行中",
        elapsed: discoveryJobElapsedText(job) || "后台持续运行",
        message: job.message || "云端正在检索公开商业来源，无需启动本地工作台。"
      });
      loadDiscoveryJobs().catch(() => undefined);
    })
      .then(async (result) => {
        const elapsedSeconds = searchProgress.stop();
        const merged = mergeDiscoveryResult(
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
        const { found, fresh } = merged;
        const importedCount = Math.max(fresh.length, discoveryJobLinkedLeadCount(result.__jobId));
        if (!found.length) {
          await markDiscoveryImported(result.__jobId, {
            importedCount: 0,
            rawCount: 0,
            skippedCount: 0,
            skipBreakdown: merged.skipped
          });
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
          message: `${sourceLabel} · ${freshnessLabel}：${importedCount} 条已进入审核，正在同步任务统计。`
        });
        if (!importedCount) {
          await markDiscoveryImported(result.__jobId, {
            importedCount: 0,
            rawCount: found.length,
            skippedCount: found.length,
            skipBreakdown: merged.skipped
          });
          setFinderProgress({
            percent: 100,
            stage: "done",
            state: "complete",
            title: "本轮搜索已完成",
            elapsed: `用时 ${elapsedSeconds} 秒`,
            message: `${sourceLabel} · ${freshnessLabel}：${discoverySkippedMessage(merged)}`
          });
          return;
        }
        await markDiscoveryImported(result.__jobId, {
          importedCount,
          rawCount: found.length,
          skippedCount: Math.max(0, found.length - importedCount),
          skipBreakdown: merged.skipped
        });
        setFinderProgress({
          percent: 100,
          stage: "done",
          state: "complete",
          title: `已导入 ${importedCount} 条待审核线索`,
          elapsed: `总用时 ${elapsedSeconds} 秒`,
          message: `${sourceLabel} · ${freshnessLabel}：线索已保存。请进入“线索审核”，按评分从高到低查看；需要更完整的邮箱、联系人和多来源证据时，再执行全网核验。`
        });
      })
      .catch((error) => {
        const elapsedSeconds = searchProgress.stop();
        const backgroundOnly = error.code === "JOB_STATUS_UNAVAILABLE";
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

  $("#finderForm").addEventListener("input", () => {
    updateFinderKeywordsFromForm();
    updateSocialProspectingQueries();
  });
  $("#finderForm").addEventListener("change", () => {
    updateFinderMarketControls();
    updateFinderKeywordsFromForm();
    updateSocialProspectingQueries();
  });
  $("#finderForm").country?.addEventListener("change", () => {
    if ($("#finderForm").domesticRegion) $("#finderForm").domesticRegion.value = "";
    syncFinderGoalToSelection();
  });
  $("#finderForm").domesticRegion?.addEventListener("change", (event) => {
    if (event.currentTarget.value) showDomesticDiscoveryNotice();
    syncFinderGoalToSelection();
  });
  $("#finderForm").model?.addEventListener("change", syncFinderGoalToSelection);
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
    const parsed = manualParsedLead && typeof manualParsedLead === "object" ? manualParsedLead : {};
    const isManualEntryOnly = !manualParsedLead;
    const customerWebsite = normalizeUserEnteredUrl(data.customerWebsite) || parsed.customerWebsite || "";
    const website = data.website || parsed.websiteContent || parsed.sourceExcerpt || `${data.company} ${data.type} ${data.country}`;
    const parsedScore = Number(parsed.score);
    const score = Number.isFinite(parsedScore)
      ? parsedScore
      : scoreLeadFromText(`${data.company} ${data.type} ${data.country} ${website}`);
    const lead = {
      ...parsed,
      company: data.company,
      country: data.country,
      city: data.city,
      type: data.type,
      source: data.source || "Website",
      origin: isManualEntryOnly ? "手动填写" : "手动解析",
      sourceType: parsed.sourceType || "手动添加线索",
      sourceTitle: parsed.sourceTitle || data.company,
      sourceUrl: parsed.sourceUrl || customerWebsite,
      customerWebsite,
      contactName: data.contactName || parsed.contactName || "",
      contactRole: data.contactRole || parsed.contactRole || "",
      email: data.email || parsed.email || "",
      phone: data.phone || parsed.phone || "",
      whatsapp: data.whatsapp || parsed.whatsapp || "",
      model: data.model,
      score,
      baseScore: score,
      stage: "准备联系",
      next: data.next || "发送首次开发信",
      website,
      isManualLead: true,
      isManualEntryOnly,
      manualApproval: true,
      manualApprovalAt: new Date().toISOString(),
      preferredChannel: data.whatsapp || parsed.whatsapp ? "WhatsApp" : "Email",
      aiReview: isManualEntryOnly ? {} : parsed.aiReview,
      researchAt: isManualEntryOnly ? "" : parsed.researchAt,
      researchSummary: isManualEntryOnly ? "" : parsed.researchSummary,
      confidence: isManualEntryOnly ? 0 : parsed.confidence,
      confidenceLabel: isManualEntryOnly ? "手动录入" : parsed.confidenceLabel,
      sourceCoverage: isManualEntryOnly ? {
        total: 0,
        official: 0,
        independentDomains: 0,
        contactable: Boolean(data.email || data.phone || data.whatsapp),
        missingFields: [],
        decision: "手动录入客户"
      } : parsed.sourceCoverage,
      sourceExcerpt: parsed.sourceExcerpt || website,
      reason: parsed.contactReason || `${data.city} 的${data.type}，公开信息显示：${website.slice(0, 90)}。适合推荐${data.model}。`
    };
    customers.unshift(normalizeLead(lead));
    event.currentTarget.reset();
    resetManualLeadParser();
    closeManualLeadModal();
    refreshAllLeadViews();
    showSection("crm");
  });

  $("#scheduleStatsPeriod")?.addEventListener("change", renderFinderV2Stats);

  $("#personalScheduleList")?.addEventListener("click", (event) => {
    const toggleButton = event.target.closest("[data-toggle-schedule]");
    const deleteButton = event.target.closest("[data-delete-schedule]");
    const button = toggleButton || deleteButton;
    if (!button) return;
    button.disabled = true;
    const operation = toggleButton
      ? toggleDiscoverySchedule(toggleButton.dataset.toggleSchedule)
      : deleteDiscoverySchedule(deleteButton.dataset.deleteSchedule);
    operation.catch((error) => {
      const status = $("#personalScheduleStatus");
      if (status) status.textContent = `操作失败：${error.message}`;
      button.disabled = false;
    });
  });

  $("#refreshDiscoverySchedules")?.addEventListener("click", async (event) => {
    const button = event.currentTarget;
    const finishButtonLoading = startButtonLoading(button, "刷新中");
    try {
      await Promise.all([
        loadDiscoverySchedules(),
        loadScheduledDiscoveryJobs(),
        loadDiscoveryJobs({ autoImport: false })
      ]);
      finishButtonLoading("刷新成功", { autoResetMs: 1600 });
      const status = $("#scheduleStatus");
      if (status) status.textContent = "刷新成功，计划和任务状态已更新";
    } catch (error) {
      finishButtonLoading("刷新失败", { autoResetMs: 1600 });
      const status = $("#scheduleStatus");
      if (status) status.textContent = `刷新失败：${error.message}`;
    }
  });

  $("#leadParserForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const button = form.querySelector('button[type="submit"]');
    const url = normalizeUserEnteredUrl(new FormData(form).get("url"));
    if (!url) {
      setLeadParserStatus("请输入有效的网址，例如 example.com。", "error");
      return;
    }
    form.elements.url.value = url;
    button.disabled = true;
    button.textContent = "正在解析...";
    setLeadParserStatus("正在读取公开页面并核验联系方式，请稍候。", "loading");
    try {
      const response = await apiFetch(`/api/parse-lead-source?${new URLSearchParams({ url })}`, { cache: "no-store" });
      const result = await response.json().catch(() => ({}));
      if (!response.ok || !result.ok) throw new Error(result.error || `解析失败（HTTP ${response.status}）`);
      applyParsedLeadToManualForm(result);
      renderLeadParserResult(result);
      setLeadParserStatus("解析完成，结果已填入右侧表单。", "success");
    } catch (error) {
      setLeadParserStatus(error.message || "解析失败，请检查网址后重试。", "error");
    } finally {
      button.disabled = false;
      button.textContent = "解析线索";
    }
  });

  $("#openManualLeadModal")?.addEventListener("click", openManualLeadModal);
  $("#manualLeadModal")?.addEventListener("click", (event) => {
    if (event.target === event.currentTarget || event.target.closest("[data-close-manual-lead]")) {
      closeManualLeadModal();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !$("#manualLeadModal")?.hidden) closeManualLeadModal();
  });

  $("#reviewGrid").addEventListener("click", (event) => {
    const row = event.target.closest("[data-review-lead-row]");
    if (row && !event.target.closest("input, button, a, summary, details")) {
      selectedReviewLeadId = row.dataset.reviewLeadRow;
      editingReviewLeadId = "";
      rejectingReviewLeadId = "";
      openReviewDetailKey = "";
      closeOpenReviewDetails();
      renderReview({ detailOnly: true });
      row.focus({ preventScroll: true });
      return;
    }
    const sectionButton = event.target.closest("[data-section]");
    if (sectionButton) {
      showSection(sectionButton.dataset.section);
      return;
    }
    const closeDetailsButton = event.target.closest("[data-close-review-details]");
    if (closeDetailsButton) {
      openReviewDetailKey = "";
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
      rejectingReviewLeadId = "";
      renderReview();
      return;
    }
    const cancelEditButton = event.target.closest("[data-review-edit-cancel]");
    if (cancelEditButton) {
      editingReviewLeadId = "";
      renderReview();
      return;
    }
    const cancelRejectButton = event.target.closest("[data-review-reject-cancel]");
    if (cancelRejectButton) {
      rejectingReviewLeadId = "";
      renderReview();
      return;
    }
    const confirmRejectButton = event.target.closest("[data-review-reject-confirm]");
    if (confirmRejectButton) {
      const panel = confirmRejectButton.closest("[data-reject-reason-panel]");
      const selected = panel?.querySelector("input[type='radio']:checked")?.value || "";
      const otherInput = panel?.querySelector("[data-reject-other]");
      const other = String(otherInput?.value || "").trim();
      const reason = selected === "__other" ? other : selected;
      if (!reason) {
        otherInput?.focus();
        return;
      }
      rejectLead(Number(confirmRejectButton.dataset.reviewRejectConfirm), reason);
      return;
    }
    const button = event.target.closest("[data-review-action]");
    if (!button) return;
    const index = Number(button.dataset.index);
    editingReviewLeadId = "";
    rejectingReviewLeadId = "";
    if (button.dataset.reviewAction === "approve") approveLead(index);
    if (button.dataset.reviewAction === "reject") {
      rejectingReviewLeadId = `pending:${reviewLeads[index]?.id || index}`;
      renderReview();
      requestAnimationFrame(() => {
        const panel = document.querySelector("[data-reject-reason-panel]");
        panel?.scrollIntoView({ behavior: "smooth", block: "center" });
        panel?.querySelector("input[type='radio']")?.focus({ preventScroll: true });
      });
    }
    if (button.dataset.reviewAction === "restore") restoreRejectedLead(index);
  });

  $("#reviewGrid").addEventListener("submit", async (event) => {
    const form = event.target.closest("[data-review-edit-form]");
    if (!form) return;
    event.preventDefault();
    await saveReviewLeadEdit(Number(form.dataset.index), form);
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
    const detailKey = details.dataset.reviewDetailKey || "";
    if (!details.open) {
      const content = details.querySelector("[data-review-detail-content]");
      if (detailKey && content) reviewDetailScrollPositions.set(detailKey, content.scrollTop);
      if (openReviewDetailKey === detailKey) openReviewDetailKey = "";
      clearReviewDetail(details);
      return;
    }
    openReviewDetailKey = detailKey;
    closeOpenReviewDetails(details);
    hydrateReviewDetail(details);
  }, true);

  $("#reviewGrid").addEventListener("scroll", (event) => {
    const content = event.target.closest?.("[data-review-detail-content]");
    const detailKey = content?.closest("details.review-more")?.dataset.reviewDetailKey || "";
    if (content && detailKey) reviewDetailScrollPositions.set(detailKey, content.scrollTop);
  }, true);

  ["#reviewStatusFilter", "#reviewDiscoveryFilter", "#reviewTimeFilter", "#reviewSourceFilter", "#reviewCountryFilter", "#reviewTierFilter"].forEach((selector) => {
    $(selector)?.addEventListener("change", renderReview);
  });
  $("#reviewSearchInput")?.addEventListener("input", () => {
    window.clearTimeout(reviewSearchRenderTimer);
    reviewSearchRenderTimer = window.setTimeout(() => {
      reviewSearchRenderTimer = 0;
      renderReview();
    }, 140);
  });

  $("#clearReviewFilters")?.addEventListener("click", () => {
    $("#reviewStatusFilter").value = "pending";
    $("#reviewDiscoveryFilter").value = "all";
    $("#reviewTimeFilter").value = "all";
    $("#reviewSourceFilter").value = "all";
    $("#reviewCountryFilter").value = "all";
    $("#reviewTierFilter").value = "all";
    if ($("#reviewSearchInput")) $("#reviewSearchInput").value = "";
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
        body: JSON.stringify({
          username: data.username,
          password: data.password,
          role: data.role || "user",
          assignedCountries: selectedUserCountryValues($("#userAssignedCountries"))
        })
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
      form.reset();
      renderUserCountryOptions();
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
    $("#userRows").innerHTML = `<tr><td colspan="8">${escapeHtml(error.message)}</td></tr>`;
  }));
  $("#previewDiscoveryDistribution")?.addEventListener("click", previewDiscoveryDistribution);
  $("#executeDiscoveryDistribution")?.addEventListener("click", executeDiscoveryDistribution);

  $("#cancelPasswordChange")?.addEventListener("click", resetAccountPasswordForm);
  $("#accountPasswordForm")?.addEventListener("submit", changeOwnPassword);

  $("#reloadAdminSettings")?.addEventListener("click", () => loadAdminSettings());
  $("#refreshApifyUsage")?.addEventListener("click", () => loadApifyUsage());
  $("#refreshApiConsumption")?.addEventListener("click", () => loadApiConsumption());
  $("#reloadAdminOperations")?.addEventListener("click", () => loadAdminOperations({ feedback: true }));
  $("#saveAdminSettingsTop")?.addEventListener("click", () => $("#adminSettingsForm")?.requestSubmit());
  $("#restartAdminServerButton")?.addEventListener("click", async () => {
    if (!confirm("确定重启工作台服务吗？页面会短暂断开。")) return;
    try { await restartAdminServer(); } catch (error) { setAdminSettingsStatus(error.message || "重启失败。", "error"); }
  });
  $("#adminSettingsTabs")?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-admin-tab]");
    if (!button) return;
    $("#adminSettingsTabs").querySelectorAll("[data-admin-tab]").forEach((item) => item.classList.toggle("active", item === button));
    document.querySelectorAll("[data-admin-panel]").forEach((panel) => { panel.hidden = panel.dataset.adminPanel !== button.dataset.adminTab; });
  });
  $("#toggleAdminApis")?.addEventListener("click", () => {
    adminApiShowAll = !adminApiShowAll;
    renderAdminSettings(adminSettingsSnapshot || {});
  });
  $("#clearAdminSettingsForm")?.addEventListener("click", () => {
    const form = $("#adminSettingsForm");
    if (!form) return;
    form.querySelectorAll("[data-admin-setting-key][type='password'], [data-custom-api-value][type='password']").forEach((input) => {
      input.value = "";
    });
    setAdminSettingsStatus("已清空输入，尚未保存。");
  });
  $("#addCustomApi")?.addEventListener("click", () => addCustomApiRow());
  $("#customApiList")?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-remove-custom-api]");
    if (button) button.closest("[data-custom-api-row]")?.remove();
  });
  $("#customApiList")?.addEventListener("change", (event) => {
    const selector = event.target.closest("[data-custom-api-type]");
    if (!selector) return;
    const row = selector.closest("[data-custom-api-row]");
    const valueInput = row?.querySelector("[data-custom-api-value]");
    if (valueInput) valueInput.type = selector.value === "text" ? "text" : "password";
  });
  $("#adminSettingsForm")?.addEventListener("submit", saveAdminSettings);
  $("#adminSettingsForm")?.addEventListener("click", async (event) => {
    const sourceTest = event.target.closest("[data-test-admin-source]")?.dataset.testAdminSource;
    if (sourceTest) {
      if (!confirm("连接测试可能产生一次供应商 API 调用，确定继续吗？")) return;
      try {
        event.target.disabled = true;
        setAdminSettingsStatus(`正在测试 ${discoverySourceLabel(sourceTest)}…`);
        const response = await apiFetch("/api/admin/operations", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action: "test-source", source: sourceTest })
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
        setAdminSettingsStatus(`${result.message}，耗时 ${result.elapsedMs || 0}ms。`, result.available ? "success" : "error");
        await loadAdminOperations();
      } catch (error) {
        setAdminSettingsStatus(error.message || "来源测试失败。", "error");
      } finally {
        event.target.disabled = false;
      }
      return;
    }
    const operation = event.target.closest("[data-admin-operation]")?.dataset.adminOperation;
    if (!operation) return;
    try {
      if (operation === "download-backup") await downloadAdminBackup();
      else if (operation === "restore-backup") $("#adminBackupFile")?.click();
      else await runAdminOperation(operation);
    } catch (error) {
      setAdminSettingsStatus(error.message || "操作失败。", "error");
    }
  });
  $("#adminBackupFile")?.addEventListener("change", async (event) => {
    try { await restoreAdminBackup(event.target.files?.[0]); }
    catch (error) { setAdminSettingsStatus(error.message || "备份恢复失败。", "error"); }
    finally { event.target.value = ""; }
  });
  $("#restoreQualityDefaults")?.addEventListener("click", () => {
    const defaults = { automotive: 20, country: 20, chineseNev: 10, huawei: 10, contact: 15, officialWebsite: 10, importDistribution: 8, businessActivity: 4, decisionMaker: 3 };
    Object.entries(defaults).forEach(([key, value]) => {
      const input = document.querySelector(`[data-control-path="quality.scoreWeights.${key}"]`);
      if (input) input.value = value;
    });
    setAdminSettingsStatus("评分权重已恢复默认，保存后生效。");
  });
  $("#adminCountrySourceEditor")?.addEventListener("change", (event) => {
    const control = adminSettingsSnapshot?.controlCenter;
    if (!control) return;
    control.discovery ||= {};
    control.discovery.countrySourceOverrides ||= {};
    const countrySelect = $("#adminCountrySourceSelect");
    if (event.target === countrySelect) {
      renderAdminCountrySources(control, countrySelect.value);
      return;
    }
    const country = countrySelect?.value;
    if (!country) return;
    if (event.target.id === "adminCountryUseGlobal") {
      if (event.target.checked) delete control.discovery.countrySourceOverrides[country];
      else control.discovery.countrySourceOverrides[country] = [...(control.discovery.globalSources || [])];
      renderAdminCountrySources(control, country);
      return;
    }
    if (event.target.matches("[data-country-source]")) {
      control.discovery.countrySourceOverrides[country] = Array.from(document.querySelectorAll("[data-country-source]:checked")).map((input) => input.dataset.countrySource);
    }
  });

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
      if (button.dataset.userAction === "activity") {
        await loadUserActivity(username);
      }
      if (button.dataset.userAction === "countries") {
        renderUserCountryEditor(username, (button.dataset.countries || "").split("|").filter(Boolean));
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

  $("#userRows")?.addEventListener("change", async (event) => {
    const selector = event.target.closest("[data-user-action='role-select']");
    if (!selector) return;
    const username = selector.dataset.username;
    const previousRole = selector.dataset.role || "user";
    const nextRole = selector.value || "user";
    if (nextRole === previousRole) return;
    if (!confirm(`确认将用户 ${username} 的角色改为${userRoleLabel(nextRole)}吗？`)) {
      selector.value = previousRole;
      return;
    }
    selector.disabled = true;
    try {
      await updateUser(username, { role: nextRole });
    } catch (error) {
      selector.value = previousRole;
      window.alert(error.message || "修改角色失败，请稍后重试。");
    } finally {
      selector.disabled = false;
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

  $("#userActivityPanel")?.addEventListener("click", (event) => {
    if (event.target.closest("[data-close-user-activity]")) {
      event.currentTarget.hidden = true;
      event.currentTarget.innerHTML = "";
    }
  });

  document.addEventListener("click", (event) => {
    const closeButton = event.target.closest("[data-close-user-region-modal]");
    if (closeButton || event.target.matches("[data-user-region-modal]")) {
      closeUserRegionModal();
      return;
    }
    const saveButton = event.target.closest("[data-save-user-countries]");
    if (!saveButton) return;
    const username = saveButton.dataset.username || "";
    const modal = saveButton.closest("[data-user-region-modal]");
    saveButton.disabled = true;
    updateUser(username, {
      assignedCountries: selectedUserCountryValues(modal?.querySelector("[data-user-country-editor]"))
    }).then(() => {
      closeUserRegionModal();
    }).catch((error) => {
      window.alert(error.message || "区域保存失败，请稍后重试。");
      saveButton.disabled = false;
    });
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

  $("#crmSearchInput")?.addEventListener("input", (event) => {
    crmSearchQuery = event.target.value || "";
    renderCrm();
  });

  $("#crmTierFilter")?.addEventListener("change", (event) => {
    crmTierFilter = event.target.value || "all";
    renderCrm();
  });

  $("#crmStageFilter")?.addEventListener("change", (event) => {
    crmStageFilter = event.target.value || "all";
    renderCrm();
  });

  $("#crmSortBy")?.addEventListener("change", (event) => {
    crmSortBy = event.target.value || "priority";
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
  $("#downloadCustomerImportTemplate")?.addEventListener("click", downloadCustomerImportTemplate);
  $("#importCustomersButton")?.addEventListener("click", () => {
    const input = $("#customerImportFile");
    if (!input) return;
    input.value = "";
    input.click();
  });
  $("#customerImportFile")?.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const button = $("#importCustomersButton");
    if (button) {
      button.disabled = true;
      button.textContent = "正在导入...";
    }
    setCustomerImportStatus("正在读取并校验客户数据...", "loading");
    try {
      const result = await importCustomersCsv(file);
      const message = `导入完成：新增 ${result.imported} 条，跳过重复 ${result.duplicates} 条，无效 ${result.invalid} 条。`;
      setCustomerImportStatus(message, result.imported ? "success" : "warning");
    } catch (error) {
      setCustomerImportStatus(error.message || "导入失败，请使用客户池模板重试。", "error");
    } finally {
      if (button) {
        button.disabled = false;
        button.textContent = "导入客户 CSV";
      }
      event.target.value = "";
    }
  });

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
  const systemSettingsNav = $("#systemSettingsNav");
  if (systemSettingsNav) systemSettingsNav.hidden = session.role !== "admin";
  const autoFinderV2Nav = $("#autoFinderV2Nav");
  if (autoFinderV2Nav) autoFinderV2Nav.hidden = session.role !== "admin";
  const autoFinderV2Section = $("#lead-finder-v2");
  if (autoFinderV2Section) autoFinderV2Section.hidden = session.role !== "admin";
  const userManagementSection = $("#user-management");
  if (userManagementSection) userManagementSection.hidden = session.role !== "admin";
  const systemSettingsSection = $("#system-settings");
  if (systemSettingsSection) systemSettingsSection.hidden = session.role !== "admin";
  const accountSettingsToggle = $("#accountSettingsToggle");
  if (accountSettingsToggle) accountSettingsToggle.hidden = session.role === "admin";
  const logoutButton = $("#logoutButton");
  if (logoutButton) logoutButton.hidden = false;
  const accountSettingsSection = $("#account-settings-page");
  if (accountSettingsSection) accountSettingsSection.hidden = session.role === "admin";
  const passwordForm = $("#accountPasswordForm");
  if (passwordForm) passwordForm.hidden = session.role === "admin";
  if (session.role === "admin" && window.location.hash === "#account-settings-page") {
    showSection("overview");
  }
  if (session.role !== "admin" && window.location.hash === "#lead-finder-v2") {
    showSection("overview");
  }
  return session;
}

function resetAccountPasswordForm() {
  const form = $("#accountPasswordForm");
  const status = $("#accountPasswordStatus");
  if (!form) return;
  form.reset();
  if (status) {
    status.className = "form-status";
    status.textContent = "";
  }
}

async function changeOwnPassword(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const status = $("#accountPasswordStatus");
  const submit = form.querySelector("button[type='submit']");
  const data = Object.fromEntries(new FormData(form).entries());
  if (status) {
    status.className = "form-status";
    status.textContent = "";
  }
  const newPassword = String(data.newPassword || "");
  const confirmPassword = String(data.confirmPassword || "");
  if (newPassword.length < 6) {
    if (status) {
      status.textContent = "新密码至少需要 6 位。";
      status.classList.add("error");
    }
    return;
  }
  if (newPassword !== confirmPassword) {
    if (status) {
      status.textContent = "两次输入的新密码不一致。";
      status.classList.add("error");
    }
    return;
  }
  if (submit) submit.disabled = true;
  try {
    const response = await apiFetch("/api/me/password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ currentPassword: data.currentPassword, newPassword })
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    form.reset();
    if (status) {
      status.textContent = "密码修改成功，下次登录请使用新密码。";
      status.classList.add("success");
    }
  } catch (error) {
    if (status) {
      status.textContent = error.message || "密码修改失败，请稍后重试。";
      status.classList.add("error");
    }
  } finally {
    if (submit) submit.disabled = false;
  }
}

function setAdminSettingsStatus(message = "", type = "") {
  const status = $("#adminSettingsStatus");
  if (!status) return;
  status.className = "form-status";
  if (type) status.classList.add(type);
  status.textContent = message;
}

function adminApiStatusText(item) {
  if (item.configured) return item.masked ? `已配置（${item.masked}）` : "已配置";
  return item.status === "active" ? "未配置，功能会降级" : "未配置，预留接口";
}

function adminApiStatusClass(item) {
  if (item.configured) return "ready";
  if (item.status === "active") return "missing";
  return "reserved";
}

function adminGroupLabel(group) {
  return {
    maps: "地图/企业数据",
    social: "社媒平台",
    search: "搜索 API",
    email: "邮箱/联系人",
    company: "公司数据",
    ai: "AI 大模型",
    runtime: "运行参数"
  }[group] || "其他 API";
}

function adminApiInputHtml(item) {
  const type = item.type === "secret" ? "password" : item.type === "int" ? "number" : "text";
  const attrs = [
    `type="${type}"`,
    `data-admin-setting-key="${escapeHtml(item.key)}"`,
    `data-admin-setting-type="${escapeHtml(item.type || "text")}"`,
    `name="${escapeHtml(item.key)}"`,
    `placeholder="${item.type === "secret" ? "留空不改；输入新值后保存" : ""}"`,
    "autocomplete=\"off\""
  ];
  if (item.min !== null && item.min !== undefined) attrs.push(`min="${Number(item.min)}"`);
  if (item.max !== null && item.max !== undefined) attrs.push(`max="${Number(item.max)}"`);
  const value = item.type === "secret" ? "" : item.value || "";
  return `<input ${attrs.join(" ")} value="${escapeHtml(value)}">`;
}

function formatApifyUsd(value) {
  const amount = Number(value || 0);
  return `$${amount.toFixed(amount >= 10 ? 2 : 4)}`;
}

function formatApifyDate(value) {
  const date = value ? new Date(value) : null;
  return date && !Number.isNaN(date.getTime())
    ? date.toLocaleString("zh-CN", { hour12: false })
    : "未提供";
}

function formatApiCount(value) {
  return new Intl.NumberFormat("zh-CN").format(Number(value || 0));
}

function apiOfficialMetrics(provider = {}) {
  const result = provider.official || {};
  const data = result.data || {};
  if (!result.ok) return [];
  if (provider.key === "serpapi") return [
    ["本月官方用量", formatApiCount(data.used), `${data.plan || "当前套餐"}`],
    ["官方剩余搜索", formatApiCount(data.remaining), data.limit ? `月额度 ${formatApiCount(data.limit)}` : "官方账户返回"],
    ["下次续期", formatApifyDate(data.renewalAt), data.hourLimit ? `本小时 ${formatApiCount(data.hourUsed)} / ${formatApiCount(data.hourLimit)}` : "官方账户返回"]
  ];
  if (provider.key === "hunter") {
    const categories = Array.isArray(data.categories) ? data.categories : [];
    return categories.slice(0, 3).map((item) => [
      item.key || "API credits",
      `${formatApiCount(item.used)} 已用`,
      `${formatApiCount(item.available)} 可用`
    ]);
  }
  if (provider.key === "deepseek") {
    return (data.balances || []).map((item) => [
      `${item.currency || "余额"} 可用余额`,
      `${item.total || "0"} ${item.currency || ""}`.trim(),
      `赠送 ${item.granted || "0"} · 充值 ${item.toppedUp || "0"}`
    ]);
  }
  return [];
}

function renderApiConsumption(data = {}) {
  const grid = $("#apiConsumptionGrid");
  const status = $("#apiConsumptionStatus");
  if (!grid || !status) return;
  const providers = Array.isArray(data.providers) ? data.providers : [];
  grid.innerHTML = providers.map((provider) => {
    const tracked = provider.tracked || {};
    const officialMetrics = apiOfficialMetrics(provider);
    const officialError = provider.official && !provider.official.ok ? provider.official.error : "";
    const metrics = [
      ["工作台今日调用", formatApiCount(tracked.calls), `${formatApiCount(tracked.failures)} 次失败`],
      ...(provider.limit ? [[provider.limitLabel || "官方上限", formatApiCount(provider.limit), provider.resetAt ? `重置 ${formatApifyDate(provider.resetAt)}` : ""]] : []),
      ...officialMetrics
    ];
    const officialReady = officialMetrics.length > 0;
    const statusLabel = !provider.configured
      ? "未配置"
      : officialReady
        ? "官方账户数据"
        : "工作台实测";
    const note = provider.officialNote || officialError || (officialReady ? "已连接供应商官方账户接口" : "仅统计本工作台请求");
    return `
      <article class="api-consumption-card ${provider.configured ? "configured" : "unconfigured"}">
        <header><strong>${escapeHtml(provider.label || provider.key)}</strong><span class="api-data-badge ${officialReady ? "official" : "tracked"}">${escapeHtml(statusLabel)}</span></header>
        <div class="api-consumption-metrics">
          ${metrics.map(([label, value, detail]) => `<div><span>${escapeHtml(label)}</span><b>${escapeHtml(value)}</b><small>${escapeHtml(detail || "")}</small></div>`).join("")}
        </div>
        <p>${escapeHtml(note)}</p>
      </article>
    `;
  }).join("") || `<p class="empty">没有可显示的 API 用量。</p>`;
  status.textContent = `数据更新时间：${formatApifyDate(data.checkedAt)}`;
}

async function loadApiConsumption() {
  const grid = $("#apiConsumptionGrid");
  const status = $("#apiConsumptionStatus");
  const button = $("#refreshApiConsumption");
  if (!grid || !status || currentSession?.role !== "admin") return;
  if (button) button.disabled = true;
  status.textContent = "正在读取供应商官方账户数据和工作台调用记录…";
  try {
    const response = await apiFetch("/api/admin/api-consumption", { cache: "no-store" });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    renderApiConsumption(result);
  } catch (error) {
    status.textContent = error.message || "API 用量读取失败";
    grid.innerHTML = `<p class="empty">无法读取 API 用量，请检查网络或 API Key 权限。</p>`;
  } finally {
    if (button) button.disabled = false;
  }
}

function renderApifyUsage(data = {}) {
  const grid = $("#apifyUsageGrid");
  const history = $("#apifyUsageHistory");
  const status = $("#apifyUsageStatus");
  if (!grid || !history || !status) return;
  const hasIncludedCredits = Number(data.includedCreditsUsd || 0) > 0;
  grid.innerHTML = `
    <article><span>绑定账户</span><strong>${escapeHtml(data.username || "未知账户")}</strong><small>${escapeHtml(data.plan || "未知套餐")}</small></article>
    <article><span>套餐月度额度</span><strong>${formatApifyUsd(data.includedCreditsUsd)}</strong><small>官方套餐包含额度</small></article>
    <article><span>本期累计消耗</span><strong>${formatApifyUsd(data.usedUsd)}</strong><small>折扣后官方用量</small></article>
    <article><span>预计剩余额度</span><strong>${formatApifyUsd(data.remainingCreditsUsd)}</strong><small>${hasIncludedCredits ? "套餐额度减去本期消耗" : "当前套餐未返回包含额度"}</small></article>
    <article><span>较上次新增消耗</span><strong>${formatApifyUsd(data.deltaSinceLastCheckUsd)}</strong><small>两次官方快照的差额</small></article>
    <article><span>额度到期 / 重置</span><strong>${escapeHtml(formatApifyDate(data.cycleEndAt))}</strong><small>当前月度账期结束时间</small></article>
    <article><span>月度消费上限</span><strong>${formatApifyUsd(data.maxMonthlyUsageUsd)}</strong><small>不是现金余额</small></article>
    <article><span>距消费上限可用</span><strong>${formatApifyUsd(data.remainingLimitUsd)}</strong><small>消费上限减去本期用量</small></article>
  `;
  const rows = Array.isArray(data.history) ? data.history.slice().reverse() : [];
  history.innerHTML = rows.length ? `
    <div class="apify-usage-history-head"><strong>官方用量快照</strong><span>只有用量发生变化时新增记录</span></div>
    ${rows.map((item) => `
      <div class="apify-usage-history-row">
        <span>${escapeHtml(formatApifyDate(item.checkedAt))}</span>
        <b>累计 ${formatApifyUsd(item.usedUsd)}</b>
        <strong>新增 ${formatApifyUsd(item.deltaUsd)}</strong>
        <small>剩余 ${formatApifyUsd(item.remainingCreditsUsd)}</small>
      </div>
    `).join("")}
  ` : "";
  status.textContent = `官方数据更新时间：${formatApifyDate(data.checkedAt)}`;
}

async function loadApifyUsage() {
  const grid = $("#apifyUsageGrid");
  const status = $("#apifyUsageStatus");
  const button = $("#refreshApifyUsage");
  if (!grid || !status || currentSession?.role !== "admin") return;
  const configured = (adminSettingsSnapshot?.catalog || []).some((item) => item.key === "APIFY_API_TOKEN" && item.configured);
  if (!configured) {
    status.textContent = "请先绑定并保存 APIFY_API_TOKEN";
    grid.innerHTML = `<p class="empty">Apify API Token 尚未配置。</p>`;
    $("#apifyUsageHistory").innerHTML = "";
    return;
  }
  if (button) button.disabled = true;
  status.textContent = "正在读取 Apify 官方账户、限额和月度用量…";
  try {
    const response = await apiFetch("/api/admin/apify-usage", { cache: "no-store" });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    renderApifyUsage(result);
  } catch (error) {
    status.textContent = error.message || "Apify 官方用量读取失败";
    grid.innerHTML = `<p class="empty">无法读取账户用量，请检查 Key 权限或稍后刷新。</p>`;
  } finally {
    if (button) button.disabled = false;
  }
}

const adminSourceDefinitions = [
  ["google", "Google Maps"], ["osm", "OpenStreetMap"], ["dealer", "官网 / 行业目录"],
  ["instagram", "Instagram"], ["facebook", "Facebook"], ["tiktok", "TikTok"],
  ["youtube", "YouTube"], ["linkedin", "LinkedIn"]
];

const adminScoreDefinitions = [
  ["automotive", "汽车业务"], ["country", "地区匹配"], ["chineseNev", "中国新能源"],
  ["huawei", "华为系列"], ["contact", "联系方式"], ["officialWebsite", "官网可信"],
  ["importDistribution", "进口分销"], ["businessActivity", "经营活跃"],
  ["decisionMaker", "决策人"]
];

function valueAtPath(object, path) {
  return String(path || "").split(".").reduce((value, key) => value?.[key], object);
}

function setValueAtPath(object, path, value) {
  const keys = String(path || "").split(".");
  const last = keys.pop();
  const parent = keys.reduce((current, key) => (current[key] ||= {}), object);
  parent[last] = value;
}

function renderAdminControlInputs(control = {}) {
  document.querySelectorAll("[data-control-path]").forEach((input) => {
    const value = valueAtPath(control, input.dataset.controlPath);
    if (input.type === "checkbox") input.checked = Boolean(value);
    else input.value = value ?? "";
  });
  const weightGrid = $("#adminScoreWeightGrid");
  if (weightGrid) {
    weightGrid.innerHTML = adminScoreDefinitions.map(([key, label]) => `
      <label>${escapeHtml(label)}<input type="number" min="0" max="30" data-control-path="quality.scoreWeights.${escapeHtml(key)}" value="${Number(control?.quality?.scoreWeights?.[key] || 0)}"></label>
    `).join("");
  }
  renderAdminSourcePolicies(control);
  renderAdminCountrySources(control);
}

function renderAdminSourcePolicies(control = {}) {
  const grid = $("#adminSourcePolicyGrid");
  if (!grid) return;
  const enabled = new Set(control?.discovery?.globalSources || []);
  const caps = control?.discovery?.sourceCaps || {};
  const weights = control?.discovery?.sourceWeights || {};
  grid.innerHTML = adminSourceDefinitions.map(([key, label]) => `
    <label class="admin-source-policy-card">
      <span><input type="checkbox" data-global-source="${key}" ${enabled.has(key) ? "checked" : ""}>${escapeHtml(label)}</span>
      <small>上限</small><input type="number" min="1" max="100" data-source-cap="${key}" value="${Number(caps[key] || 30)}">
      <small>权重</small><input type="number" min="1" max="10" data-source-weight="${key}" value="${Number(weights[key] || 1)}">
    </label>
  `).join("");
}

function renderAdminCountrySources(control = {}, selectedCountry = "") {
  const editor = $("#adminCountrySourceEditor");
  if (!editor) return;
  const country = selectedCountry || editor.querySelector("select")?.value || countries[0]?.name || "";
  const overrides = control?.discovery?.countrySourceOverrides || {};
  const hasOverride = Object.prototype.hasOwnProperty.call(overrides, country);
  const selected = new Set(hasOverride ? overrides[country] : control?.discovery?.globalSources || []);
  editor.innerHTML = `
    <div class="admin-country-source-toolbar">
      <label>目标国家<select id="adminCountrySourceSelect">${countries.map((item) => `<option value="${escapeHtml(item.name)}" ${item.name === country ? "selected" : ""}>${escapeHtml(item.name)}</option>`).join("")}</select></label>
      <label class="admin-check-row"><input type="checkbox" id="adminCountryUseGlobal" ${hasOverride ? "" : "checked"}>使用全局来源</label>
    </div>
    <div class="admin-toggle-grid admin-country-source-options">
      ${adminSourceDefinitions.map(([key, label]) => `<label><input type="checkbox" data-country-source="${key}" ${selected.has(key) ? "checked" : ""} ${hasOverride ? "" : "disabled"}>${escapeHtml(label)}</label>`).join("")}
    </div>
  `;
}

function collectAdminControlPayload(form) {
  const control = JSON.parse(JSON.stringify(adminSettingsSnapshot?.controlCenter || {}));
  form.querySelectorAll("[data-control-path]").forEach((input) => {
    let value = input.type === "checkbox" ? input.checked : input.value;
    if (input.type === "number") value = Number(value || 0);
    setValueAtPath(control, input.dataset.controlPath, value);
  });
  control.discovery ||= {};
  control.discovery.globalSources = Array.from(form.querySelectorAll("[data-global-source]:checked")).map((input) => input.dataset.globalSource);
  control.discovery.sourceCaps = Object.fromEntries(Array.from(form.querySelectorAll("[data-source-cap]")).map((input) => [input.dataset.sourceCap, Number(input.value || 0)]));
  control.discovery.sourceWeights = Object.fromEntries(Array.from(form.querySelectorAll("[data-source-weight]")).map((input) => [input.dataset.sourceWeight, Number(input.value || 1)]));
  return control;
}

function renderAdminSettings(settings = {}) {
  adminSettingsSnapshot = settings;
  const catalog = Array.isArray(settings.catalog) ? settings.catalog : [];
  const apiList = $("#adminApiList");
  const runtimeGrid = $("#adminRuntimeGrid");
  if (apiList) {
    const apiItems = catalog
      .filter((item) => item.group !== "runtime" && item.group !== "ai")
      .sort((a, b) =>
        Number(Boolean(b.configured)) - Number(Boolean(a.configured))
        || Number((b.status || "") === "active") - Number((a.status || "") === "active")
        || String(a.label || a.key || "").localeCompare(String(b.label || b.key || ""), "zh-CN")
      );
    const visibleItems = adminApiShowAll ? apiItems : apiItems.slice(0, 5);
    apiList.innerHTML = visibleItems.map((item) => `
      <article class="admin-api-card ${escapeHtml(adminApiStatusClass(item))}">
        <div class="admin-api-card-head">
          <div>
            <strong>${escapeHtml(item.label)}</strong>
            <span>${escapeHtml(adminGroupLabel(item.group))} · ${escapeHtml(item.key)}</span>
          </div>
          <b>${escapeHtml(adminApiStatusText(item))}</b>
        </div>
        <p>${escapeHtml(item.use || "保存后进入后台配置池。")}</p>
        ${adminApiInputHtml(item)}
      </article>
    `).join("");
    const apiSummary = $("#adminApiListSummary");
    if (apiSummary) {
      const configured = apiItems.filter((item) => item.configured).length;
      apiSummary.textContent = adminApiShowAll
        ? `已展开全部 ${apiItems.length} 个 API，已配置 ${configured} 个`
        : `优先显示已配置 API，当前显示 ${Math.min(5, apiItems.length)} / ${apiItems.length} 个`;
    }
    const toggle = $("#toggleAdminApis");
    if (toggle) {
      toggle.hidden = apiItems.length <= 5;
      toggle.textContent = adminApiShowAll ? "收起" : "展开全部";
    }
  }
  const aiList = $("#adminAiApiList");
  if (aiList) {
    const aiItems = catalog.filter((item) => item.group === "ai");
    aiList.innerHTML = aiItems.map((item) => `
      <article class="admin-api-card ${escapeHtml(adminApiStatusClass(item))}">
        <div class="admin-api-card-head"><div><strong>${escapeHtml(item.label)}</strong><span>${escapeHtml(item.key)}</span></div><b>${escapeHtml(adminApiStatusText(item))}</b></div>
        <p>${escapeHtml(item.use || "AI复核配置")}</p>${adminApiInputHtml(item)}
      </article>
    `).join("");
  }
  if (runtimeGrid) {
    runtimeGrid.innerHTML = catalog
      .filter((item) => item.group === "runtime")
      .map((item) => `
        <label>${escapeHtml(item.label)}
          ${adminApiInputHtml(item)}
          <small>${escapeHtml(item.use || "")}${item.key === "DISCOVERY_MAX_CONCURRENCY" ? "，保存后立即生效。" : item.key === "NETWORK_DEFAULT_TIMEOUT" ? "，保存后重启生效。" : ""}</small>
        </label>
      `).join("");
  }
  renderCustomApis(settings.customApis || []);
  renderAdminControlInputs(settings.controlCenter || {});
  const summary = $("#adminSettingsSummary");
  if (summary) {
    const configured = catalog.filter((item) => item.group !== "runtime" && item.configured).length;
    const total = catalog.filter((item) => item.group !== "runtime").length;
    summary.textContent = `已配置 ${configured}/${total} 个 API，支持继续添加自定义 API`;
  }
}

function compactUserAgent(value = "") {
  const text = String(value || "");
  if (!text) return "未知浏览器";
  const browser = text.includes("Edg/")
    ? "Microsoft Edge"
    : text.includes("Chrome/")
      ? "Chrome"
      : text.includes("Firefox/")
        ? "Firefox"
        : text.includes("Safari/")
          ? "Safari"
          : "浏览器";
  const os = text.includes("Windows")
    ? "Windows"
    : text.includes("Mac OS")
      ? "macOS"
      : text.includes("Android")
        ? "Android"
        : text.includes("iPhone") || text.includes("iPad")
          ? "iOS"
          : "";
  return [browser, os].filter(Boolean).join(" / ");
}

function customApiRowHtml(item = {}) {
  const id = item.id || `new-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const type = item.type === "text" ? "text" : "secret";
  return `
    <article class="custom-api-row" data-custom-api-row data-custom-api-id="${escapeHtml(id)}">
      <div class="custom-api-row-head">
        <strong>${escapeHtml(item.name || "新增 API")}</strong>
        <button class="danger-button compact" type="button" data-remove-custom-api>删除</button>
      </div>
      <div class="admin-settings-grid">
        <label>API 名称<input data-custom-api-name value="${escapeHtml(item.name || "")}" placeholder="例如 Brave Search API"></label>
        <label>配置 Key<input data-custom-api-env value="${escapeHtml(item.envKey || "")}" placeholder="例如 BRAVE_SEARCH_API_KEY"></label>
        <label>保存类型
          <select data-custom-api-type>
            <option value="secret" ${type === "secret" ? "selected" : ""}>密钥 / Token</option>
            <option value="text" ${type === "text" ? "selected" : ""}>普通文本</option>
          </select>
        </label>
        <label>API 值<input data-custom-api-value type="${type === "secret" ? "password" : "text"}" value="${type === "secret" ? "" : escapeHtml(item.value || "")}" placeholder="${type === "secret" ? "留空不改；输入新值后保存" : ""}"></label>
        <label>接口地址<input data-custom-api-base value="${escapeHtml(item.baseUrl || "")}" placeholder="https://api.example.com"></label>
        <label>用途说明<input data-custom-api-notes value="${escapeHtml(item.notes || "")}" placeholder="这个 API 用来做什么"></label>
      </div>
      <small>${item.configured ? `已配置${item.masked ? `（${escapeHtml(item.masked)}）` : ""}` : "未配置"}</small>
    </article>
  `;
}

function renderCustomApis(items = []) {
  const list = $("#customApiList");
  if (!list) return;
  list.innerHTML = items.length
    ? items.map((item) => customApiRowHtml(item)).join("")
    : `<p class="empty">还没有自定义 API。点击“添加 API”后填写名称、配置 Key 和密钥。</p>`;
}

function addCustomApiRow() {
  const list = $("#customApiList");
  if (!list) return;
  if (list.querySelector(".empty")) list.innerHTML = "";
  list.insertAdjacentHTML("beforeend", customApiRowHtml());
}

function collectAdminSettingsPayload(form) {
  const payload = {};
  form.querySelectorAll("[data-admin-setting-key]").forEach((input) => {
    payload[input.dataset.adminSettingKey] = input.value;
  });
  payload.customApis = Array.from(form.querySelectorAll("[data-custom-api-row]")).map((row) => ({
    id: row.dataset.customApiId || "",
    name: row.querySelector("[data-custom-api-name]")?.value || "",
    envKey: row.querySelector("[data-custom-api-env]")?.value || "",
    type: row.querySelector("[data-custom-api-type]")?.value || "secret",
    value: row.querySelector("[data-custom-api-value]")?.value || "",
    baseUrl: row.querySelector("[data-custom-api-base]")?.value || "",
    notes: row.querySelector("[data-custom-api-notes]")?.value || "",
    enabled: true
  }));
  payload.controlCenter = collectAdminControlPayload(form);
  return payload;
}

async function loadAdminSettings() {
  if (currentSession?.role !== "admin") return;
  setAdminSettingsStatus("正在读取系统设置…");
  try {
    const response = await apiFetch("/api/admin/settings", { cache: "no-store" });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    renderAdminSettings(result);
    setAdminSettingsStatus("设置已读取。密钥输入框留空表示保持不变。", "success");
    loadApifyUsage();
    loadApiConsumption();
  } catch (error) {
    setAdminSettingsStatus(error.message || "设置读取失败。", "error");
  }
}

async function saveAdminSettings(event) {
  event.preventDefault();
  if (currentSession?.role !== "admin") return;
  const form = event.currentTarget;
  const submit = form.querySelector("button[type='submit']");
  const data = collectAdminSettingsPayload(form);
  submit.disabled = true;
  setAdminSettingsStatus("正在保存系统设置…");
  try {
    const response = await apiFetch("/api/admin/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    renderAdminSettings(result);
    loadApifyUsage();
    loadApiConsumption();
    loadDiscoverySourceStatus();
    loadAdminOperations();
    if (result.restartRequiredChanged) {
      setAdminSettingsStatus("设置已保存。网络超时已变更，需要重启服务器后生效；获客并发数已立即生效。", "success");
      if (confirm("设置已保存，但网络超时需要重启服务器后生效。现在重启服务器吗？")) {
        await restartAdminServer();
      }
    } else {
      setAdminSettingsStatus("设置已保存。API Key 已进入后台配置池；获客并发数已立即生效。", "success");
    }
  } catch (error) {
    setAdminSettingsStatus(error.message || "设置保存失败。", "error");
  } finally {
    submit.disabled = false;
  }
}

async function restartAdminServer() {
  setAdminSettingsStatus("正在重启服务器，页面可能会短暂断开…", "success");
  const response = await apiFetch("/api/admin/restart", { method: "POST" });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  window.setTimeout(() => {
    window.location.reload();
  }, 3500);
}

function formatBytes(value = 0) {
  const bytes = Number(value || 0);
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(units.length - 1, Math.floor(Math.log(bytes) / Math.log(1024)));
  return `${(bytes / (1024 ** index)).toFixed(index ? 1 : 0)} ${units[index]}`;
}

function renderAdminOperations(data = {}) {
  adminOperationsSnapshot = data;
  const system = data.system || {};
  const summary = data.data || {};
  const overview = $("#adminOverviewGrid");
  if (overview) overview.innerHTML = [
    ["服务状态", "运行正常", `版本 ${system.version || "-"}`],
    ["当前任务", `${summary.activeJobs || 0} 个运行中`, `共 ${summary.jobs || 0} 条记录`],
    ["业务数据", `${summary.reviewLeads || 0} 条待审核`, `${summary.customers || 0} 个客户`],
    ["AI复核", system.aiEnabled ? "已启用" : "未启用", `并发 ${system.workerConcurrency || 0}`],
    ["数据库", system.database || "-", summary.databaseBytes ? formatBytes(summary.databaseBytes) : "云数据库"],
    ["最近备份", system.lastBackupAt ? formatJobTime(system.lastBackupAt) : "尚未备份", `服务器 ${formatJobTime(system.serverTime || "")}`]
  ].map(([label, value, note]) => `<article><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong><small>${escapeHtml(note)}</small></article>`).join("");

  const sources = Array.isArray(data.sources) ? data.sources : [];
  const sourceRows = $("#adminSourceRows");
  if (sourceRows) sourceRows.innerHTML = sources.length ? sources.map((source) => `
    <tr>
      <td><strong>${escapeHtml(source.label)}</strong></td>
      <td><span class="admin-health ${source.configured && source.enabled ? "ready" : "warning"}">${source.enabled ? (source.configured ? "可用" : "未配置") : "已停用"}</span></td>
      <td>${source.todayCalls || 0}${source.todayFailures ? `<small>${source.todayFailures} 次失败</small>` : ""}</td>
      <td>${source.completedTasks || 0} / ${source.taskCount || 0}</td>
      <td>${source.discovered || 0} / ${source.imported || 0}</td>
      <td>${escapeHtml(source.lastSuccessAt ? formatJobTime(source.lastSuccessAt) : "暂无")}</td>
      <td title="${escapeHtml(source.lastFailure || "")}">${escapeHtml(source.lastFailure ? String(source.lastFailure).slice(0, 70) : "-")}</td>
      <td><button class="ghost compact" type="button" data-test-admin-source="${escapeHtml(source.key)}">测试</button></td>
    </tr>
  `).join("") : `<tr><td colspan="8">暂无来源数据。</td></tr>`;
  if ($("#adminSourceSummary")) $("#adminSourceSummary").textContent = `${sources.filter((item) => item.enabled && item.configured).length} 个来源可用`;

  const tasks = Array.isArray(data.tasks) ? data.tasks : [];
  const taskList = $("#adminTaskList");
  if (taskList) taskList.innerHTML = tasks.length ? tasks.slice(0, 20).map((job) => `
    <article class="admin-task-row">
      <span class="admin-health ${job.status === "completed" ? "ready" : job.status === "failed" ? "error" : "warning"}">${escapeHtml({completed:"完成",failed:"失败",running:"运行中",queued:"排队",canceled:"已取消"}[job.status] || job.status)}</span>
      <strong>${escapeHtml(job.country || "未知地区")} · ${escapeHtml(discoverySourceLabel(job.sourceMode))}</strong>
      <span>${escapeHtml(job.ownerUsername || "admin")}</span>
      <span>${escapeHtml(formatJobTime(job.updatedAt || job.createdAt || ""))}</span>
      <small title="${escapeHtml(job.error || job.message || "")}">
        ${escapeHtml((job.error || job.message || "").slice(0, 100))}
        ${job.result ? `<br>发现 ${discoveryJobRawCount(job)} · 导入 ${discoveryJobImportedCount(job)} · 跳过 ${discoveryJobSkippedCount(job)}${discoveryJobSkipBreakdownText(job) ? `（${escapeHtml(discoveryJobSkipBreakdownText(job))}）` : ""}` : ""}
      </small>
    </article>
  `).join("") : `<p class="empty">暂无任务记录。</p>`;
  if ($("#adminTaskSummary")) $("#adminTaskSummary").textContent = `${summary.activeJobs || 0} 个运行中，${summary.failedJobs || 0} 个失败`;
  if ($("#adminDataSummary")) $("#adminDataSummary").textContent = `工作区 ${summary.workspaces || 0} · 待审核 ${summary.reviewLeads || 0} · 客户 ${summary.customers || 0} · 已拒绝 ${summary.rejectedLeads || 0} · 删除指纹 ${summary.deletedRecords || 0}`;

  const events = Array.isArray(data.auditEvents) ? data.auditEvents : [];
  const audit = $("#adminAuditList");
  if (audit) audit.innerHTML = events.length ? events.map((event) => `
    <article><strong>${escapeHtml(event.action)}</strong><span>${escapeHtml(event.username)} · ${escapeHtml(formatJobTime(event.createdAt || ""))}</span><p>${escapeHtml(event.detail || "无补充信息")}</p><small>${escapeHtml(event.ip || "")}</small></article>
  `).join("") : `<p class="empty">暂无管理员操作记录。</p>`;
}

async function loadAdminOperations({ feedback = false } = {}) {
  if (currentSession?.role !== "admin") return;
  const button = $("#reloadAdminOperations");
  const finishButtonLoading = feedback ? startButtonLoading(button, "刷新中") : null;
  if (feedback) setAdminSettingsStatus("正在刷新系统运行状态…");
  try {
    const response = await apiFetch("/api/admin/operations", { cache: "no-store" });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    renderAdminOperations(result);
    if (feedback) {
      finishButtonLoading?.("刷新成功", { autoResetMs: 1800 });
      setAdminSettingsStatus(`刷新成功，系统状态已更新（${new Date().toLocaleTimeString("zh-CN", { hour12: false })}）。`, "success");
    }
  } catch (error) {
    finishButtonLoading?.("刷新失败", { autoResetMs: 1800 });
    setAdminSettingsStatus(error.message || "运行状态读取失败。", "error");
  }
}

async function runAdminOperation(action) {
  const pruneCutoffDate = action === "prune-search-data" ? $("#adminPruneCutoffDate")?.value : "";
  if (action === "prune-search-data" && !pruneCutoffDate) {
    setAdminSettingsStatus("请先选择历史数据截止日期。", "error");
    return;
  }
  const labels = {
    "cancel-active-jobs": "确定终止当前所有运行和排队任务吗？",
    "clear-failed-jobs": "确定删除全部失败和已取消任务记录吗？",
    "clean-old-jobs": "确定按设置的保留天数清理过期任务吗？",
    deduplicate: "确定扫描所有账号并删除重复线索吗？",
    "prune-search-data": `确定删除 ${pruneCutoffDate} 之前的待审核线索、拒绝记录和搜索任务吗？客户池数据会永久保留。该操作不可撤销。`,
    "clear-tombstones": "确定清除已删除线索的拦截指纹吗？清除后这些线索可能再次被搜到。",
    "clear-rejected-memory": "确定清除全部已拒绝线索记忆吗？清除后被拒绝线索可能再次进入审核。",
    "force-logout": "确定强制所有账号重新登录吗？当前管理员也会退出。"
  };
  if (!confirm(labels[action] || "确定执行该操作吗？")) return;
  setAdminSettingsStatus("正在执行管理操作…");
  if (action === "prune-search-data") {
    const response = await apiFetch("/api/admin/prune-search-data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ confirm: "PRUNE_SEARCH_DATA", cutoffDate: pruneCutoffDate })
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    setAdminSettingsStatus(
      `清理完成：待审核 ${result.reviewLeads || 0} 条、拒绝记录 ${result.rejectedLeads || 0} 条、搜索任务 ${result.discoveryJobs || 0} 条；客户池未改动。`,
      "success"
    );
    await loadAdminOperations();
    return;
  }
  const dangerous = new Set(["deduplicate", "clear-tombstones", "clear-rejected-memory", "force-logout"]);
  const response = await apiFetch("/api/admin/operations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, confirm: dangerous.has(action) ? action : "" })
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  if (action === "force-logout") {
    window.location.href = "/login.html";
    return;
  }
  setAdminSettingsStatus("操作完成。", "success");
  await loadAdminOperations();
}

async function downloadAdminBackup() {
  setAdminSettingsStatus("正在生成业务备份…");
  const response = await apiFetch("/api/admin/backup", { cache: "no-store" });
  if (!response.ok) {
    const result = await response.json().catch(() => ({}));
    throw new Error(result.error || `HTTP ${response.status}`);
  }
  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition") || "";
  const filename = disposition.match(/filename="([^"]+)"/)?.[1] || `hima-backup-${new Date().toISOString().slice(0, 10)}.json`;
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
  setAdminSettingsStatus("业务备份已生成。", "success");
  loadAdminOperations();
}

async function restoreAdminBackup(file) {
  if (!file || !confirm("恢复会覆盖同名账号当前的业务数据，确定继续吗？")) return;
  const payload = JSON.parse(await file.text());
  const response = await apiFetch("/api/admin/restore-backup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  setAdminSettingsStatus(`备份恢复完成，共恢复 ${result.workspacesRestored || 0} 个工作区。`, "success");
  await loadAdminOperations();
}

function userDisplayName(username) {
  return {
    admin: "管理员",
    chenruizhe: "陈睿哲",
    xuchenghui: "徐成会",
    sunruilin: "孙瑞林",
    sunpengfei: "孙鹏飞",
    shihaohua: "石豪华",
    fanjie: "范杰"
  }[String(username || "").trim().toLowerCase()] || "-";
}

function renderUsers(users = []) {
  const rows = $("#userRows");
  if (!rows) return;
  $("#userCount").textContent = `${users.length} 位用户`;
  rows.innerHTML = users.length ? users.map((user, index) => `
    <tr>
      <td>${index + 1}</td>
      <td><strong>${escapeHtml(user.username)}</strong>${user.builtIn ? `<br><small>系统内置</small>` : ""}</td>
      <td><strong class="user-display-name">${escapeHtml(userDisplayName(user.username))}</strong></td>
      <td>${escapeHtml(userRoleLabel(user.role))}</td>
      <td>${escapeHtml(assignedCountrySummary(user.assignedCountries))}</td>
      <td>${escapeHtml(formatSyncTime(user.createdAt))}</td>
      <td>
        <span class="user-status ${user.online ? "online" : "disabled"}">${user.online ? "在线" : "离线"}</span>
        <br><small>${escapeHtml(user.lastSeenAt ? formatJobTime(user.lastSeenAt) : "暂无记录")}</small>
      </td>
      <td><span class="user-status ${user.status === "disabled" ? "disabled" : ""}">${user.status === "disabled" ? "已禁用" : "启用中"}</span></td>
      <td><div class="user-actions">${user.builtIn ? `
        <button type="button" data-user-action="activity" data-username="${escapeHtml(user.username)}">记录</button>
        <span class="meta">受保护</span>` : `
        <button type="button" data-user-action="activity" data-username="${escapeHtml(user.username)}">记录</button>
        <button type="button" data-user-action="countries" data-countries="${escapeHtml((user.assignedCountries || []).join("|"))}" data-username="${escapeHtml(user.username)}">区域</button>
        <button type="button" data-user-action="password" data-username="${escapeHtml(user.username)}">改密码</button>
        <select class="user-role-select" data-user-action="role-select" data-role="${escapeHtml(user.role)}" data-username="${escapeHtml(user.username)}" aria-label="修改 ${escapeHtml(user.username)} 的角色">
          ${userRoleOptions(user.role)}
        </select>
        <button type="button" data-user-action="status" data-status="${user.status}" data-username="${escapeHtml(user.username)}">${user.status === "disabled" ? "启用" : "禁用"}</button>
        <button class="danger" type="button" data-user-action="delete" data-username="${escapeHtml(user.username)}">删除</button>`}</div></td>
    </tr>`).join("") : `<tr><td colspan="9">暂无用户。管理员可通过左侧表单添加。</td></tr>`;
}

function renderUserActivity(data = {}) {
  const panel = $("#userActivityPanel");
  if (!panel) return;
  const user = data.user || {};
  const presence = data.presence || {};
  const events = Array.isArray(data.events) ? data.events : [];
  panel.hidden = false;
  panel.innerHTML = `
    <div class="panel-head">
      <div>
        <h3>${escapeHtml(user.username || presence.username || "账号")} 操作记录</h3>
        <span>${presence.online ? "当前在线" : "当前离线"} · 最近 ${events.length} 条操作记录</span>
      </div>
      <button class="ghost compact" type="button" data-close-user-activity>关闭</button>
    </div>
    <div class="user-activity-summary">
      <span><b>在线状态</b>${presence.online ? "在线" : "离线"}</span>
      <span><b>最后活跃</b>${escapeHtml(presence.lastSeenAt ? formatJobTime(presence.lastSeenAt) : "暂无记录")}</span>
      <span><b>最近 IP</b>${escapeHtml(presence.ip || "unknown")}</span>
      <span><b>设备</b>${escapeHtml(compactUserAgent(presence.userAgent || ""))}</span>
    </div>
    <div class="admin-audit-list user-operation-list">
      ${events.length ? events.map((event) => `
        <article>
          <strong>${escapeHtml(event.action || "账号操作")}</strong>
          <span>${escapeHtml(event.username || user.username || "账号")} · ${escapeHtml(formatJobTime(event.createdAt || ""))}</span>
          <p title="${escapeHtml(event.userAgent || event.detail || "")}">${escapeHtml(event.kind === "login" ? compactUserAgent(event.userAgent || "") : (event.detail || "无补充信息"))}</p>
          <small>${escapeHtml(event.ip || "")}</small>
        </article>
      `).join("") : `<p class="empty">暂无操作记录。</p>`}
    </div>
  `;
}

async function loadUserActivity(username) {
  const panel = $("#userActivityPanel");
  if (panel) {
    panel.hidden = false;
    panel.innerHTML = `<p class="empty">正在读取 ${escapeHtml(username)} 的记录…</p>`;
  }
  const response = await apiFetch(`/api/users/${encodeURIComponent(username)}/activity`, { cache: "no-store" });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  renderUserActivity(result);
}

function renderUserCountryEditor(username, selected = []) {
  closeUserRegionModal();
  const modal = document.createElement("div");
  modal.className = "user-region-modal-backdrop";
  modal.dataset.userRegionModal = "true";
  modal.innerHTML = `
    <div class="user-region-modal" role="dialog" aria-modal="true" aria-label="${escapeHtml(username)} 负责区域">
      <div class="panel-head">
        <div>
          <h3>${escapeHtml(username)} 负责区域</h3>
          <span>勾选负责的国外国家；全不勾选表示全部国外国家。国内区域不受影响。</span>
        </div>
        <button class="ghost compact" type="button" data-close-user-region-modal>关闭</button>
      </div>
      <div class="user-country-checklist user-country-checklist-wide" data-user-country-editor>
        ${countryCheckboxListHtml(`edit-user-country-${username}`, selected)}
      </div>
      <div class="result-actions">
        <button class="ghost" type="button" data-close-user-region-modal>取消</button>
        <button class="primary" type="button" data-save-user-countries data-username="${escapeHtml(username)}">确认</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
}

function closeUserRegionModal() {
  document.querySelector("[data-user-region-modal]")?.remove();
}

function setLeadParserStatus(message, state = "") {
  const status = $("#leadParserStatus");
  if (!status) return;
  status.textContent = message;
  status.dataset.state = state;
}

function selectManualLeadValue(select, value) {
  if (!select || !value) return;
  const target = String(value).trim().toLowerCase();
  const option = [...select.options].find((item) => item.value.trim().toLowerCase() === target);
  if (option) select.value = option.value;
}

function applyParsedLeadToManualForm(result) {
  const form = $("#leadForm");
  if (!form) return;
  manualParsedLead = result;
  form.elements.company.value = result.company || "";
  form.elements.country.value = result.country || "";
  form.elements.city.value = result.city || "";
  form.elements.source.value = result.source || (result.parsedSourceKind === "social" ? "Social media" : "Website");
  form.elements.customerWebsite.value = result.customerWebsite || "";
  form.elements.contactName.value = result.contactName || "";
  form.elements.contactRole.value = result.contactRole || "";
  form.elements.email.value = result.email || "";
  form.elements.phone.value = result.phone || "";
  form.elements.whatsapp.value = result.whatsapp || "";
  form.elements.website.value = result.websiteContent || result.sourceExcerpt || "";
  selectManualLeadValue(form.elements.type, result.type);
  selectManualLeadValue(form.elements.model, result.model);
}

function renderLeadParserResult(result) {
  const container = $("#leadParserResult");
  if (!container) return;
  const sourceUrl = safeHttpUrl(result.sourceUrl);
  const websiteUrl = safeHttpUrl(result.customerWebsite);
  const location = [result.country, result.city].filter(Boolean).join(" · ") || "未识别";
  const contacts = [result.email, result.phone, result.whatsapp].filter(Boolean).join(" · ") || "未发现";
  const sourceCount = Number(result.sourceCoverage?.total || result.evidenceSources?.length || 0);
  container.innerHTML = `
    <div class="lead-parser-result-head">
      <span>${escapeHtml(result.parsedSourceKind === "social" ? "社媒主页" : "企业官网")}</span>
      <strong>${escapeHtml(result.company || "未识别公司名")}</strong>
    </div>
    <dl>
      <div><dt>地区</dt><dd>${escapeHtml(location)}</dd></div>
      <div><dt>客户类型</dt><dd>${escapeHtml(result.type || "待确认")}</dd></div>
      <div><dt>联系方式</dt><dd>${escapeHtml(contacts)}</dd></div>
      <div><dt>初步评分</dt><dd>${escapeHtml(result.score ?? 0)} 分 · ${sourceCount} 个公开来源</dd></div>
      ${websiteUrl ? `<div><dt>客户官网</dt><dd><a href="${escapeHtml(websiteUrl)}" target="_blank" rel="noopener">${escapeHtml(websiteUrl)}</a></dd></div>` : ""}
      ${sourceUrl && sourceUrl !== websiteUrl ? `<div><dt>来源页面</dt><dd><a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener">${escapeHtml(sourceUrl)}</a></dd></div>` : ""}
    </dl>`;
  container.hidden = false;
}

function resetManualLeadParser() {
  manualParsedLead = null;
  $("#leadParserForm")?.reset();
  const result = $("#leadParserResult");
  if (result) {
    result.hidden = true;
    result.innerHTML = "";
  }
  setLeadParserStatus("支持企业官网、Facebook、Instagram、TikTok、YouTube、LinkedIn 等公开主页。");
}

function openManualLeadModal() {
  const modal = $("#manualLeadModal");
  if (!modal) return;
  modal.hidden = false;
  document.body.classList.add("modal-open");
  window.requestAnimationFrame(() => $("#leadParserUrl")?.focus());
}

function closeManualLeadModal() {
  const modal = $("#manualLeadModal");
  if (!modal) return;
  modal.hidden = true;
  document.body.classList.remove("modal-open");
}

async function loadUsers() {
  if (currentSession?.role !== "admin") return;
  const rows = $("#userRows");
  if (rows) rows.innerHTML = `<tr><td colspan="9">正在读取用户列表…</td></tr>`;
  const response = await apiFetch("/api/users", { cache: "no-store" });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
  adminUsers = Array.isArray(result.users) ? result.users : [];
  renderUsers(adminUsers);
  renderScheduleTargetOptions();
}

function renderDiscoveryDistribution(data = {}) {
  const box = $("#discoveryDistributionResult");
  const executeButton = $("#executeDiscoveryDistribution");
  if (!box) return;
  const totals = data.totals || {};
  const rows = Array.isArray(data.rows) ? data.rows : [];
  const unassigned = Array.isArray(data.unassigned) ? data.unassigned : [];
  if (executeButton) {
    executeButton.disabled = Boolean(data.executed) || Number(totals.copyJobs || 0) <= 0;
  }
  box.innerHTML = `
    <div class="admin-distribution-summary">
      <span><b>${Number(totals.sourceJobs || 0)}</b>来源任务</span>
      <span><b>${Number(totals.sourceLeads || 0)}</b>来源线索</span>
      <span><b>${Number(totals.copyJobs || 0)}</b>待复制任务</span>
      <span><b>${Number(totals.copyLeads || 0)}</b>${data.executed ? "已复制线索" : "待复制线索"}</span>
      <span><b>${Number(totals.duplicates || 0)}</b>重复跳过</span>
      <span><b>${Number(totals.unassignedJobs || 0)}</b>未分配地区</span>
    </div>
    <div class="admin-distribution-table">
      <table>
        <thead><tr><th>销售账号</th><th>负责区域</th><th>任务</th><th>新线索</th><th>重复</th><th>已分配过</th></tr></thead>
        <tbody>${rows.length ? rows.map((row) => `
          <tr>
            <td><strong>${escapeHtml(row.username)}</strong></td>
            <td>${escapeHtml(assignedCountrySummary(row.assignedCountries))}</td>
            <td>${Number(row.jobs || 0)}</td>
            <td><strong>${Number(row.leads || 0)}</strong></td>
            <td>${Number(row.duplicates || 0)}</td>
            <td>${Number(row.alreadyDistributed || 0)}</td>
          </tr>`).join("") : `<tr><td colspan="6">没有配置明确负责国家的销售账号。</td></tr>`}</tbody>
      </table>
    </div>
    ${unassigned.length ? `
      <p class="admin-distribution-note">未找到地区负责人：${escapeHtml(
        [...new Set(unassigned.map((item) => item.country || "未指定地区"))].join("、")
      )}</p>` : ""}
    <p class="form-status success">${data.executed
      ? `复制完成。销售登录后会在搜索记录中看到“管理员搜索导入”，并自行点击“手动导入”。`
      : `预览完成，尚未修改任何销售账号数据。`}</p>
  `;
}

async function previewDiscoveryDistribution() {
  const button = $("#previewDiscoveryDistribution");
  const box = $("#discoveryDistributionResult");
  const finish = startButtonLoading(button, "正在预览");
  if (box) box.innerHTML = `<p class="empty">正在检查地区负责人、现有任务和客户数据并执行去重…</p>`;
  try {
    const response = await apiFetch("/api/admin/discovery-distribution-preview", { cache: "no-store" });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    renderDiscoveryDistribution(result);
    finish("预览分配", { autoResetMs: 800 });
  } catch (error) {
    if (box) box.innerHTML = `<p class="form-status error">${escapeHtml(error.message || "分配预览失败")}</p>`;
    finish("预览失败", { autoResetMs: 1600 });
  }
}

async function executeDiscoveryDistribution() {
  if (!confirm("确认按预览结果复制搜索任务吗？复制后销售可看到记录，但仍需销售手动导入线索。")) return;
  const button = $("#executeDiscoveryDistribution");
  const finish = startButtonLoading(button, "正在复制");
  try {
    const response = await apiFetch("/api/admin/distribute-discovery-jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ confirm: "DISTRIBUTE_ADMIN_SEARCHES" })
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    renderDiscoveryDistribution(result);
    finish("复制完成", { disabled: true });
  } catch (error) {
    window.alert(error.message || "复制分配失败");
    finish("重新确认", { disabled: false, autoResetMs: 1600 });
  }
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
  const greetingBox = $("#timeGreeting");
  const dateBox = $("#beijingDate");
  const accountName = String(currentSession?.username || "").trim();
  if (greetingBox) greetingBox.textContent = accountName ? `${accountName}，${greeting}` : greeting;
  if (dateBox) {
    dateBox.textContent =
      `${parts.year}年${parts.month}月${parts.day}日 · ${weekday} · ` +
      `${parts.hour}:${parts.minute}:${parts.second} · 北京时间`;
  }
}

async function init() {
  window.__workbenchInitErrors = [];
  applyUiSettings();
  bindUiSettings();
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
  await hydrateCloudState(false);
  const startupSteps = [
    ["北京时间", renderBeijingGreeting],
    ["用户区域", renderUserCountryOptions],
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
    ["销售地图", renderSalesOverview],
    ["导航", bindNavigation],
    ["销售地图交互", bindSalesOverview],
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
  renderWebsiteLeads();
  loadUsers().catch((error) => {
    if ($("#userRows")) $("#userRows").innerHTML = `<tr><td colspan="8">${escapeHtml(error.message)}</td></tr>`;
  });
  loadAdminSettings();
  loadAdminOperations();
  setInterval(renderBeijingGreeting, 1_000);
  loadDiscoveryJobs().catch((error) => {
    if ($("#discoveryJobList")) {
      $("#discoveryJobList").innerHTML = `<p class="empty">任务读取失败：${escapeHtml(error.message)}</p>`;
    }
  });
  loadDiscoverySchedules().catch((error) => {
    if ($("#personalScheduleList")) {
      $("#personalScheduleList").innerHTML = `<p class="empty">定时任务读取失败：${escapeHtml(error.message)}</p>`;
    }
    if ($("#scheduleList") && currentSession?.role === "admin") {
      $("#scheduleList").innerHTML = `<p class="empty">定时计划读取失败：${escapeHtml(error.message)}</p>`;
    }
  });
  if (currentSession?.role === "admin") {
    loadScheduledDiscoveryJobs().catch((error) => {
      if ($("#scheduledRunList")) {
        $("#scheduledRunList").innerHTML = `<p class="empty">2.0 执行记录读取失败：${escapeHtml(error.message)}</p>`;
      }
    });
  }
  discoveryJobsTimer = window.setInterval(() => {
    loadDiscoveryJobs().catch(() => undefined);
    loadDiscoverySchedules().catch(() => undefined);
    scheduledRunPollTick += 1;
    if (currentSession?.role === "admin" && scheduledRunPollTick % 3 === 0) {
      loadScheduledDiscoveryJobs().catch(() => undefined);
    }
  }, 5_000);
  window.addEventListener("online", () => {
    hydrateCloudState(true).catch(() => undefined);
  });
  window.setInterval(() => {
    if (!cloudStateReady && navigator.onLine) {
      hydrateCloudState(true).catch(() => undefined);
    }
  }, 30_000);
  updateFinderKeywordsFromForm();
  updateSocialProspectingQueries();
  loadDiscoverySourceStatus();
  importSocialCaptures();
  setInterval(importSocialCaptures, 4_000);
  showRequestedSection();
  window.addEventListener("hashchange", showRequestedSection);
  $$("#logoutButton").forEach((logoutButton) => {
    logoutButton.addEventListener("click", async () => {
      logoutButton.disabled = true;
      try {
        await fetch("/api/logout", { method: "POST" });
      } finally {
        window.location.replace("/login.html");
      }
    });
  });
}

init();
