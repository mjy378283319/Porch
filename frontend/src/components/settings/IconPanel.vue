<script setup lang="ts">
// 共享图标管理：上传 / 浏览预览 / 删除确认 / 分享直链。
// 状态自包含，仅从上下文取 activeTab；API 走相对路径，由全局 fetch patch 处理 basePath。
import { inject, onMounted, ref, toRef } from "vue";
import { SETTINGS_CTX } from "./context";
import { toBackendUrl } from "@/utils/runtimeUrls";

const ctx = inject(SETTINGS_CTX) as Record<string, any>;
const activeTab = toRef(ctx, "activeTab");

type SharedIcon = {
  name: string;
  path: string;
  sizeBytes: number;
  modifiedAt: string;
};

const icons = ref<SharedIcon[]>([]);
const loading = ref(false);
const uploading = ref(false);
const statusText = ref("");
const statusOk = ref(true);
let statusTimer: number | null = null;
const fileInput = ref<HTMLInputElement | null>(null);
const previewIcon = ref<SharedIcon | null>(null);
const deleteTarget = ref<SharedIcon | null>(null);
const shareTarget = ref<SharedIcon | null>(null);

const notify = (message: string, ok = true) => {
  statusText.value = message;
  statusOk.value = ok;
  if (statusTimer) window.clearTimeout(statusTimer);
  statusTimer = window.setTimeout(() => {
    statusText.value = "";
    statusTimer = null;
  }, 4000);
};

const authHeaders = (): Record<string, string> => {
  const token = localStorage.getItem("flat-nas-token") || "";
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const loadIcons = async () => {
  loading.value = true;
  try {
    const res = await fetch("/api/shared-icons");
    const data = await res.json();
    if (!res.ok || !data.success) throw new Error(data.error || "加载失败");
    icons.value = Array.isArray(data.icons) ? data.icons : [];
  } catch (e) {
    notify(`加载图标失败：${(e as Error).message}`, false);
  } finally {
    loading.value = false;
  }
};

const pickFiles = () => fileInput.value?.click();

const onFilesSelected = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const files = Array.from(input.files || []);
  input.value = "";
  if (!files.length) return;
  uploading.value = true;
  try {
    const form = new FormData();
    for (const file of files) form.append("files", file);
    const res = await fetch("/api/shared-icons/upload", {
      method: "POST",
      headers: authHeaders(),
      body: form,
    });
    const data = await res.json();
    if (!res.ok || !data.success) throw new Error(data.error || "上传失败");
    notify(`已上传 ${data.icons?.length || 0} 个图标`);
    await loadIcons();
  } catch (e) {
    notify(`上传失败：${(e as Error).message}`, false);
  } finally {
    uploading.value = false;
  }
};

