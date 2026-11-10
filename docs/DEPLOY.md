# Porch 部署手册（Docker / GHCR / Unraid）

面向本 Fork：从源码构建镜像 → 推到自己的 GitHub Container Registry → Unraid 直接拉取运行。

> 全文中 `mjy378283319` 指你的 GitHub 用户名/组织名。本仓库已统一使用占位符 `mjy378283319`，  
> 拿到账号后执行一次 `./scripts/set-owner.sh <你的GitHub用户名>` 即可批量替换。



---

## 0. 前置条件

| 项      | 要求                                          |
| ------ | ------------------------------------------- |
| Docker | 20.10+（buildx 支持）                           |
| Unraid | 6.10+（Compose Manager 插件可选）                 |
| 磁盘     | 镜像约 120 MB；数据目录按壁纸/音乐/传输文件实际占用              |
| 端口     | 容器内 3000，宿主默认映射 23000                       |
| 架构     | linux/amd64（主流 Unraid）、linux/arm64（ARM NAS） |

---

## 1. 仓库准备

```bash
git clone https://github.com/mjy378283319/Porch.git
cd Porch
./scripts/set-owner.sh mjy378283319
git commit -am "chore: set image owner to mjy378283319" && git push
```

`set-owner.sh` 会把以下文件里的 `mjy378283319` 换成你的账号：

- `docker-compose.yml`、`docker-compose.unraid.yml`、`.env.example`
- `unraid/porch.xml`（Repository / Registry / Icon / TemplateURL / Support / Project）

---

## 2. 构建镜像

### 2.1 本地单架构构建

```bash
docker build -t porch:1.2.6 --build-arg VERSION=1.2.6 .

# 或走 Makefile
make build            # 产出 ghcr.io/mjy378283319/porch:1.2.6 与 :latest
```

国内网络慢可加构建参数（构建期有效，不影响运行期）：

```bash
docker build \
  --build-arg NPM_REGISTRY=https://registry.npmmirror.com \
  --build-arg GOPROXY=https://goproxy.cn,direct \
  -t porch:1.2.6 .
```

### 2.2 多架构构建并推送 GHCR

```bash
# 1) 建 PAT：GitHub → Settings → Developer settings → Tokens(classic)，勾 write:packages + read:packages
echo <PAT> | docker login ghcr.io -u mjy378283319 --password-stdin

# 2) 创建 buildx 构建器（只需一次）
docker buildx create --name porch-builder --use
docker buildx inspect --bootstrap

# 3) 多架构构建并推送
docker buildx build --platform linux/amd64,linux/arm64 \
  --build-arg VERSION=1.2.6 \
  -t ghcr.io/mjy378283319/porch:1.2.6 \
  -t ghcr.io/mjy378283319/porch:latest \
  --push .

# 或 make multiarch OWNER=mjy378283319
```

推完在 GitHub → 你的头像 → `Your packages` 里能看到 `porch`。

### 2.3 用 GitHub Actions 自动构建（推荐）

`.github/workflows/docker-publish.yml` 已配好，推 `main` 或打 tag 即自动构建  
`linux/amd64,linux/arm64` 并推到 `ghcr.io/mjy378283319/<repo>`，用内置 `GITHUB_TOKEN`，无需额外 Secrets。

首次使用需确认两点：

1. **Actions 权限**：仓库 `Settings → Actions → General → Workflow permissions` 选  
   `Read and write permissions`（否则 `packages: write` 会被拒）。
2. **包可见性**：默认私有仓库产出的镜像也是私有。Unraid 拉取需登录（见 3.4）；  
   想公开则在 `Packages → porch → Package settings → Change visibility` 改为 Public。

打 tag 会自动产生语义化版本标签：

```bash
git tag v1.2.6 && git push origin v1.2.6
# → ghcr.io/mjy378283319/porch:1.2.6 / :1.2 / :latest
```

手动触发（可选自定义平台，例如给老 ARM NAS 加 `linux/arm/v7`）：

```
Actions → Build & Publish Image (GHCR) → Run workflow → platforms: linux/amd64,linux/arm64,linux/arm/v7
```

