# 前端模块化拆分说明

这次重构只做**搬家**，不改功能：界面、交互、样式、DOM 结构全部保持原样。
目的只有一个 —— 让 `SettingsModal.vue` 这种五千行的巨型单文件变成"一个壳 + 每个标签页一个文件"，
方便你自己改。

## 前后对比

| 文件 | 拆分前 | 拆分后 |
| --- | --- | --- |
| `components/SettingsModal.vue` | 5053 行（脚本 1842 + 模板 3135 + 样式 73） | **2379 行**（壳、标签导航、两个确认弹窗） |
| `components/settings/StylePanel.vue` | — | 457 行（外观布局） |
| `components/settings/WidgetsPanel.vue` | — | 426 行（单开组件） |
| `components/settings/DockerPanel.vue` | — | 381 行（Docker 管理） |
| `components/settings/UniversalWindowPanel.vue` | — | 499 行（多开组件） |
| `components/settings/NetworkPanel.vue` | — | 131 行（网络判定） |
| `components/settings/LuckyStunPanel.vue` | — | 654 行（开放中心） |
| `components/settings/AccountPanel.vue` | — | 341 行（账户管理） |
| `components/settings/AboutPanel.vue` | — | 189 行（关于） |
| `components/settings/LanguagePanel.vue` | — | 59 行（语言） |
| `components/settings/context.ts` | — | 19 行（共享上下文 key） |

## 状态怎么传：provide + toRef

9 个面板加起来要用父组件里 114 个 ref / computed / 函数。用 props 层层透传会写上百个属性，
所以父组件在 setup 末尾统一 provide：

```ts
// SettingsModal.vue
provide(SETTINGS_CTX, reactive({ appConfig, store, showWallpaperLibrary, ... }));
```

子面板按需取自己用到的字段，并且**必须用 `toRef` 而不是解构**：

```ts
const ctx = inject(SETTINGS_CTX) as Record<string, any>;
const appConfig = toRef(ctx, "appConfig");   // ✅ 保持响应性，v-model 可写
// const { appConfig } = ctx;                 // ❌ 会定格成当时的值，且赋值丢失
```

原因：`reactive()` 会把 ref 解包，直接解构拿到的是"当时的快照"；`toRef` 的读取会追踪依赖、
写入会回写到原来的 ref，所以模板里的 `v-model="x"` 依旧能双向写回父组件状态。

## 样式为什么拆成两块

父组件原来的 `<style scoped>` 里有两类规则：

- `.night-settings :deep(...)` —— `:deep()` 会穿透到子组件内部，拆完仍然生效，保留在 scoped 块
- `.glass-panel` / `.glass-card` / `.selected-outline` 等普通类名 —— 编译后会带上父组件的
  `data-v-xxx`，搬到子组件后这些元素不再匹配，玻璃质感会直接丢失

所以第二类被移到同一文件里的**非 scoped** `<style>` 块。这些类名全仓库只有设置面板在用
（`grep -rl glass-panel` 只命中 SettingsModal），提到全局不会污染别处。

## 想改某个设置项时

1. 只改外观/壁纸 → `components/settings/StylePanel.vue`
2. 加一个新开关 → 在面板模板里加控件，绑定父级已有的字段；
   若要用新状态，就在 `SettingsModal.vue` 里加 ref，再把它加进 `provide` 的对象里
3. 改标签页名字/顺序 → `SettingsModal.vue` 的 `<nav>` 与 `locales/*/settings.json` 的 `tabs`

## 怎么验证没改坏（本机无 Go 环境时）

仓库自带两个开发工具：

```bash
# 1) 用 mock 后端把 dist 当静态站点跑起来（API 返回 backend/config/default.json）
cd frontend && VITE_DOCKER_BUILD=1 npm run build-only && cd ..
python tools/mock_server.py --port 23100

# 2) 抓界面截图（用系统 Edge，无需下载浏览器）
node tools/shots.mjs shots-before http://127.0.0.1:23100
# 改完代码重新 build，再抓一次到 shots-after，逐张对比
```

`tools/split_settings.py` 是这次拆分的生成脚本（含边界自检），`tools/scan_settings.py` 统计
每个面板引用的父级绑定，`tools/check_panels.mjs` 用编译器反查"面板里还没声明就直接用了的标识符"。
改完面板后跑一下 `node tools/check_panels.mjs frontend/src/components/settings`，
输出里除了 `$t` 之外不应该有别的名字。
