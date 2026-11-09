// 编译每个面板 SFC，找出编译后仍然走 _ctx.xxx 的标识符 —— 这些就是
// 面板没通过 toRef 声明、运行时必然是 undefined 的绑定。
import { createRequire } from "node:module";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

const require = createRequire(new URL("../frontend/package.json", import.meta.url));
const { parse, compileScript } = require("@vue/compiler-sfc");

const dir = process.argv[2] || "frontend/src/components/settings";
const out = {};
for (const f of readdirSync(dir)) {
  if (!f.endsWith(".vue")) continue;
  const file = join(dir, f);
  const { descriptor } = parse(readFileSync(file, "utf8"), { filename: file });
  const compiled = compileScript(descriptor, { id: f, inlineTemplate: true });
  const names = new Set();
  const re = /_ctx\.([A-Za-z_$][\w$]*)/g;
  let m;
  while ((m = re.exec(compiled.content))) names.add(m[1]);
  out[f] = [...names].sort();
}
console.log(JSON.stringify(out, null, 1));
