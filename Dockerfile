# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# Porch 一体化镜像：前端(Vue3/Vite) + 后端(Go/Gin) 打进单个镜像
#
# 本地构建：
#   docker build -t porch:local .
# 多架构构建并推送：
#   docker buildx build --platform linux/amd64,linux/arm64 \
#     -t ghcr.io/<owner>/porch:latest --push .
# ---------------------------------------------------------------------------

# ---------- Stage 1: 构建前端 ----------
FROM node:20.19-bookworm-slim AS frontend-builder

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NPM_REGISTRY=https://registry.npmjs.org

ENV HTTP_PROXY=$HTTP_PROXY \
    HTTPS_PROXY=$HTTPS_PROXY \
    NPM_CONFIG_REGISTRY=$NPM_REGISTRY \
    TAILWIND_DISABLE_NATIVE=1 \
    VITE_DOCKER_BUILD=1

WORKDIR /app/frontend

# 先复制依赖清单，让依赖层可缓存
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --prefer-offline --no-audit --no-fund

# 复制源码（含 frontend/public 图标素材，vite publicDir 指向此目录）
COPY frontend/ ./

# VITE_DOCKER_BUILD=1 时 outDir=dist
RUN npm run build-only


# ---------- Stage 2: 构建后端 ----------
FROM --platform=$BUILDPLATFORM golang:alpine AS backend-builder

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG GOPROXY=https://proxy.golang.org,direct

ENV HTTP_PROXY=$HTTP_PROXY \
    HTTPS_PROXY=$HTTPS_PROXY \
    GOPROXY=$GOPROXY

WORKDIR /app/backend

COPY backend/go.mod backend/go.sum ./
RUN go mod download

COPY backend/ ./

ARG TARGETOS
ARG TARGETARCH
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH \
    go build -trimpath -ldflags="-s -w" -o porch-backend .


# ---------- Stage 3: 运行时 ----------
FROM alpine:latest

ARG VERSION=1.2.6
ARG REVISION=unknown

LABEL org.opencontainers.image.title="Porch" \
      org.opencontainers.image.description="轻量级个人导航页与仪表盘（Vue3 + Go/Gin，无数据库，纯文件存储）" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${REVISION}" \
      org.opencontainers.image.licenses="AGPL-3.0"

RUN apk --no-cache add ca-certificates tzdata wget

WORKDIR /app

ENV TZ=Asia/Shanghai \
    GIN_MODE=release \
    BASE_DIR=/app \
    HOST=0.0.0.0 \
    PORT=3000

COPY --from=backend-builder /app/backend/porch-backend ./
COPY --from=frontend-builder /app/frontend/dist ./server/public

# 运行期数据目录（建议逐个挂载持久化）
RUN mkdir -p server/data server/music server/PC server/APP server/doc \
             server/data/icon-cache server/data/config_versions

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD wget -qO- "http://127.0.0.1:${PORT:-3000}/api/system-config" >/dev/null 2>&1 || exit 1

CMD ["./porch-backend"]