const confirmDelete = async () => {
  const target = deleteTarget.value;
  if (!target) return;
  deleteTarget.value = null;
  try {
    const res = await fetch(`/api/shared-icons/${encodeURIComponent(target.name)}`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    const data = await res.json();
    if (!res.ok || !data.success) throw new Error(data.error || "删除失败");
    notify(`已删除 ${target.name}`);
    if (previewIcon.value?.name === target.name) previewIcon.value = null;
    if (shareTarget.value?.name === target.name) shareTarget.value = null;
    await loadIcons();
  } catch (e) {
    notify(`删除失败：${(e as Error).message}`, false);
  }
};

const iconUrl = (icon: SharedIcon) =>
  toBackendUrl(`/shared-icons/${encodeURIComponent(icon.name)}`);

const shareMarkdown = (icon: SharedIcon) => `![${icon.name}](${iconUrl(icon)})`;
const shareHtml = (icon: SharedIcon) => `<img src="${iconUrl(icon)}" alt="${icon.name}">`;

const copyText = async (text: string, label: string) => {
  try {
    await navigator.clipboard.writeText(text);
    notify(`已复制${label}`);
  } catch {
    notify("复制失败，请手动选中复制", false);
  }
};

const formatSize = (bytes: number) =>
  bytes < 1024 ? `${bytes} B` : bytes < 1024 * 1024 ? `${(bytes / 1024).toFixed(1)} KB` : `${(bytes / 1048576).toFixed(1)} MB`;

onMounted(() => {
  void loadIcons();
});
</script>

<template>
  <div v-if="activeTab === 'icons'" class="space-y-4">
    <div class="bg-white/60 border border-gray-100 rounded-xl p-4">
      <div class="flex items-center justify-between mb-4 gap-3 flex-wrap">
        <div>
          <h4 class="text-base font-bold text-gray-900">共享图标管理</h4>
          <p class="text-xs text-gray-500 mt-1">
            上传的图标会生成公开直链，Porch 之外的应用、Unraid 容器或其它设备都能直接引用。
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="loadIcons"
            :disabled="loading"
            class="px-3 py-1.5 bg-white border border-gray-200 hover:border-gray-300 text-gray-700 text-xs rounded-lg transition-colors disabled:opacity-50"
          >
            刷新
          </button>
          <button
            @click="pickFiles"
            :disabled="uploading"
            class="px-3 py-1.5 bg-gray-900 hover:bg-black text-white text-xs rounded-lg transition-colors disabled:opacity-50"
          >
            {{ uploading ? "上传中…" : "上传图标" }}
          </button>
          <input
            ref="fileInput"
            type="file"
            accept="image/png,image/jpeg,image/gif,image/webp,image/svg+xml,image/x-icon"
            multiple
            class="hidden"
            @change="onFilesSelected"
          />
        </div>
      </div>

      <p
        v-if="statusText"
        class="mb-3 text-xs rounded-lg px-3 py-2"
        :class="statusOk ? 'text-green-700 bg-green-50' : 'text-red-600 bg-red-50'"
      >
        {{ statusText }}
      </p>

      <p v-if="loading && !icons.length" class="text-xs text-gray-500">加载中…</p>
      <p v-else-if="!icons.length" class="text-xs text-gray-500">还没有上传图标。</p>

      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        <div
          v-for="icon in icons"
          :key="icon.name"
          class="border border-gray-200 rounded-xl p-2 bg-white hover:border-gray-300 transition-colors"
        >
          <button
            @click="previewIcon = icon"
            class="w-full aspect-square flex items-center justify-center bg-gray-50 rounded-lg overflow-hidden"
            :title="`预览 ${icon.name}`"
          >
            <img :src="iconUrl(icon)" :alt="icon.name" class="max-w-full max-h-full object-contain" loading="lazy" />
          </button>
          <p class="mt-2 text-[11px] text-gray-700 truncate" :title="icon.name">{{ icon.name }}</p>
          <p class="text-[10px] text-gray-400">{{ formatSize(icon.sizeBytes) }}</p>
          <div class="flex gap-1 mt-2">
            <button
              @click="shareTarget = icon"
              class="flex-1 px-2 py-1 text-[11px] bg-blue-50 text-blue-700 hover:bg-blue-100 rounded"
            >
              分享
            </button>
            <button
              @click="deleteTarget = icon"
              class="flex-1 px-2 py-1 text-[11px] bg-red-50 text-red-600 hover:bg-red-100 rounded"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 预览 -->
    <div
      v-if="previewIcon"
      class="fixed inset-0 z-[120] bg-black/60 flex items-center justify-center p-6"
      @click.self="previewIcon = null"
    >
      <div class="bg-white rounded-xl p-5 max-w-lg w-full shadow-xl">
        <div class="flex justify-between items-center mb-3">
          <h3 class="text-sm font-bold text-gray-900 truncate">{{ previewIcon.name }}</h3>
          <button @click="previewIcon = null" class="text-gray-400 hover:text-gray-700 text-lg leading-none">×</button>
        </div>
        <div class="flex items-center justify-center bg-gray-50 rounded-lg p-6 min-h-48">
          <img :src="iconUrl(previewIcon)" :alt="previewIcon.name" class="max-h-80 max-w-full object-contain" />
        </div>
        <div class="mt-3 flex gap-2">
          <button
            @click="copyText(iconUrl(previewIcon!), '图片直链')"
            class="px-3 py-1.5 bg-gray-900 text-white text-xs rounded-lg"
          >
            复制直链
          </button>
          <button
            @click="shareTarget = previewIcon; previewIcon = null"
            class="px-3 py-1.5 bg-blue-600 text-white text-xs rounded-lg"
          >
            分享
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认 -->
    <div
      v-if="deleteTarget"
      class="fixed inset-0 z-[121] bg-black/60 flex items-center justify-center p-6"
      @click.self="deleteTarget = null"
    >
      <div class="bg-white rounded-xl p-6 max-w-sm w-full shadow-xl">
        <h3 class="text-base font-bold text-gray-900 mb-2">确认删除图标</h3>
        <p class="text-sm text-gray-600 break-all">删除后通过此直链访问的图标将失效：{{ deleteTarget.name }}</p>
        <div class="flex justify-end gap-2 mt-5">
          <button
            @click="deleteTarget = null"
            class="px-3 py-1.5 bg-white border border-gray-200 text-gray-700 text-xs rounded-lg"
          >
            取消
          </button>
          <button
            @click="confirmDelete"
            class="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs rounded-lg"
          >
            确认删除
          </button>
        </div>
      </div>
    </div>

    <!-- 分享 -->
    <div
      v-if="shareTarget"
      class="fixed inset-0 z-[122] bg-black/60 flex items-center justify-center p-6"
      @click.self="shareTarget = null"
    >
      <div class="bg-white rounded-xl p-6 max-w-xl w-full shadow-xl">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-bold text-gray-900">分享图标</h3>
          <button @click="shareTarget = null" class="text-gray-400 hover:text-gray-700 text-lg leading-none">×</button>
        </div>
        <div class="flex items-center gap-3 mb-4">
          <img :src="iconUrl(shareTarget)" :alt="shareTarget.name" class="w-16 h-16 object-contain bg-gray-50 rounded-lg" />
          <p class="text-sm text-gray-700 break-all">{{ shareTarget.name }}</p>
        </div>
        <div class="space-y-3">
          <div>
            <div class="flex justify-between items-center mb-1">
              <label class="text-xs font-medium text-gray-600">图片直链</label>
              <button @click="copyText(iconUrl(shareTarget!), '图片直链')" class="text-xs text-blue-600 hover:text-blue-700">复制</button>
            </div>
            <input readonly :value="iconUrl(shareTarget)" class="w-full px-2 py-2 border border-gray-200 rounded-lg text-[11px] text-gray-600 bg-gray-50" @focus="($event.target as HTMLInputElement).select()" />
          </div>
          <div>
            <div class="flex justify-between items-center mb-1">
              <label class="text-xs font-medium text-gray-600">Markdown</label>
              <button @click="copyText(shareMarkdown(shareTarget!), 'Markdown')" class="text-xs text-blue-600 hover:text-blue-700">复制</button>
            </div>
            <input readonly :value="shareMarkdown(shareTarget)" class="w-full px-2 py-2 border border-gray-200 rounded-lg text-[11px] text-gray-600 bg-gray-50" @focus="($event.target as HTMLInputElement).select()" />
          </div>
          <div>
            <div class="flex justify-between items-center mb-1">
              <label class="text-xs font-medium text-gray-600">HTML</label>
              <button @click="copyText(shareHtml(shareTarget!), 'HTML')" class="text-xs text-blue-600 hover:text-blue-700">复制</button>
            </div>
            <input readonly :value="shareHtml(shareTarget)" class="w-full px-2 py-2 border border-gray-200 rounded-lg text-[11px] text-gray-600 bg-gray-50" @focus="($event.target as HTMLInputElement).select()" />
          </div>
        </div>
        <p class="mt-4 text-[11px] text-gray-500">
          直链无需登录即可访问。若对方使用 HTTPS 页面，请通过 HTTPS 域名访问本应用后再复制。
        </p>
      </div>
    </div>
  </div>
</template>
