// 在 Porch 设置页读取握手链接。保留旧属性名以兼容原项目插件协议。
(function () {
  const findHandshakeUrl = () => {
    const candidates = Array.from(
      document.querySelectorAll('a[data-flatnas-helper-link], a[href*="flatnas-helper-handshake"]'),
    );
    for (const el of candidates) {
      const href = el.href || el.getAttribute("href") || "";
      if (href.includes("flatnas-helper-handshake")) return href;
    }
    if (window.location.hash.includes("flatnas-helper-handshake")) {
      return window.location.href;
    }
    return null;
  };

  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message?.type === "PORCH_SCAN_HANDSHAKE") {
      sendResponse({ url: findHandshakeUrl() });
    }
  });

  const found = findHandshakeUrl();
  if (found) {
    chrome.runtime.sendMessage({ type: "PORCH_HANDSHAKE_URL", url: found }).catch(() => {});
  }
})();