### 2.4 `git push` 不通时：走 GitHub API 推送

国内网络下 `git push` 常见 `schannel: failed to receive handshake` 或
`CONNECT tunnel failed, response 502`（git 端口被拦，但 `api.github.com` 正常）。
此时用仓库自带的 API 推送脚本，它按本地提交链逐条重建 tree/commit，**远端 sha 与本地完全一致**：

```bash
python scripts/api_push.py --pat <你的PAT文件> --repo <owner>/Porch --jobs 8
```

- 只上传远端缺失的 blob（按内容 sha 去重），增量推送通常几十秒
- 建 tree 后会校验返回的 tree sha 是否等于本地，`[ok]` 才继续
- 触发限流（403）时自动按 `Retry-After` 退避重试
- 首次推送会创建根提交；远端若只有一个初始化提交，会被本地链覆盖（`force`）

> PAT 权限：fine-grained 需勾 `Contents: Read and write`；
> 还要在 `Settings → Actions → General` 把 Workflow permissions 设为
> **Read and write**，否则 GHCR 推送会 403。
> 建仓库用 classic PAT（`repo` scope）或网页手动创建，fine-grained 令牌不一定有创建权限。

---

## 3. Unraid 部署

### 3.1 方式一：Unraid 模板（图形化，最省事）

1. 先确认 `unraid/porch.xml` 里的 `Repository` 是 `ghcr.io/mjy378283319/porch:latest`（跑过 `set-owner.sh` 即已正确）。
2. Unraid → `Docker` → `Add Container`，右上角 `Template` 输入框粘贴：
   ```
   https://raw.githubusercontent.com/mjy378283319/Porch/main/unraid/porch.xml
   ```
   私有仓库 raw 链接不可匿名访问时，改用方式二/三，或把该 XML 上传到  
   `/boot/config/plugins/dockerMan/templates-user/my-Porch.xml` 后在模板下拉里选 “Porch”。
3. 表单里已预置好：端口 `23000 → 3000`、5 个 appdata 路径、`TZ`，以及可选的 `BASE_PATH` / `PROXY_URL`  
   和 Docker Socket。确认路径后 `Apply`。
4. 浏览器打开 `http://<Unraid-IP>:23000`，用 `admin`/`admin` 登录并改密码。

### 3.2 方式二：Compose Manager（Stack）

Unraid 装 `Compose Manager` 插件 → `Compose` → `Add New Stack` → 名称 `porch` →  
把 `docker-compose.unraid.yml` 内容整段粘进去 → `Compose Up`。

目录规划（默认全部落在 appdata，Unraid 备份只认这一个目录）：

```
/mnt/user/appdata/porch/
├── data/     配置、用户、版本快照、图标缓存   ← 必备份
├── music/    音乐播放器音频
├── PC/       桌面壁纸
├── APP/      移动端壁纸
└── doc/      文件传输助手落盘
```

### 3.3 方式三：Docker UI 手动添加

| 字段           | 值                                                            |
| ------------ | ------------------------------------------------------------ |
| Name         | `porch`                                                    |
| Repository   | `ghcr.io/mjy378283319/porch:latest`                             |
| Network Type | `bridge`                                                     |
| Port         | `23000` / 容器端口 `3000` / TCP                                  |
| Path 1       | `/mnt/user/appdata/porch/data` → `/app/server/data` (rw)   |
| Path 2       | `/mnt/user/appdata/porch/music` → `/app/server/music` (rw) |
| Path 3       | `/mnt/user/appdata/porch/PC` → `/app/server/PC` (rw)       |
| Path 4       | `/mnt/user/appdata/porch/APP` → `/app/server/APP` (rw)     |
| Path 5       | `/mnt/user/appdata/porch/doc` → `/app/server/doc` (rw)     |
| Path 6（可选）   | `/var/run/docker.sock` → `/var/run/docker.sock` (rw)         |
| Variable     | `TZ` = `Asia/Shanghai`                                       |

> 只有挂了 `docker.sock` 并且进设置里开启 “Docker 管理”，容器管理组件才可用。  
> 该挂载等价于把宿主 Docker 控制权交给容器，属高危权限，不需要就别挂。

