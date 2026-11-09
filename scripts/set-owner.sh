#!/usr/bin/env bash
# 把仓库里的占位符 your-name 换成你的 GitHub 用户名/组织名
# 用法: ./scripts/set-owner.sh <owner>
set -euo pipefail

OWNER="${1:-}"
if [ -z "$OWNER" ]; then
  echo "用法: $0 <github-owner>" >&2
  exit 1
fi

cd "$(dirname "$0")/.."

FILES=(
  docker-compose.yml
  docker-compose.unraid.yml
  .env.example
  unraid/flatnas.xml
  README.md
  docs/DEPLOY.md
)

for f in "${FILES[@]}"; do
  [ -f "$f" ] || continue
  if grep -q "your-name" "$f"; then
    sed -i.bak "s/your-name/${OWNER}/g" "$f" && rm -f "${f}.bak"
    echo "updated: $f"
  fi
done

echo
echo "完成。检查一遍镜像地址："
grep -rn "ghcr.io/${OWNER}/" docker-compose*.yml .env.example unraid/flatnas.xml || true
