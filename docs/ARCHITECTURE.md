# Porch 架构说明

## 1. 一句话架构

**单容器、双进程合一**：Go(Gin) 后端同时承担 API、WebSocket、静态文件服务；Vue 3 前端构建成静态资源后
放进镜像同一目录，由后端直接对外提供。**没有数据库**，所有状态写入 `server/data/*.json`。

```
                    ┌──────────────────────── 单个 Docker 容器 ────────────────────────┐
浏览器  ──HTTP──▶   │  Gin Router                                                      │
        ──WS────▶   │   ├─ /                → server/public/index.html（SPA 入口）     │
                    │   ├─ /assets /icons   → 静态资源（前端构建产物 + 图标库）        │
                    │   ├─ /api/*           → REST（登录/配置/组件数据/文件传输/Docker）│
                    │   ├─ /socket.io/*     → Socket.IO（热榜/天气/RSS/备忘录/待办）     │
                    │   ├─ /ws              → 原生 WebSocket（配置广播、在线状态）      │
                    │   └─ /proxy?url=      → 出站代理（SSRF 防护 + 可选上游代理）      │
                    │                                                                  │
                    │  数据层：server/data/data.json + users/ + config_versions/        │
                    └──────────────────────────────────────────────────────────────────┘
                              │                          │
                     /var/run/docker.sock          (可选) PROXY_URL 上游代理
                              ▼                          ▼
                     宿主机 Docker 守护进程         外网 / RSS / 热榜 / 壁纸 API
```

## 2. 技术栈

### 前端

| 类别 | 选型 | 用途 |
| --- | --- | --- |
| 框架 | Vue 3.5（`<script setup>` + TypeScript） | 全部 UI |
| 构建 | Vite 7 + `@vitejs/plugin-vue` | 开发服务器 / 生产打包 |
| 样式 | Tailwind CSS 4（`@tailwindcss/postcss`）+ 原生 CSS 变量 | 主题、卡片、暗色适配 |
| 状态 | Pinia 3（`stores/` 下 10 个 store） | 配置、组件、分组、认证、网络、同步、缓存 |
| 网格 | `grid-layout-plus` | 可拖拽/可缩放的组件网格 |
| 拖拽排序 | `vue-draggable-plus` | 分组、书签、待办排序 |
| 实时 | `socket.io-client` + 原生 `WebSocket` | 多端同步、组件数据推送 |
| 国际化 | `vue-i18n` 10，7 套 locale | 简中/繁中/英/日/德/法/西 |
| 工具 | `@vueuse/core`、`axios`、`fuse.js`、`dompurify`、`pako`、`xlsx`、`prismjs`、`lunar-javascript` | 组合式工具、请求、图标模糊搜索、HTML 净化、压缩、表格导入导出、代码高亮、农历 |
| 图标 | `frontend/public/icons`（约 1000+ PNG，构建时整目录复制） | 书签图标库 |

### 后端

| 类别 | 选型 | 用途 |
| --- | --- | --- |
| 语言 | Go 1.25 | 单二进制，静态编译 `CGO_ENABLED=0` |
| Web 框架 | Gin 1.11 + `gin-contrib/gzip` + `gin-contrib/cors` | 路由、压缩、跨域 |
| 实时 | `googollee/go-socket.io` 1.7 + `gorilla/websocket` | 双通道推送 |
| 认证 | `golang-jwt/jwt/v5`（HS256）+ `x/crypto/bcrypt` | 登录态、密码哈希 |
| 容器 | `docker/docker` SDK 25 | 容器列表/启停/升级/日志 |
| 监控 | `shirou/gopsutil/v3` | CPU/内存/磁盘/网络 |
| 图片 | `deepteams/webp`、`x/image` | 缩略图与 WebP 转码 |
| 其他 | `google/uuid`、`x/time`（限流）、`x/net` | ID、速率限制 |

### 运行与交付

| 项 | 说明 |
| --- | --- |
| 镜像 | 三阶段：`node:20.19-bookworm-slim` → `golang:alpine` → `alpine:latest` |
| 基础镜像体积 | 运行时仅 alpine + tzdata + ca-certificates，镜像约 120 MB |
| 端口 | 容器 `3000`（`PORT` 可改） |
| 架构 | `linux/amd64`、`linux/arm64`（可选 `arm/v7`） |
| 健康检查 | `GET /api/system-config` |
| CI | GitHub Actions → GHCR，`GITHUB_TOKEN`，buildx + gha 缓存 |

