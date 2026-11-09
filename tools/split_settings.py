#!/usr/bin/env python3
"""把 SettingsModal.vue 的 9 个设置面板拆成独立组件。

规则：
- 模板块原样搬进子组件，不改一行标记（DOM/类名/v-if 结构完全不变）
- 子组件通过 inject 拿父级上下文，用 toRef 建立可写绑定（v-model 依然生效）
- 父组件只保留壳、标签页导航与两个确认弹窗
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path("C:/Users/MJY/WorkBuddy/2026-11-09-15-50-18/FlatNas/frontend/src/components")
SRC = ROOT / "SettingsModal.vue"
OUT = ROOT / "settings"
SCAN = Path("C:/Users/MJY/WorkBuddy/2026-11-09-15-50-18/FlatNas/tools/_panel_scan.json")

PANELS = [
    ("style", "StylePanel", 2029, 2461),
    ("widgets", "WidgetsPanel", 2461, 2844),
    ("docker", "DockerPanel", 2844, 3187),
    ("universal-window", "UniversalWindowPanel", 3187, 3657),
    ("network", "NetworkPanel", 3657, 3761),
    ("lucky-stun", "LuckyStunPanel", 3761, 4367),
    ("account", "AccountPanel", 4367, 4660),
    ("about", "AboutPanel", 4660, 4827),
    ("language", "LanguagePanel", 4827, 4866),
]

scan = json.loads(SCAN.read_text(encoding="utf-8"))
lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)
script_text = "".join(lines[:next(i for i, l in enumerate(lines) if l.startswith("</script>"))])
COMPONENT_IMPORTS = {
    m.group(1): m.group(2)
    for m in re.finditer(r'import\s+([A-Za-z_$][\w$]*)\s+from\s+"([^"]+\.vue)"', script_text)
}
print("components available:", len(COMPONENT_IMPORTS))

OUT.mkdir(exist_ok=True)
(OUT / "context.ts").write_text('import type { InjectionKey } from "vue";\n\n/**\n * 设置面板共享上下文。\n *\n * SettingsModal.vue 里维护着上百个 ref/computed/函数，9 个 tab 面板都要用。\n * 与其把几十个 props 层层透传（还容易漏、类型难维护），父组件统一 provide 一个\n * reactive 对象，子面板 inject 之后用 toRef 取自己需要的字段：\n *\n *   const ctx = inject(SETTINGS_CTX) as Record<string, any>;\n *   const appConfig = toRef(ctx, "appConfig");\n *\n * 用 toRef 而不是解构：解构会把 reactive 解包后的值定格在当时，\n * toRef 的读取会追踪依赖、写入会回写到原 ref，v-model 才依然可写。\n */\nexport const SETTINGS_CTX: InjectionKey<Record<string, any>> = Symbol("flatnas:settings-ctx");\n', encoding="utf-8")

# 1) 每个 tab 生成一个组件
for key, comp, start, end in PANELS:
    block = "".join(lines[start - 1:end - 1])
    assert re.match(r"\s*<div", block), f"{comp}: 起始不是 div"
    assert block.rstrip().endswith("</div>"), f"{comp}: 结束不是 </div>"
    names = sorted(set(scan["panels"][key]) | set(scan["models"][key]))

    # 特例：widgets 面板里直接给 activeTab 赋值，改成调用上下文里的 setTab
    if key == "widgets":
        block = block.replace("(activeTab = 'docker')", "setTab('docker')")
        names = sorted(set(names) | {"setTab"})

    head = [
        "<script setup lang=\"ts\">",
        "// 该面板由 SettingsModal.vue 拆分而来：模板保持原样，状态通过 inject 取父级上下文。",
        "import { inject, toRef } from \"vue\";",
        "import { SETTINGS_CTX } from \"./context\";",
        "",
        "const ctx = inject(SETTINGS_CTX) as Record<string, any>;",
        "",
    ]
    head += [f"const {n} = toRef(ctx, \"{n}\");" for n in names]

    used_components = sorted({c for c in re.findall(r"<([A-Z][A-Za-z0-9]*)", block) if c in COMPONENT_IMPORTS})
    if used_components:
        head.append("")
        head += [f'import {c} from "{COMPONENT_IMPORTS[c]}";'.replace('"./', '"../') for c in used_components]
    head += ["</script>", "", "<template>"]
    (OUT / f"{comp}.vue").write_text("\n".join(head) + "\n" + block + "</template>\n", encoding="utf-8")
    print(f"wrote {comp}.vue  ({end-start} lines, {len(names)} bindings)")

# 2) 父组件：替换面板块（自下而上，保持行号有效）
new_lines = list(lines)
for key, comp, start, end in reversed(PANELS):
    indent = re.match(r"\s*", new_lines[start - 1]).group(0)
    new_lines[start - 1:end - 1] = [f"{indent}<{comp} />\n"]
text = "".join(new_lines)

# 3) 父组件：补 import
imports = "\n".join(f'import {comp} from "./settings/{comp}.vue";' for _, comp, _, _ in PANELS)
text = text.replace(
    'import PasswordConfirmModal from "./PasswordConfirmModal.vue";',
    'import PasswordConfirmModal from "./PasswordConfirmModal.vue";\n'
    'import { SETTINGS_CTX } from "./settings/context";\n' + imports,
)

# 4) 父组件：provide 上下文（放在 script 末尾，此时所有绑定已就绪）
ctx_names = sorted(set(scan["union"]) | {"setTab"})
ctx_body = ",\n  ".join(ctx_names)
provide_code = (
    "\n// ---- 设置面板共享上下文 ----\n"
    "// 子面板通过 inject(SETTINGS_CTX) 取用，避免几十个 props 层层透传。\n"
    "const setTab = (tab: string) => {\n  activeTab.value = tab;\n};\n"
    "provide(\n  SETTINGS_CTX,\n  reactive({\n    " + ctx_body + ",\n  }),\n);\n"
)
idx = text.rindex("</script>")
text = text[:idx] + provide_code + text[idx:]

# 5) 父组件：ensure provide/reactive 已导入
m = re.search(r'import \{([^}]*)\} from "vue";', text)
vue_imports = {s.strip() for s in m.group(1).split(",") if s.strip()}
vue_imports |= {"provide", "reactive"}
text = text[:m.start()] + 'import { ' + ", ".join(sorted(vue_imports)) + ' } from "vue";' + text[m.end():]

SRC.write_text(text, encoding="utf-8")
print("patched SettingsModal.vue")
