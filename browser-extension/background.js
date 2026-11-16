// Porch 浏览器助手后台。
// 保留 flatnas-helper-handshake / flat-nas-token 协议名以兼容原项目插件：
// 这些字符串只用于本机扩展通信，不作为界面文案。

const CONFIG_KEY = "porchHelperConfig";
const RULE_ID = 1;

const authHeaders = (token) => {
  const raw = String(token || "").trim();
  return {
    Authorization: raw.toLowerCase().startsWith("bearer ") ? raw : `Bearer ${raw}`,
    "Content-Type": "application/json",
  };
};

const normalizeOrigin = (value) => {
  try {
    const u = new URL(String(value || ""));
    if (!/^https?:$/.test(u.protocol)) return "";
    return u.origin;
  } catch {
    return "";
  }
};

const parseHandshakeUrl = (raw) => {
  try {
    const u = new URL(String(raw || ""));
    const params = new URLSearchParams(u.hash.replace(/^#/, ""));
    if (params.get("flatnas-helper-handshake") !== "1") return null;
    const origin = normalizeOrigin(params.get("origin") || u.origin);
    const token = (params.get("token") || "").trim();
    if (!origin || !token) return null;
    return {
      origin,
      token,
      source: params.get("source") || "",
      savedAt: Date.now(),
    };
  } catch {
    return null;
  }
};

const getConfig = async () => {
  const stored = await chrome.storage.local.get(CONFIG_KEY);
  return stored[CONFIG_KEY] || null;
};

const saveConfig = async (config) => {
  await chrome.storage.local.set({ [CONFIG_KEY]: config });
  return config;
};

const currentTab = async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab || null;
};

const scanPageForHandshake = async (tab) => {
  if (!tab || !tab.id || !/^https?:/.test(tab.url || "")) return null;
  try {
    const response = await chrome.tabs.sendMessage(tab.id, { type: "PORCH_SCAN_HANDSHAKE" });
    if (response && response.url) return parseHandshakeUrl(response.url);
  } catch {
    // 扩展页、浏览器内部页或权限受限页面会抛错，忽略即可。
  }
  return null;
};

const pairWithTab = async (tab) => {
  let config = tab ? parseHandshakeUrl(tab.url) : null;
  if (!config) config = await scanPageForHandshake(tab);
  if (!config) return null;
  return saveConfig(config);
};

const fetchJson = async (url, options = {}, timeoutMs = 10000) => {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal, cache: "no-store" });
    let body = null;
    try {
      body = await res.json();
    } catch {
      body = null;
    }
    return { ok: res.ok, status: res.status, body };
  } catch (error) {
    return { ok: false, status: 0, body: null, error };
  } finally {
    clearTimeout(timer);
  }
};

const fetchBookmarkMeta = async (config, url, tab) => {
  const endpoint = `${config.origin}/api/fetch-meta?url=${encodeURIComponent(url)}`;
  const result = await fetchJson(endpoint, { headers: authHeaders(config.token) }, 8000);
  const meta = result.ok && result.body ? result.body : {};
  return {
    title: String(meta.title || tab?.title || url).trim() || url,
    icon:
      meta.icon ||
      tab?.favIconUrl ||
      `https://www.favicon.vip/get.php?url=${encodeURIComponent(url)}`,
  };
};

const normalizeBookmarkUrl = (url) => {
  try {
    return new URL(url).href;
  } catch {
    return String(url || "");
  }
};

