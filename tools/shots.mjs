// 用 Playwright(msedge) 抓界面截图，用于重构前后比对
// 用法：node tools/shots.mjs <outDir> [baseUrl]
import { createRequire } from "node:module";
import { mkdirSync } from "node:fs";

// 依赖装在 frontend/node_modules，脚本在 tools/ 下，需按仓库相对路径解析
const require = createRequire(new URL("../frontend/package.json", import.meta.url));
const { chromium } = require("@playwright/test");

const outDir = process.argv[2] || "shots";
const base = process.argv[3] || "http://127.0.0.1:23100";
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ channel: "msedge" });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
page.on("pageerror", (e) => console.log("PAGEERROR:", e.message.slice(0, 200)));

// 免登录：直接写入 token，跳过登录框（mock 后端不校验）
await page.addInitScript(() => {
  localStorage.setItem("flat-nas-token", "mock-token");
  localStorage.setItem("flat-nas-username", "admin");
});

const shot = async (name) => {
  await page.waitForTimeout(650);
  await page.screenshot({ path: `${outDir}/${name}.png` });
  console.log("shot", name);
};

const clickVisible = (predicateSource) =>
  page.evaluate((src) => {
    const visible = (el) => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
    const fn = new Function("el", `return (${src})(el);`);
    const hit = [...document.querySelectorAll("button, a, [role='tab'], li, div, span")].find(
      (el) => visible(el) && fn(el),
    );
    if (hit) { hit.click(); return true; }
    return false;
  }, predicateSource);

await page.goto(base, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(3000);
await shot("01-home");

const openSettings = () =>
  clickVisible(
    `(el) => el.tagName === 'BUTTON' && !!el.querySelector("svg path[d^='M11.078']")`,
  );

// 未登录点齿轮会弹登录框：填 admin 登录
if (await openSettings()) {
  await page.waitForTimeout(800);
  const needLogin = await page.evaluate(() => !!document.querySelector("input[type='password']"));
  if (needLogin) {
    await page.fill("input[type='password']", "admin");
    await page.waitForTimeout(200);
    await clickVisible(`(el) => (el.textContent || '').trim() === '登录'`);
    await page.waitForTimeout(1500);
    await shot("02b-after-login");
    await openSettings();
  }
}
await shot("02-settings-open");

const tabs = {
  style: "外观",
  widgets: "组件",
  docker: "Docker",
  "universal-window": "多开组件",
  network: "网络",
  "lucky-stun": "开放中心",
  account: "账户",
  about: "关于",
  language: "语言",
};
for (const [key, label] of Object.entries(tabs)) {
  const ok = await clickVisible(
    `(el) => { const t = (el.textContent || '').trim(); return t.length > 0 && t.length <= 12 && t.includes(${JSON.stringify(label)}); }`,
  );
  if (!ok) { console.log("tab not found:", key, label); continue; }
  await shot(`03-tab-${key}`);
}

await browser.close();
console.log("done ->", outDir);