## 3. 目录结构

```
Porch/
├── backend/                        Go 后端
│   ├── main.go                     路由注册、静态文件、WS/Socket.IO 挂载、BASE_PATH 处理
│   ├── config/
│   │   ├── config.go               路径解析（BASE_DIR/server/*）、首启初始化、JWT 密钥生成
│   │   └── default.json            默认仪表盘模板（go:embed 进二进制）
│   ├── handlers/                   auth / data / docker / system / weather / rss / hot /
│   │                               music / memo / transfer / wallpaper / icons / proxy / versions /
│   │                               meta（书签抓标题/图标）、lucky_webhook（STUN 状态回调）
│   ├── middleware/                 认证、限流、恢复、gzip 解压
│   ├── models/models.go            数据结构定义
│   ├── utils/                      crypto（bcrypt/JWT）、通用工具
│   └── ws/                         WebSocket 管理器、事件广播、连接鉴权
│
├── frontend/                       Vue 前端
│   ├── src/
│   │   ├── App.vue                 全局壳：自定义 CSS/JS 注入、冲突弹窗、回顶、状态监控
│   │   ├── components/
│   │   │   ├── GridPanel.vue       主界面（标题 + 搜索 + 网格 + 分组），最大的单文件
│   │   │   ├── AppSidebar.vue      侧边栏（书签树 / 分组列表）
│   │   │   ├── SettingsModal.vue   设置中心（外观/壁纸/组件/网络/安全/自定义）
│   │   │   ├── EditModal.vue       书签/分组编辑弹窗
│   │   │   ├─┬ ClockWidget / ClockWeatherWidget / SimpleWeatherWidget / AmapWeatherWidget
│   │   │     ├─ CalendarWidget / MemoWidget / TodoWidget / RssWidget / HotWidget
│   │   │     ├─ BookmarkWidget / MusicWidget / MiniPlayer / FileTransferWidget
│   │   │     ├─ DockerWidget / SystemStatusWidget / StatusMonitor / IframeWidget
│   │   │     └─ CalculatorWidget / CountdownWidget / CountUpWidget / CustomCssWidget
│   │   ├── stores/                 main（总装）、config、groups、widgets、auth、network、
│   │   │                           sync（版本冲突）、save（防抖落盘）、cache、i18n
│   │   ├── composables/            useDevice / useWeather / useWallpaperRotation / useSmartIconMatch
│   │   ├── utils/                  gridLayout（布局换算）、network（内外网判定）、crypto、
│   │   │                           chunkedUploader（断点续传）、offlineQueue、security（净化）
│   │   ├── locales/                zh-CN / zh-TW / en-US / ja-JP / de-DE / fr-FR / es-ES
│   │   ├── assets/                 基础样式、城市数据、Logo
│   │   └── types.ts                NavItem / NavGroup / AppConfig / WidgetConfig 等类型
│   ├── public/                     静态素材源目录（图标库、默认壁纸、favicon）→ 构建时整目录复制
│   ├── package.json
│   └── vite.config.ts              base="./"、dev 代理、outDir 二选一（见 §7）
│
├── server/                         运行期数据（镜像内路径，全部建议挂载持久化）
│   ├── data/                       data.json / system.json / users/ / config_versions/ / icon-cache/
│   ├── music/  PC/  APP/  doc/     音乐、桌面壁纸、移动壁纸、文件传输落盘
│   └── public/                     构建产物落点（镜像内生成，不入库）
│
├── unraid/                         porch.xml（CA 模板）+ 图标
├── docs/                           DEPLOY.md / ARCHITECTURE.md / README_UPSTREAM.md
├── Dockerfile                      docker-compose.yml / docker-compose.unraid.yml
├── Makefile                        build / multiarch / up / logs / test-frontend
└── .github/workflows/              docker-publish.yml（GHCR 多架构）
```

## 4. 数据模型

全部状态是**普通 JSON 文件**，可直接编辑、可 git diff、可整包迁移。

### `server/data/data.json`（核心，单用户模式）