### 3.4 拉私有 GHCR 镜像

Unraid 终端执行一次（凭据写入 `/root/.docker/config.json`，重启保留在 flash 上需自行备份）：

```bash
docker login ghcr.io -u mjy378283319
# 密码粘贴 PAT（classic，勾 read:packages 即可）
```

`docker pull ghcr.io/mjy378283319/porch:latest` 成功即说明凭据可用。换 token 或报  
`denied: denied` 时重新 login。

### 3.5 权限说明

容器内进程以 root 运行（需要读宿主机 `/proc`、`/var/run/docker.sock` 做监控与容器管理），  
所以 appdata 目录属主为 `root:root` 属正常现象，不要改成 `nobody`，否则会写不进配置。  
若坚持最小权限，可去掉 Docker Socket 挂载并关掉 Docker 组件，再自行以非 root 运行  
（需同时改 Dockerfile 的 `USER` 与目录属主，属未验证路径）。

---

## 4. 反向代理 / HTTPS / 子路径

### 4.1 根路径反代（Nginx Proxy Manager / SWAG / lucky）

关键是 Upgrade 头，否则多端同步会掉线：

```nginx
location / {
    proxy_pass         http://<UNRAID-IP>:23000;
    proxy_http_version 1.1;
    proxy_set_header   Host              $host;
    proxy_set_header   X-Real-IP         $remote_addr;
    proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto $scheme;
    proxy_set_header   Upgrade           $http_upgrade;   # WebSocket
    proxy_set_header   Connection        "upgrade";       # WebSocket
    proxy_read_timeout 3600s;                             # 长连接不掐断
    client_max_body_size 0;                               # 文件传输/壁纸上传不限体积
}
```

Nginx Proxy Manager 里勾选 `Websockets Support` + `Block Common Exploits` 关闭即可。

### 4.2 子路径部署（`https://nas.example.com/porch/`）

两处必须同时改，缺一白屏：

1. 容器环境变量 `BASE_PATH=/porch`
2. 反代保留前缀并透传：

```nginx
location /porch/ {
    proxy_pass http://<UNRAID-IP>:23000/porch/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    client_max_body_size 0;
}
```

前端静态资源使用相对路径（`base: "./"`），因此子路径下不会出现写死 `/assets/...` 的 404。

### 4.3 内外网自动切换

在 `设置 → 网络` 里填：

- `内部域名`：如 `nas.local,192.168.1.`（逗号分隔）
- 每个书签的 `内网地址 (LanUrl)`：如 `http://192.168.1.10:8080`

系统按客户端 IP、访问域名、延迟三维判定，内网直接走 LanUrl，外网走公网地址。

### 4.4 开放中心（Lucky STUN）联动

设置 → 开放中心里会给出一个 Webhook 地址：

```
https://<你的域名>/api/webhook/lucky/stun
```

在 Lucky 的「STUN 穿透 → 全局 Webhook」里填这个地址，Header 用 `Content-Type: application/json`，
Body 用：

```json
{ "stun": "success", "ip": "#{ip}", "port": "#{port}" }
```

Lucky 每次穿透状态变化都会 POST 一次，Porch 收到后通过 WebSocket 推给所有已登录页面，
设置面板的「最新状态」会实时刷新；断线时点「刷新数据」也能拉到最近一次快照。

两个注意点：

- 该路径**不校验 JWT**（Lucky 不会带），如果实例暴露公网，建议在反代上按来源 IP 限制。
- 快照存在内存里，容器重启后清空，下一次任意一条回调进来就会重新填充。

### 4.5 版本检查地址

`frontend/src/stores/config.ts` 顶部的 `UPDATE_CHECK_TAGS_URL` 决定设置页显示哪个仓库的版本号。
Fork 后已默认指向本仓库；如果仓库保持私有，浏览器匿名请求 GitHub API 会 401，此时只是不显示版本号，
不影响使用。想让它工作就把仓库转公开，或改成你自己的公开仓库地址。

---

## 5. 备份、升级与回滚

