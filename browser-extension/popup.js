const $ = (id) => document.getElementById(id);

const send = (message) =>
  new Promise((resolve) => {
    chrome.runtime.sendMessage(message, (response) => resolve(response || { ok: false }));
  });

const showResult = (message, error = false) => {
  const el = $("result");
  el.textContent = message || "";
  el.className = error ? "error" : "";
};

const render = (state) => {
  $("dot").className = state.paired ? "dot on" : "dot";
  $("status").textContent = state.paired ? "已连接" : "未配对";
  $("origin").textContent = state.paired ? state.origin : "未配对，请先打开 Porch 设置生成握手链接";
  $("add").disabled = !state.paired;
  $("open").disabled = !state.paired;
  $("iframeRule").checked = Boolean(state.iframeRuleEnabled);
};

const load = async () => {
  const response = await send({ type: "PORCH_GET_STATE" });
  render(response.state || {});
};

document.addEventListener("DOMContentLoaded", () => {
  load();

  $("add").addEventListener("click", async () => {
    showResult("正在收藏…");
    const response = await send({ type: "PORCH_QUICK_ADD" });
    if (response.ok) showResult(response.message || "已收藏");
    else showResult(response.error || "收藏失败", true);
  });

  $("open").addEventListener("click", async () => {
    const response = await send({ type: "PORCH_GET_STATE" });
    if (response.state?.origin) {
      chrome.tabs.create({ url: response.state.origin });
      window.close();
    }
  });

  $("iframeRule").addEventListener("change", async (event) => {
    const enabled = event.target.checked;
    const response = await send({ type: "PORCH_TOGGLE_IFRAME_RULE", enabled });
    if (!response.ok) {
      event.target.checked = !enabled;
      showResult(response.error || "规则更新失败", true);
    } else {
      showResult(enabled ? "已启用 iframe 解除限制" : "已关闭 iframe 解除限制");
    }
  });
});