```jsonc
{
  "version": 166,                 // 配置版本号，每次保存自增；多端同步据此判断冲突
  "authMode": "single",           // single | multi（multi 时用户存 users/）
  "enableDocker": true,           // 是否启用 Docker 管理组件
  "appConfig": {                  // 81 个字段：外观、布局、搜索、天气、壁纸、自定义 CSS/JS…
    "customTitle": "我的导航",
    "titleAlign": "left",
    "cardLayout": "vertical",
    "cardSize": 110,
    "gridGap": 12,
    "iconShape": "rounded",
    "background": "...",
    "searchEngines": [{ "id": "...", "key": "bing", "label": "Bing", "urlTemplate": "..." }],
    "defaultSearchEngine": "bing",
    "sidebarViewMode": "bookmarks",
    "locale": "zh-CN",
    "customCss": "", "customJs": "", "customJsList": []
  },
  "groups": [                     // 分组 → 书签项
    {
      "id": "…", "title": "常用", "iconShape": "rounded", "cardLayout": "vertical",
      "cardSize": 110, "gridGap": 12, "isPublic": true,
      "items": [
        { "id": "…", "title": "GitHub", "url": "https://github.com",
          "lanUrl": "http://192.168.1.10:3000", "icon": "icons/github.png",
          "color": "#0d1117", "isPublic": true }
      ]
    }
  ],
  "widgets": [                    // 网格组件；x/y/w/h + layouts 三套断点
    { "id": "…", "type": "clockweather", "enable": true, "isPublic": true,
      "x": 0, "y": 0, "w": 3, "h": 2,
      "layouts": { "desktop": {...}, "tablet": {...}, "mobile": {...} },
      "data": { } }
  ],
  "rssFeeds": [], "rssCategories": []
}
```

组件 `type` 取值：`clock` `clockweather` `weather` `calendar` `memo` `todo` `rss` `hot`
`bookmarks` `player` `music` `file-transfer` `docker` `system-status` `status-monitor`
`iframe` `calculator` `countdown` `countup` `custom-css` `div-card` `search` `sidebar` `ip` `quote`。

### 其他数据文件

| 文件 | 内容 |
| --- | --- |
| `system.json` | `{ authMode, enableDocker }`，系统级开关 |
| `default.json` | 默认模板副本（重置用；首次启动自 `go:embed` 写入） |
| `secret.key` | JWT 签名密钥（32 字节 hex）。删除会让所有登录态失效 |
| `users/*.json` | 多用户模式的用户记录（bcrypt 哈希） |
| `visitors.json` / `amap_stats.json` | 页脚访客统计、高德调用计数 |
| `custom_scripts.json` / `widget_cache.json` / `asset_meta.json` | 自定义脚本、组件缓存、媒体元信息 |
| `config_versions/*.json` | 配置快照，用于回滚 |
| `icon-cache/` | 远程图标缓存 |

## 5. API 与实时通道

### REST（`/api`，`*` 需登录）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/login` `/register` | 登录（返回 JWT）/ 注册（多用户模式） |
| GET | `/data`* | 拉取整包配置 |
| POST | `/save`* | 保存整包配置（版本号自增，冲突返回 409） |
| PUT | `/widgets/:id`* / POST `/widgets/batch`* | 细粒度组件保存 / 批量拉取 |
| GET | `/version` `/system-config` `/ip` | 版本、系统开关（健康检查用）、客户端 IP |
| GET | `/hot` `/weather` `/rss` `/rss/meta` | 热榜、天气、RSS（服务端抓取，规避跨域） |
| GET/PUT | `/memo/:id` | 备忘录 |
| GET/POST | `/docker/containers` `/docker/container/:id/:action`* | 容器列表、启停/重启/升级 |
| GET | `/system/stats`* | 宿主机 CPU/内存/磁盘/网络 |
| GET/POST | `/transfer/*`* | 文件传输：分片初始化/上传/合并/断点续传状态 |
| GET/POST | `/backgrounds/*` `/music/*` | 壁纸、音乐的上传与删除 |
| GET/POST | `/config-versions*` | 配置快照列表 / 保存 / 恢复 / 删除 |
| GET | `/fetch-meta?url=` | 抓取目标网页的 `<title>` 与 favicon（添加书签时自动填充） |
| POST | `/webhook/lucky/stun` | 接收 Lucky STUN 穿透状态回调（**匿名**，Lucky 不带 JWT），广播 `lucky:stun` |
| GET | `/webhook/lucky/stun` | 最近一次 STUN 快照，供设置面板「刷新数据」拉取 |
| ANY | `/proxy?url=` | 出站代理，带 SSRF 校验 |

### 实时