### 备份

```bash
# 只需备 data 目录（其余是用户自己的媒体文件）
docker stop porch
tar -czf porch-data-$(date +%F).tar.gz -C /mnt/user/appdata/porch data
docker start porch
```

`data/` 里最关键的是 `data.json`（全部布局/书签/组件配置）、`system.json`（认证模式）、  
`users/`（多用户）、`secret.key`（JWT 签名密钥，换掉会导致所有登录态失效）。  
应用内 `设置 → 配置版本` 还能存快照并一键回滚，适合改坏了局部恢复。

### 升级

```bash
docker pull ghcr.io/mjy378283319/porch:latest
docker compose -f docker-compose.unraid.yml up -d      # 或 Unraid UI 里 Force Update
```

镜像升级不动 `data/`，配置自动继承。跨大版本前先做一次上面的备份。

### 回滚

```bash
docker pull ghcr.io/mjy378283319/porch:1.2.6     # 拉回旧 tag
docker compose up -d                          # compose 里把 tag 改成 1.2.6
```

---

## 6. 常用运维命令

```bash
docker logs -f --tail=200 porch                 # 实时日志
docker inspect --format '{{.State.Health.Status}}' porch   # 健康状态
curl -s http://127.0.0.1:23000/api/system-config  # 后端存活探测（健康检查同款）
curl -s http://127.0.0.1:23000/api/version        # 版本
docker stats --no-stream porch                  # 资源占用
```

---

## 7. 故障排查

| 现象                                            | 原因                                  | 处理                                                             |
| --------------------------------------------- | ----------------------------------- | -------------------------------------------------------------- |
| 页面白屏 / 只有背景                                   | `BASE_PATH` 与反代路径不一致；或浏览器缓存了旧 chunk | 两处路径对齐；强刷（Ctrl+Shift+R），后端已对 `index.html` 发 `no-store`         |
| `401 Unauthorized` 频繁                         | token 过期或 `secret.key` 被换           | 重新登录；确认 `data/secret.key` 未被删除                                 |
| 多端不同步 / 保存后别的端不更新                             | 反代没透传 `Upgrade`，WebSocket 被降级       | 按 4.1 补 `Upgrade`/`Connection` 头                               |
| `permission denied /var/run/docker.sock`      | 未挂 Socket 或宿主 docker 组权限            | 挂 `docker.sock`；Docker 组件需 root（本镜像默认 root）                    |
| 图标大量 404                                      | 反代把 `/icons/` 拦了，或构建时素材没打进去         | 直接访问 `/icons/favicon.ico` 验证；重新 `docker build`                 |
| 上传大文件失败 / 413                                 | 反代 `client_max_body_size` 太小        | 设为 `0` 或足够大                                                    |
| RSS / 热榜 / 壁纸加载失败                             | NAS 无法直连外网                          | 设 `PROXY_URL=http://<代理>:<端口>`，支持 http/https/socks5            |
| 天气组件空白                                        | 未配 Key（高德/和风）或源不可达                  | 设置 → 天气，切 `wttr`（免 Key）或填高德 Key                                |
| 容器一直 `unhealthy`                              | 端口/`PORT` 被改但健康检查未同步                | 健康检查读 `${PORT}`，改端口需同时改 env                                    |
| GHCR 拉取 `denied`                              | 未登录或 PAT 无 `read:packages`          | `docker login ghcr.io`；确认包可见性与 PAT scope                       |
| Actions 构建失败 `permission denied for packages` | 工作流权限不足                             | 仓库 `Settings → Actions → General → Read and write permissions` |

---

## 8. 安全建议

1. 首次登录立即改 `admin` 密码（默认 `admin` 是公开秘密）。
2. 不要把 23000 直接暴露到公网，走反代 + HTTPS；需要公网访问时开启多用户模式并逐个授权。
3. `docker.sock` 挂载是高权限能力，只在需要容器管理时开启。
4. `data/` 含用户密码哈希与 JWT 密钥，备份文件按敏感数据保管。
5. 自定义 JS 会在浏览器执行任意代码，只粘贴自己信任的脚本。
