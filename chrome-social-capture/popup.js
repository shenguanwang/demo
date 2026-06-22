const statusEl = document.querySelector("#status");
const previewEl = document.querySelector("#preview");
const captureButton = document.querySelector("#captureButton");

function pageExtractor() {
  const text = String(document.body?.innerText || "").slice(0, 100000);
  const anchors = Array.from(document.querySelectorAll("a[href]")).slice(0, 500);
  const links = anchors.map((anchor) => ({
    url: anchor.href,
    text: String(anchor.innerText || anchor.getAttribute("aria-label") || "").trim()
  })).filter((item) => /^https?:\/\//i.test(item.url));
  const emailValues = [
    ...(text.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi) || []),
    ...anchors
      .map((anchor) => anchor.href)
      .filter((href) => /^mailto:/i.test(href))
      .map((href) => decodeURIComponent(href.replace(/^mailto:/i, "").split("?")[0]))
  ];
  const phoneValues = [
    ...(text.match(/(?:\+?\d[\d\s().-]{7,}\d)/g) || []),
    ...anchors
      .map((anchor) => anchor.href)
      .filter((href) => /^(?:tel:|https?:\/\/(?:wa\.me|api\.whatsapp\.com))/i.test(href))
  ];
  const hostname = location.hostname.toLowerCase();
  const platform = hostname.includes("youtube") ? "YouTube"
    : hostname.includes("facebook") ? "Facebook"
    : hostname.includes("instagram") ? "Instagram"
    : hostname.includes("tiktok") ? "TikTok"
    : hostname.includes("linkedin") ? "LinkedIn"
    : "公开网页";
  const title = document.querySelector("h1")?.innerText
    || document.querySelector('meta[property="og:title"]')?.content
    || document.title;
  return {
    platform,
    title: String(title || "").trim(),
    url: location.href,
    text,
    links,
    emails: [...new Set(emailValues.map((value) => value.trim().toLowerCase()))],
    phones: [...new Set(phoneValues.map((value) => value.trim()))],
    capturedAt: new Date().toISOString()
  };
}

async function getActiveTab() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tabs.length) throw new Error("没有找到当前标签页");
  return tabs[0];
}

async function inspectPage(tab) {
  const result = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: pageExtractor
  });
  return result[0]?.result;
}

async function updatePreview() {
  try {
    const tab = await getActiveTab();
    previewEl.innerHTML = `<strong>${tab.title || "当前页面"}</strong><span>${tab.url || ""}</span>`;
  } catch (error) {
    statusEl.textContent = error.message;
    statusEl.className = "status error";
  }
}

captureButton.addEventListener("click", async () => {
  captureButton.disabled = true;
  statusEl.className = "status";
  statusEl.textContent = "正在读取当前可见页面…";
  try {
    const tab = await getActiveTab();
    if (!/^https?:/i.test(tab.url || "")) throw new Error("当前页面不支持采集");
    const payload = await inspectPage(tab);
    if (!payload) throw new Error("未读取到页面内容");
    try {
      payload.screenshotData = await chrome.tabs.captureVisibleTab(tab.windowId, { format: "png" });
    } catch {
      payload.screenshotData = "";
    }
    statusEl.textContent = `已识别 ${payload.emails.length} 个邮箱、${payload.links.length} 个链接，正在发送…`;
    const response = await fetch("http://127.0.0.1:8815/api/social-capture", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    statusEl.textContent = `采集成功：${payload.emails.length} 个邮箱，已发送到工作台待审核。`;
    statusEl.className = "status success";
  } catch (error) {
    statusEl.textContent = `采集失败：${error.message}。请确认工作台服务已启动。`;
    statusEl.className = "status error";
  } finally {
    captureButton.disabled = false;
  }
});

updatePreview();