- **Socket.IO**（`/socket.io`）：`hot` `weather` `rss` `memo` `todo` `network` 事件；连接时用 `?token=` 鉴权
- **原生 WebSocket**（`/ws`）：配置变更广播、在线状态、其它端保存后的推送、`lucky:stun`（STUN 穿透状态）
- WebSocket 连接先建立，再发 `{"type":"auth","payload":{"token":"<JWT>"}}` 完成鉴权；广播只发给已鉴权连接

### 保存与冲突

前端每次改动走 `stores/save.ts` 防抖合并 → `POST /api/save` 携带本地 `version`。
服务端版本号不一致时返回 409，前端弹「版本冲突」框，让用户选择 **采用服务端** 或 **强制本端覆盖**；
心跳恢复时若发现服务端版本变了，另弹「服务端配置已更新，是否同步」提示。

## 6. 认证与权限

- 密码存储：`bcrypt`（cost 10）
- 登录态：JWT HS256，签名密钥来自 `secret.key`；请求头 `Authorization: Bearer <token>`（也接受 `?token=`）
- 单用户模式：账号固定 `admin`，首次登录密码 `admin`，首次成功登录后写入 `data.json`
- 多用户模式：用户存 `users/`，`admin` 为超管，可增删用户；书签/组件带 `isPublic` 控制游客可见性
- 游客：未登录时只能看到 `isPublic: true` 的内容

## 7. 构建流程

```
npm ci → vite build-only → dist/
        ↑ VITE_DOCKER_BUILD=1 时 outDir=dist
          Windows 本地开发默认 outDir=../server/public（直接给 go run 用）
go mod download → go build -trimpath -ldflags="-s -w" -o porch-backend
        ↓
alpine + tzdata + ca-certificates + wget
   /app/porch-backend
   /app/server/public ← dist（HTML + assets + icons）
   /app/server/{data,music,PC,APP,doc}
```

`vite.config.ts` 里 `base: "./"`（可用 `VITE_APP_BASE_PATH` 覆盖），所以子路径反代不会把资源写死到站点根。

## 8. 环境变量

### 运行期

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `PORT` | `3000` | 监听端口 |
| `HOST` | `0.0.0.0` | 监听地址 |
| `BASE_DIR` | `/app` | 数据根，决定 `server/data` 等路径（镜像内已设） |
| `BASE_PATH` | 空 | 子路径部署前缀，如 `/porch` |
| `PROXY_URL` | 空 | 出站代理，`http/https/socks5/socks5h://[user:pass@]host:port` |
| `CORS_ALLOW_ORIGINS` | 空（全放行） | 逗号分隔白名单，前后端分离部署时收紧 |
| `TZ` | `Asia/Shanghai` | 时区 |
| `GIN_MODE` | `release` | Gin 运行模式 |

### 构建期（`--build-arg`）

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `VERSION` | `1.2.6` | 写入镜像 label |
| `REVISION` | `unknown` | git sha |
| `NPM_REGISTRY` | `https://registry.npmjs.org` | 国内可换 `https://registry.npmmirror.com` |
| `GOPROXY` | `https://proxy.golang.org,direct` | 国内可换 `https://goproxy.cn,direct` |
| `HTTP_PROXY` / `HTTPS_PROXY` | 空 | 构建期代理 |

## 9. 扩展点

| 扩展 | 位置 | 说明 |
| --- | --- | --- |
| 自定义 CSS | 设置 → 自定义 CSS | 支持 `<mobile>` `<desktop>` `<dark>` `<light>` 自动转媒体查询 |
| 自定义 JS | 设置 → 自定义 JS | 沙箱执行，`ctx` 提供 `store`（只读）、`query`、`widgetEl`、`fetch`（自动走代理）、`on/emit`、`onCleanup`；支持 `init/update/destroy` 生命周期 |
| 自定义 HTML 组件 | 添加组件 → 自定义 | 内容经 DOMPurify 净化 |
| iframe 组件 | 添加组件 → iframe | 嵌入外部页面，可开代理 |
| 图标 | 编辑书签 → 图标库/上传 | 支持颜色 `#hex` 背景与多种形状 |

## 10. 资源占用

- 镜像 ~120 MB；后端常驻内存约 40–100 MB（视组件数量与缓存）
- 前端首屏产物 gzip 后约 220 KB（主包）+ 懒加载组件分包（日历 104 KB、设置面板 41 KB…）
- 图标库与壁纸走强缓存（`max-age=604800`），`index.html` 明确 `no-store`
