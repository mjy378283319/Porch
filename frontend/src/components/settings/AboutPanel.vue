<script setup lang="ts">
// 该面板由 SettingsModal.vue 拆分而来：模板保持原样，状态通过 inject 取父级上下文。
import { inject, toRef } from "vue";
import { SETTINGS_CTX } from "./context";

const ctx = inject(SETTINGS_CTX) as Record<string, any>;

const activeTab = toRef(ctx, "activeTab");
const store = toRef(ctx, "store");
const t = toRef(ctx, "t");
</script>

<template>
  <div v-if="activeTab === 'about'" class="min-h-full flex flex-col p-8 -mt-4">
    <div class="bg-white/60 border border-gray-100 rounded-xl p-6">
      <div class="flex items-center gap-4">
        <img src="/ICON.PNG" alt="Porch" class="w-14 h-14 rounded-xl shadow-sm" />
        <div class="min-w-0">
          <div class="text-lg font-bold text-gray-900">Porch</div>
          <div class="text-xs text-gray-500">自托管导航页与仪表盘</div>
        </div>
        <div class="ml-auto shrink-0 text-lg text-gray-400 font-mono">v{{ store.currentVersion }}</div>
      </div>
      <p class="mt-4 text-xs text-gray-600 leading-relaxed">
        书签分组、多引擎搜索、可拖拽组件网格。单容器、无数据库，全部配置只存一个 JSON
        文件，备份与迁移只需要 appdata 目录。
      </p>
    </div>

    <div class="mt-4 bg-white/60 border border-gray-100 rounded-xl p-4">
      <h5 class="text-sm font-bold text-gray-900 mb-3">项目</h5>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-xs text-gray-500">
        <div class="truncate">
          项目主页：
          <a
            href="https://github.com/mjy378283319/Porch"
            target="_blank"
            class="text-gray-700 underline decoration-gray-300 hover:text-gray-900"
            >github.com/mjy378283319/Porch</a
          >
        </div>
        <div class="truncate">
          问题反馈：
          <a
            href="https://github.com/mjy378283319/Porch/issues"
            target="_blank"
            class="text-gray-700 underline decoration-gray-300 hover:text-gray-900"
            >Issues</a
          >
        </div>
        <div class="truncate">
          容器镜像：
          <a
            href="https://github.com/mjy378283319/Porch/pkgs/container/porch"
            target="_blank"
            class="text-gray-700 underline decoration-gray-300 hover:text-gray-900"
            >ghcr.io/mjy378283319/porch</a
          >
        </div>
        <div class="truncate">
          图标源：
          <a
            href="https://nasicon.top/"
            target="_blank"
            class="text-gray-700 underline decoration-gray-300 hover:text-gray-900"
            >nasicon.top</a
          >
          <span class="text-gray-400">（智能图标匹配）</span>
        </div>
      </div>
    </div>

    <div class="mt-4 bg-white/60 border border-gray-100 rounded-xl p-4">
      <h5 class="text-sm font-bold text-gray-900 mb-2">致谢与许可</h5>
      <div class="text-xs text-gray-600 leading-relaxed space-y-2">
        <p>
          本项目基于 FlatNas 修改，遵循 GNU AGPLv3。原始版权归 Garry-QD
          及贡献者所有，完整声明见仓库根目录
          <span class="font-mono text-gray-700">NOTICE</span> 与
          <span class="font-mono text-gray-700">LICENSE</span>。
        </p>
        <p>
          感谢上游贡献者与反馈者：Excel、徐大大、时也命也、大星、友人A、汪仔饭、Assassin、多度、Wheezer、苍蝇炖粉条
          等。
        </p>
        <p>
          内置图标库由
          <a
            href="https://nasicon.top/"
            target="_blank"
            class="text-gray-700 underline decoration-gray-300 hover:text-gray-900"
            >nasicon.top</a
          >
          提供，图标版权归各站点所有。
        </p>
      </div>
    </div>
  </div>
</template>
