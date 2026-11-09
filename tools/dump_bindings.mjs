// 用 @vue/compiler-sfc 的 compileScript 拿到 <script setup> 的真实顶层绑定
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
const require = createRequire(new URL("../frontend/package.json", import.meta.url));
const { parse, compileScript } = require("@vue/compiler-sfc");
const file = process.argv[2];
const source = readFileSync(file, "utf8");
const { descriptor } = parse(source, { filename: file });
const compiled = compileScript(descriptor, { id: "dump" });
console.log(JSON.stringify(Object.keys(compiled.bindings || {}), null, 1));