const addBookmarkOnce = async (config, tab, retry = false) => {
  const pageUrl = normalizeBookmarkUrl(tab.url);
  const dataResult = await fetchJson(`${config.origin}/api/data`, {
    headers: authHeaders(config.token),
  });
  if (!dataResult.ok || !dataResult.body) {
    throw new Error(`读取 Porch 数据失败 (${dataResult.status || "network"})`);
  }

  const data = dataResult.body;
  const widget = (Array.isArray(data.widgets) ? data.widgets : []).find(
    (w) => w && w.type === "bookmarks",
  );
  if (!widget) throw new Error("Porch 中没有收藏夹组件");

  const categories = Array.isArray(widget.data) ? widget.data : [];
  const targetUrl = normalizeBookmarkUrl(pageUrl);
  const exists = categories.some((cat) =>
    (Array.isArray(cat?.children) ? cat.children : []).some(
      (item) => item && normalizeBookmarkUrl(item.url) === targetUrl,
    ),
  );
  if (exists) return "这个页面已经在 Porch 收藏夹里了";

  const meta = await fetchBookmarkMeta(config, pageUrl, tab);
  let category = categories.find((cat) => cat && Array.isArray(cat.children));
  if (!category) {
    category = {
      id: `${Date.now()}_default`,
      title: "默认收藏",
      collapsed: false,
      children: [],
    };
    categories.push(category);
  }

  const item = {
    id: `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`,
    title: meta.title,
    url: pageUrl,
    icon: meta.icon,
  };
  category.children.push(item);

  const version = Number(data.version) || 0;
  const saveResult = await fetchJson(
    `${config.origin}/api/widgets/${encodeURIComponent(widget.id)}`,
    {
      method: "PUT",
      headers: authHeaders(config.token),
      body: JSON.stringify({
        data: categories,
        enable: widget.enable !== false,
        version,
      }),
    },
  );

  if (saveResult.status === 409 && !retry) return addBookmarkOnce(config, tab, true);
  if (!saveResult.ok) {
    throw new Error(`保存到 Porch 失败 (${saveResult.status || "network"})`);
  }
  return `已收藏：${meta.title}`;
};

const quickAdd = async () => {
  const config = await getConfig();
  if (!config?.origin || !config?.token) {
    throw new Error("尚未配对。请先在 Porch 设置里复制握手链接，再点插件图标。");
  }
  const tab = await currentTab();
  if (!tab || !/^https?:/.test(tab.url || "")) {
    throw new Error("当前页面无法收藏（仅支持 http/https 页面）");
  }
  return addBookmarkOnce(config, tab);
};

const getHeaderRuleEnabled = async () => {
  const rules = await chrome.declarativeNetRequest.getDynamicRules();
  return rules.some((rule) => rule.id === RULE_ID);
};

const setHeaderRule = async (enabled) => {
  const addRules = enabled
    ? [
        {
          id: RULE_ID,
          priority: 1,
          action: {
            type: "modifyHeaders",
            responseHeaders: [
              { header: "x-frame-options", operation: "remove" },
              { header: "content-security-policy", operation: "remove" },
              { header: "content-security-policy-report-only", operation: "remove" },
            ],
          },
          condition: {
            resourceTypes: ["sub_frame"],
          },
        },
      ]
    : [];
  await chrome.declarativeNetRequest.updateDynamicRules({
    removeRuleIds: [RULE_ID],
    addRules,
  });
  return enabled;
};

const getState = async () => {
  const config = await getConfig();
  return {
    paired: Boolean(config?.origin && config?.token),
    origin: config?.origin || "",
    savedAt: config?.savedAt || 0,
    iframeRuleEnabled: await getHeaderRuleEnabled(),
  };
};

chrome.runtime.onInstalled.addListener(async () => {
  const stored = await chrome.storage.local.get(CONFIG_KEY);
  if (stored[CONFIG_KEY] === undefined) {
    await chrome.storage.local.set({ [CONFIG_KEY]: null });
  }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url || changeInfo.status === "complete") {
    pairWithTab(tab).catch(() => {});
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const handle = async () => {
    switch (message?.type) {
      case "PORCH_HANDSHAKE_URL": {
        const config = parseHandshakeUrl(message.url);
        if (!config) return { ok: false, error: "握手链接无效" };
        await saveConfig(config);
        return { ok: true };
      }
      case "PORCH_SCAN_HANDSHAKE": {
        const config = await pairWithTab(await currentTab());
        return { ok: Boolean(config) };
      }
      case "PORCH_GET_STATE":
        return { ok: true, state: await getState() };
      case "PORCH_QUICK_ADD":
        try {
          return { ok: true, message: await quickAdd() };
        } catch (error) {
          return { ok: false, error: error?.message || String(error) };
        }
      case "PORCH_TOGGLE_IFRAME_RULE":
        return { ok: true, enabled: await setHeaderRule(Boolean(message.enabled)) };
      default:
        return { ok: false, error: "未知消息" };
    }
  };
  handle().then(sendResponse).catch((error) => {
    sendResponse({ ok: false, error: error?.message || String(error) });
  });
  return true;
});
