#!/usr/bin/env bash
# 把本地仓库推到你的 GitHub 仓库
#
# 用法（Token 不要写进历史，用环境变量传）：
#   GITHUB_TOKEN=ghp_xxx ./scripts/push-to-github.sh https://github.com/<owner>/FlatNas.git
#
# 建议：先在 GitHub 网页上创建一个空仓库（不要勾 README/.gitignore），再执行本脚本。
set -euo pipefail

REMOTE_URL="${1:-}"
if [ -z "$REMOTE_URL" ]; then
  echo "用法: GITHUB_TOKEN=<pat> $0 https://github.com/<owner>/FlatNas.git" >&2
  exit 1
fi

cd "$(dirname "$0")/.."

if [ -n "${GITHUB_TOKEN:-}" ]; then
  # 临时把 token 注入 remote，推完立刻还原，避免 token 落进 .git/config
  AUTH_URL="$(printf '%s' "$REMOTE_URL" | sed -E "s#https://#https://x-access-token:${GITHUB_TOKEN}@#")"
  git remote remove origin 2>/dev/null || true
  git remote add origin "$AUTH_URL"
  git push -u origin "$(git rev-parse --abbrev-ref HEAD)" --tags
  git remote set-url origin "$REMOTE_URL"
  echo "已推送，remote 已还原为不含 token 的地址：$REMOTE_URL"
else
  git remote remove origin 2>/dev/null || true
  git remote add origin "$REMOTE_URL"
  echo "未提供 GITHUB_TOKEN，已配置 remote。请手动执行：git push -u origin \$(git rev-parse --abbrev-ref HEAD) --tags"
fi
