#!/usr/bin/env python3
"""分析 SettingsModal.vue：切出各 tab 面板，统计模板用到的父级绑定与 v-model 目标。"""
from __future__ import annotations

import json
import re
from pathlib import Path

SRC = Path("C:/Users/MJY/WorkBuddy/2026-11-09-15-50-18/Porch/frontend/src/components/SettingsModal.vue")
lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)

SCRIPT_END = next(i for i, l in enumerate(lines) if l.startswith("</script>"))
script = "".join(lines[:SCRIPT_END])

PANELS = {
    "style": (2029, 2461),
    "widgets": (2461, 2844),
    "docker": (2844, 3187),
    "universal-window": (3187, 3657),
    "network": (3657, 3761),
    "lucky-stun": (3761, 4367),
    "account": (4367, 4660),
    "about": (4660, 4827),
    "language": (4827, 4867),
}

# ---- 父级绑定（用 @vue/compiler-sfc 导出的真实顶层绑定，避免把函数内局部变量当成绑定）----
BINDINGS_JSON = Path("C:/Users/MJY/WorkBuddy/2026-11-09-15-50-18/Porch/tools/_bindings.json")
bindings: set[str] = set(json.loads(BINDINGS_JSON.read_text(encoding="utf-8")))

KEYWORDS = set("""true false null undefined this new typeof instanceof in of return if else for while
switch case break continue try catch finally throw await async function const let var class extends
super void delete yield do import export default from as""".split())

KNOWN_GLOBALS = set("""Math JSON Object Array String Number Boolean Date RegExp Promise Set Map window
document console localStorage navigator location history setTimeout setInterval clearTimeout
clearInterval parseInt parseFloat isNaN encodeURIComponent decodeURIComponent Intl Number BigInt
Symbol Error structuredClone requestAnimationFrame cancelAnimationFrame URL URLSearchParams fetch
alert confirm prompt $event""".split())


def strip_noise(text: str) -> str:
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    # 去掉标签名与属性名，保留属性值
    text = re.sub(r"</?[A-Za-z][^>]*>", lambda m: " " + " ".join(re.findall(r'"[^"]*"', m.group(0))), text)
    return text


ALL: dict[str, list[str]] = {}
MODELS: dict[str, list[str]] = {}
for name, (start, end) in PANELS.items():
    block = "".join(lines[start - 1:end - 1])
    models = re.findall(r'v-model(?::[\w-]+)?="([A-Za-z_$][\w$]*)"', block)
    body = strip_noise(block)
    idents = set(re.findall(r"(?<![\w$.])[A-Za-z_$][\w$]*", body))
    used = sorted(i for i in idents if i in bindings and i not in KEYWORDS)
    ALL[name] = used
    MODELS[name] = sorted(set(models))
    missing = sorted(i for i in idents if i not in bindings and i not in KEYWORDS
                     and i not in KNOWN_GLOBALS and i not in MODELS[name]
                     and not i.startswith("_") and len(i) > 1)
    print(f"{name:18s} lines={end-start:5d} used={len(used):3d} models={len(set(models)):2d}")
    print(f"    unbound?: {missing[:14]}")

union = sorted({n for v in ALL.values() for n in v} | {m for v in MODELS.values() for m in v})
print("\nunion bindings:", len(union))
Path("C:/Users/MJY/WorkBuddy/2026-11-09-15-50-18/Porch/tools/_panel_scan.json").write_text(
    json.dumps({"panels": ALL, "models": MODELS, "union": union}, ensure_ascii=False, indent=1),
    encoding="utf-8",
)
print("written tools/_panel_scan.json")
