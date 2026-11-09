#!/usr/bin/env python3
"""把本地仓库通过 GitHub REST API 推到远端（绕开 git 协议）。

适用：`git push` 报 schannel/TLS 握手失败、CONNECT tunnel 502、或长时间挂起的机器。
前提：api.github.com 可达，PAT 对该仓库有 Contents 写权限。

与「只推一个 squash 提交」的做法不同，本脚本按本地提交链逐条重建：
对每个提交先建 tree（校验 sha 与本地一致），再建 commit（复用原 author/committer/日期/信息），
最后把分支引用指到最新提交 —— 远端历史与本地逐字节一致。

用法：
    python scripts/api_push.py --pat <pat文件> [--repo owner/name] [--root .] [--jobs 6]

注意：PAT 从文件读取，不要写进命令行历史之外的地方；脚本不会打印它。
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

API = "https://api.github.com"
SKIP_FILES = {"_msg.txt", "api_push.log"}

_print_lock = threading.Lock()
_stat_lock = threading.Lock()
_done = 0
_total = 0
_started = 0.0


def log(msg: str, end: str = "\n") -> None:
    with _print_lock:
        print(msg, end=end, flush=True)


def _proxy_handler() -> urllib.request.OpenerDirector:
    proxies = {}
    for scheme in ("https", "http"):
        val = os.environ.get(f"{scheme}_proxy") or os.environ.get(f"{scheme.upper()}_PROXY")
        if val:
            proxies[scheme] = val
    return urllib.request.build_opener(urllib.request.ProxyHandler(proxies))


_OPENER = _proxy_handler()


class ApiError(RuntimeError):
    def __init__(self, status: int, body: str, url: str):
        super().__init__(f"HTTP {status} {url}: {body[:300]}")
        self.status = status
        self.body = body


def api(token: str, method: str, path: str, payload: dict | None = None,
        retries: int = 5, timeout: float = 45.0) -> dict:
    """带重试的 API 调用。404 直接返回 {}（由调用方判断）。"""
    url = path if path.startswith("http") else API + path
    data = json.dumps(payload).encode() if payload is not None else None
    delay = 1.0
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, method=method, data=data, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "flatnas-api-push",
            "Content-Type": "application/json",
        })
        try:
            with _OPENER.open(req, timeout=timeout) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            if exc.code == 404:
                return {}
            # 401/403 里的 403 可能是次级限流，等一会儿再试
            if exc.code in (403, 429) and attempt < retries:
                wait = delay
                retry_after = exc.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    wait = max(wait, float(retry_after))
                log(f"  ! {exc.code} 限流/权限，{wait:.0f}s 后重试：{body[:120]}")
                time.sleep(wait)
                delay = min(delay * 2, 30)
                continue
            if exc.code >= 500 and attempt < retries:
                time.sleep(delay)
                delay = min(delay * 2, 30)
                continue
            raise ApiError(exc.code, body, url) from None
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt < retries:
                log(f"  ! 网络异常（{exc}），{delay:.0f}s 后重试")
                time.sleep(delay)
                delay = min(delay * 2, 30)
                continue
            raise
    raise RuntimeError("unreachable")


def git(root: Path, *args: str, binary: bool = False):
    exe = find_git()
    if not exe:
        raise RuntimeError("找不到 git 可执行文件")
    proc = subprocess.run([exe, "-C", str(root), *args], capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败：{proc.stderr.decode('utf-8', 'replace')[:300]}")
    return proc.stdout if binary else proc.stdout.decode("utf-8", "replace")


def find_git() -> str | None:
    for cand in ("git", r"C:/Program Files/Git/cmd/git.exe",
                 r"C:/Users/MJY/.workbuddy/binaries/PortableGit/versions/1.3.0/cmd/git.exe"):
        try:
            subprocess.run([cand, "--version"], capture_output=True, check=True)
            return cand
        except (OSError, subprocess.SubprocessError):
            continue
    return None


def resolve_repo(root: Path) -> str | None:
    try:
        url = git(root, "remote", "get-url", "origin").strip()
    except RuntimeError:
        return None
    m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?$", url)
    return f"{m.group(1)}/{m.group(2)}" if m else None


def iso_date(raw: str) -> str:
    """`1730000000 +0800` → `2025-10-27T10:13:20+08:00`"""
    ts, tz = raw.split()
    dt = datetime.fromtimestamp(int(ts), tz=datetime.now().astimezone().tzinfo)
    sign = tz[0]
    hours, minutes = tz[1:3], tz[3:5]
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + f"{sign}{hours}:{minutes}"


def parse_commit(root: Path, sha: str) -> dict:
    raw = git(root, "cat-file", "commit", sha, binary=True)
    head, _, message = raw.partition(b"\n\n")
    headers: dict[str, list[str]] = {}
    for line in head.decode("utf-8", "replace").splitlines():
        if line.startswith(" ") or " " not in line:
            continue
        key, _, val = line.partition(" ")
        headers.setdefault(key, []).append(val)

    def person(key: str) -> dict:
        val = headers[key][0]
        m = re.match(r"(.*?) <(.*?)> (\d+ [+-]\d{4})$", val)
        assert m, val
        return {"name": m.group(1), "email": m.group(2), "date": iso_date(m.group(3))}

    return {
        "sha": sha,
        "tree": headers["tree"][0],
        "parents": headers.get("parent", []),
        "author": person("author"),
        "committer": person("committer"),
        "message": message.decode("utf-8", "replace"),
    }


def tracked_files(root: Path) -> list[str]:
    out = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z", binary=True)
    return [p for p in out.decode("utf-8", "replace").split("\0") if p and p not in SKIP_FILES]


def tree_entries(root: Path, commit: str) -> list[dict]:
    out = git(root, "ls-tree", "-r", "-z", commit, binary=True)
    entries = []
    for item in out.split(b"\0"):
        if not item:
            continue
        meta, _, path = item.partition(b"\t")
        mode, otype, sha = meta.decode().split()
        if otype != "blob":
            continue
        entries.append({"path": path.decode("utf-8", "replace"), "mode": mode,
                        "type": "blob", "sha": sha})
    return entries


def upload_blobs(repo: str, token: str, root: Path, blobs: dict[str, str], jobs: int) -> None:
    """blobs: blob-sha -> 本地内容来源路径（用 cat-file 读，避免工作区改动影响）。"""
    global _done, _total, _started
    _total, _done, _started = len(blobs), 0, time.time()

    def one(item: tuple[str, str]) -> None:
        global _done
        blob_sha, source = item
        content = git(root, "cat-file", "blob", blob_sha, binary=True) if source == "@git" else Path(source).read_bytes()
        resp = api(token, "POST", f"/repos/{repo}/git/blobs",
                   {"content": base64.b64encode(content).decode("ascii"), "encoding": "base64"})
        if resp.get("sha") != blob_sha:
            raise RuntimeError(f"blob sha 不一致：{blob_sha} != {resp.get('sha')}")
        with _stat_lock:
            _done += 1
            done = _done
        if done % 50 == 0 or done == _total:
            elapsed = time.time() - _started
            rate = done / elapsed if elapsed else 0
            eta = (_total - done) / rate if rate else 0
            log(f"  blobs {done}/{_total}  {rate:.1f}/s  ETA {eta/60:.1f}min")

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        list(pool.map(one, sorted(blobs.items())))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pat", required=True, help="PAT 文件路径")
    ap.add_argument("--repo", default=None, help="owner/name，默认读 origin")
    ap.add_argument("--root", default=".", help="本地仓库路径")
    ap.add_argument("--jobs", type=int, default=6, help="并发上传数")
    ap.add_argument("--branch", default=None, help="分支名，默认当前分支")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    token = Path(args.pat).read_text(encoding="utf-8").strip()
    repo = args.repo or resolve_repo(root)
    if not repo:
        log("!! 无法确定目标仓库，请用 --repo owner/name")
        return 2
    branch = args.branch or git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    log(f"目标仓库: {repo}  分支: {branch}")

    me = api(token, "GET", "/user") or {}
    log(f"身份: {me.get('login')}")
    info = api(token, "GET", f"/repos/{repo}") or {}
    if not info:
        log("!! 仓库不存在或无权访问")
        return 2
    if not info.get("permissions", {}).get("push"):
        log("!! token 缺少该仓库的写权限（Contents: Read and write）")
        return 2
    log(f"仓库: {info.get('full_name')}  private={info.get('private')}")

    commits = [c for c in git(root, "rev-list", "--reverse", branch).split() if c]
    if not commits:
        log("!! 本地没有提交")
        return 2
    log(f"本地提交数: {len(commits)}（{commits[0][:7]} → {commits[-1][:7]}）")

    # 远端若已有提交，只推远端缺失的部分
    remote_head = (api(token, "GET", f"/repos/{repo}/git/ref/heads/{branch}") or {}).get("object", {}).get("sha")
    start = 0
    if remote_head and remote_head in commits:
        start = commits.index(remote_head) + 1
        log(f"远端已含 {remote_head[:7]}，从其后继续")
    elif remote_head:
        log(f"远端 head {remote_head[:7]} 不在本地历史里，将整链覆盖（force）")

    pending = commits[start:]
    if not pending:
        log("远端已是最新，无需推送")
        return 0

    # 1) 上传所有待推提交引用到的 blob（按内容 sha 去重）
    needed: dict[str, str] = {}
    for sha in pending:
        for e in tree_entries(root, sha):
            needed.setdefault(e["sha"], "@git")
    log(f"待上传 blob: {len(needed)} 个（去重后）")
    upload_blobs(repo, token, root, needed, args.jobs)

    # 2) 逐条重建 tree / commit
    # 远端 head 在本地历史里时，从它接着推；不在（例如远端只有一个初始化提交）就从根开始，
    # 让远端历史与本地逐字节一致，而不是把本地链挂到一个无关的远端提交上。
    parent = remote_head if start > 0 else None
    for sha in pending:
        meta = parse_commit(root, sha)
        entries = tree_entries(root, sha)
        tree = api(token, "POST", f"/repos/{repo}/git/trees", {"tree": entries})
        tree_sha = tree.get("sha", "")
        flag = "ok" if tree_sha == meta["tree"] else "MISMATCH"
        log(f"tree {sha[:7]}: {tree_sha[:7]} vs 本地 {meta['tree'][:7]} [{flag}]")

        body = {
            "message": meta["message"],
            "tree": tree_sha,
            "parents": [parent] if parent else [],
            "author": meta["author"],
            "committer": meta["committer"],
        }
        commit = api(token, "POST", f"/repos/{repo}/git/commits", body)
        log(f"commit {sha[:7]} → {commit.get('sha', '')[:7]}  {meta['message'].splitlines()[0][:60]}")
        parent = commit.get("sha")

    # 3) 移动分支引用
    api(token, "PATCH", f"/repos/{repo}/git/refs/heads/{branch}",
        {"sha": parent, "force": True})
    log(f"已更新 refs/heads/{branch} → {parent[:7] if parent else '?'}")

    # 4) 回读校验
    final = api(token, "GET", f"/repos/{repo}/git/trees/{git(root, 'rev-parse', f'{branch}^{{tree}}').strip()}?recursive=1") or {}
    remote_count = len([e for e in final.get("tree", []) if e.get("type") == "blob"])
    local_count = len(tracked_files(root))
    log(f"远端文件 {remote_count} / 本地跟踪 {local_count}  {'一致' if remote_count == local_count else '!! 不一致'}")
    log(f"远端 head: {(api(token, 'GET', f'/repos/{repo}/git/ref/heads/{branch}') or {}).get('object', {}).get('sha', '?')[:7]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
