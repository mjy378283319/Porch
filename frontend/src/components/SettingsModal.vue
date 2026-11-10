<script setup lang="ts">
import { computed, onMounted, onUnmounted, provide, reactive, ref, watch } from "vue";
import { useStorage } from "@vueuse/core";
import { useI18n } from "vue-i18n";
import { useMainStore } from "../stores/main";
import { useI18nStore, type SupportedLocale } from "@/stores/i18n";
import type { WidgetConfig, NavGroup, NavItem } from "@/types";
import IconUploader from "./IconUploader.vue";
import WallpaperLibrary from "./WallpaperLibrary.vue";
import PasswordConfirmModal from "./PasswordConfirmModal.vue";
import { SETTINGS_CTX } from "./settings/context";
import StylePanel from "./settings/StylePanel.vue";
import WidgetsPanel from "./settings/WidgetsPanel.vue";
import DockerPanel from "./settings/DockerPanel.vue";
import UniversalWindowPanel from "./settings/UniversalWindowPanel.vue";
import NetworkPanel from "./settings/NetworkPanel.vue";
import LuckyStunPanel from "./settings/LuckyStunPanel.vue";
import AccountPanel from "./settings/AccountPanel.vue";
import AboutPanel from "./settings/AboutPanel.vue";
import LanguagePanel from "./settings/LanguagePanel.vue";
import DockerWidget from "./DockerWidget.vue";
import ProxyToggle from "./ProxyToggle.vue";
import SystemStatusWidget from "./SystemStatusWidget.vue";
import RssSettings from "./RssSettings.vue";
import SearchSettings from "./SearchSettings.vue";
import ScriptManager from "./ScriptManager.vue";
import OverlayMotion from "@/components/base/OverlayMotion.vue";
import { DEFAULT_NETWORK_RULES, NETWORK_PRESET_RULES } from "@/utils/network";
import { createDefaultWidgetList } from "@/utils/widgetUtils";
import { toApiUrl } from "@/utils/runtimeUrls";
import daoliyuLogo from "@/assets/daoliyu.svg";

const { t } = useI18n();
const props = defineProps<{ show: boolean }>();
const emit = defineEmits(["update:show"]);
const store = useMainStore();
const i18nStore = useI18nStore();

const LOCALE_LABELS: Record<SupportedLocale, string> = {
  "zh-CN": "简体中文",
  "en-US": "English",
  "ja-JP": "日本語",
  "de-DE": "Deutsch",
  "zh-TW": "繁體中文",
  "fr-FR": "Français",
  "es-ES": "Español",
};

const LOCALE_FLAGS: Record<SupportedLocale, string> = {
  "zh-CN": "🇨🇳",
  "en-US": "🇺🇸",
  "ja-JP": "🇯🇵",
  "de-DE": "🇩🇪",
  "zh-TW": "🇹🇼",
  "fr-FR": "🇫🇷",
  "es-ES": "🇪🇸",
};

// 自动保存所有设置修改
watch(
  [() => store.widgets, () => store.appConfig],
  () => {
    if (props.show) {
      store.saveData();
    }
  },
  { deep: true }
);

const handleEscapeKey = (e: KeyboardEvent) => {
  if (e.key === "Escape" && props.show) {
    e.stopPropagation();
    emit("update:show", false);
  }
};

onMounted(() => {
  store.lockServerSync();
  document.addEventListener("keydown", handleEscapeKey);
});
onUnmounted(() => {
  store.unlockServerSync();
  document.removeEventListener("keydown", handleEscapeKey);
});

const DEFAULT_LATENCY_THRESHOLD_MS = 200;
const latencyThresholdDraft = ref("");
const latencyThresholdTouched = ref(false);
const latencyThresholdAppliedToast = ref("");
let latencyThresholdToastTimer: number | null = null;
const latencyThresholdValidation = computed(() => {
  const raw = latencyThresholdDraft.value.trim();
  if (!raw) return { ok: false, value: null as number | null, error: t('settings.validation.latencyInput') };
  if (!/^\d+$/.test(raw)) return { ok: false, value: null as number | null, error: t('settings.validation.positiveInteger') };
  const n = Number.parseInt(raw, 10);
  if (!Number.isFinite(n)) return { ok: false, value: null as number | null, error: t('settings.validation.invalidValue') };
  if (n < 20 || n > 30000) return { ok: false, value: n, error: t('settings.validation.latencyRange') };
  return { ok: true, value: n, error: "" };
});
const whitelistLatencyEnabled = computed(() => {
  return store.appConfig.whitelistLatencyMode === true;
});
const toggleWhitelistLatency = () => {
  store.appConfig.whitelistLatencyMode = !store.appConfig.whitelistLatencyMode;
  store.markDirty();
};
const syncLatencyThresholdDraft = () => {
  const v = store.appConfig.latencyThresholdMs ?? DEFAULT_LATENCY_THRESHOLD_MS;
  latencyThresholdDraft.value = String(v);
  latencyThresholdTouched.value = false;
};
watch(
  () => store.forceNetworkMode,
  (mode) => {
    if (mode === "latency") syncLatencyThresholdDraft();
  },
  { immediate: true },
);
watch(
  () => store.appConfig.latencyThresholdMs,
  () => {
    if (!latencyThresholdTouched.value) syncLatencyThresholdDraft();
  },
);
const onLatencyThresholdInput = (e: Event) => {
  latencyThresholdTouched.value = true;
  const raw = (e.target as HTMLInputElement).value ?? "";
  const digits = raw.replace(/[^\d]/g, "");
  latencyThresholdDraft.value = digits;
};
const applyLatencyThreshold = async () => {
  const v = latencyThresholdValidation.value;
  if (!v.ok || typeof v.value !== "number") return;
  store.appConfig.latencyThresholdMs = v.value;
  latencyThresholdTouched.value = false;
  store.markDirty();
  latencyThresholdAppliedToast.value = `${t('settings.messages.saved')}：${v.value} ms`;
  if (latencyThresholdToastTimer) window.clearTimeout(latencyThresholdToastTimer);
  latencyThresholdToastTimer = window.setTimeout(() => {
    latencyThresholdAppliedToast.value = "";
    latencyThresholdToastTimer = null;
  }, 1200);
};
const onLatencyThresholdBlur = async () => {
  if (!latencyThresholdTouched.value) return;
  const v = latencyThresholdValidation.value;
  if (!v.ok || typeof v.value !== "number") {
    syncLatencyThresholdDraft();
    return;
  }
  await applyLatencyThreshold();
};
const resetLatencyThreshold = async () => {
  store.appConfig.latencyThresholdMs = DEFAULT_LATENCY_THRESHOLD_MS;
  syncLatencyThresholdDraft();
  store.markDirty();
  latencyThresholdAppliedToast.value = `${t('settings.messages.reset')}：${DEFAULT_LATENCY_THRESHOLD_MS} ms`;
  if (latencyThresholdToastTimer) window.clearTimeout(latencyThresholdToastTimer);
  latencyThresholdToastTimer = window.setTimeout(() => {
    latencyThresholdAppliedToast.value = "";
    latencyThresholdToastTimer = null;
  }, 1200);
};

const mergeLegacyInternalDomainsToRules = () => {
  const legacy = String(store.appConfig.internalDomains || "")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  const existing = String(store.appConfig.networkRules || "")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  if (legacy.length === 0) return;

  const mapped = legacy.map((line) => {
    if (line.includes(":")) return line;
    if (/^\d{1,3}(\.\d{1,3}){0,3}\.?$/.test(line)) return `ip:${line}`;
    return `domain_suffix:${line}`;
  });

  const merged = Array.from(new Set([...existing, ...mapped]));
  store.appConfig.networkRules = merged.join("\n");
};

const applyDefaultNetworkRules = async () => {
  mergeLegacyInternalDomainsToRules();
  const existing = String(store.appConfig.networkRules || "").trim();
  store.appConfig.networkRules = existing
    ? `${existing}\n${DEFAULT_NETWORK_RULES}`
    : DEFAULT_NETWORK_RULES;
  store.markDirty();
};

const resetNetworkRules = async () => {
  store.appConfig.networkRules = DEFAULT_NETWORK_RULES;
  store.markDirty();
};

const toggleWhitelistLatencyMode = async () => {
  store.forceNetworkMode = store.forceNetworkMode === "latency" ? "auto" : "latency";
};

const ensureNetworkPresets = () => {
  if (!store.appConfig.networkPresets) {
    store.appConfig.networkPresets = {
      tailscale: false,
      zerotier: false,
      frp: false,
      cloudflareTunnel: false,
      ngrok: false,
    };
  }
};

const presetMeta: Record<string, { label: string; desc: string }> = {
  tailscale: { label: "Tailscale", desc: "自动识别 .ts.net 与 100.64.x.x" },
  zerotier: { label: "ZeroTier", desc: "自动识别 .zerotier.net" },
  frp: { label: "FRP", desc: "启用后可叠加你的自定义 FRP 域名规则" },
  cloudflareTunnel: { label: "Cloudflare Tunnel", desc: "识别 trycloudflare 域名" },
  ngrok: { label: "ngrok", desc: "识别 ngrok 域名" },
};

const presetKeys = Object.keys(NETWORK_PRESET_RULES);

const toggleNetworkPreset = async (key: string) => {
  ensureNetworkPresets();
  const current = !!store.appConfig.networkPresets?.[key as keyof NonNullable<typeof store.appConfig.networkPresets>];
  store.appConfig.networkPresets![key as keyof NonNullable<typeof store.appConfig.networkPresets>] = !current;
  store.markDirty();
};

const showWallpaperLibrary = ref(false);
const currentHour = ref(new Date().getHours());
let daylightTimer: number | null = null;
const updateHour = () => {
  currentHour.value = new Date().getHours();
};
const isNightTime = computed(() => currentHour.value >= 18 || currentHour.value < 6);
const isNightDaylightMode = computed(
  () => store.appConfig.daylightModeEnabled && isNightTime.value,
);
const daylightMaskPercent = computed({
  get: () => Math.round((store.appConfig.daylightMask ?? 0.5) * 100),
  set: (val: number) => {
    const v = Number.isFinite(val) ? val : 50;
    const clamped = Math.min(100, Math.max(0, v));
    store.appConfig.daylightMask = clamped / 100;
    store.markDirty();
  },
});
const musicVolume = useStorage<number>("flat-nas-music-volume", 0.7);
const musicVolumePercent = computed({
  get: () => Math.round((musicVolume.value ?? 0.7) * 100),
  set: (val: number) => {
    const v = Number.isFinite(val) ? val : 70;
    musicVolume.value = Math.min(1, Math.max(0, v / 100));
  },
});
const cardBorderHoverPreview = computed(() =>
  store.appConfig.cardBorderColor && store.appConfig.cardBorderColor !== "transparent"
    ? store.appConfig.cardBorderColor
    : store.appConfig.background || store.appConfig.solidBackgroundColor
      ? "rgba(255, 255, 255, 0.35)"
      : "rgba(15, 23, 42, 0.12)",
);
const styleVariableRows = computed(() => [
  {
    name: "--group-title-color",
    desc: "分组标题文字颜色",
    value: store.appConfig.groupTitleColor || "#ffffff",
  },
  {
    name: "--card-bg-color",
    desc: "卡片背景颜色",
    value: store.appConfig.cardBgColor || "transparent",
  },
  {
    name: "--card-border-color",
    desc: "卡片边框颜色",
    value: store.appConfig.cardBorderColor || "transparent",
  },
  {
    name: "--card-border-hover-color",
    desc: "卡片边框悬停颜色",
    value: cardBorderHoverPreview.value,
  },
  {
    name: "--card-title-color",
    desc: "卡片标题文字颜色",
    value: store.appConfig.cardTitleColor || "#111827",
  },
]);
const styleVariableStatus = {
  contrast: "待校验",
  visual: "未配置",
};
const solidBackgroundColorProxy = computed({
  get: () => store.appConfig.solidBackgroundColor || "#f3f4f6",
  set: (val: string) => {
    store.appConfig.solidBackgroundColor = val;
    store.markDirty();
  },
});

const setSolidColorAsWallpaper = () => {
  const color = store.appConfig.solidBackgroundColor || "#f3f4f6";
  if (!color) return;

  const canvas = document.createElement("canvas");
  canvas.width = 1;
  canvas.height = 1;
  const ctx = canvas.getContext("2d");
  if (ctx) {
    ctx.fillStyle = color;
    ctx.fillRect(0, 0, 1, 1);
    const dataUrl = canvas.toDataURL("image/png");
    store.appConfig.background = dataUrl;
    store.appConfig.solidBackgroundColor = "";
    store.markDirty();
  }
};

const handleWallpaperSelect = (payload: { url: string; type: string } | string) => {
  const url = typeof payload === "string" ? payload : payload.url;
  const type = typeof payload === "string" ? "pc" : payload.type;

  if (type === "mobile") {
    store.appConfig.mobileBackground = url;
  } else {
    store.appConfig.background = url;
  }
  store.markDirty();
};

const activeTab = ref("style");
const handleNavWheel = (e: WheelEvent) => {
  if (window.innerWidth < 768) {
    const container = e.currentTarget as HTMLElement;
    container.scrollLeft += e.deltaY;
  }
};

const dockerWidget = computed(() => store.widgets.find((w) => w.type === "docker"));
const systemStatusWidget = computed(() => store.widgets.find((w) => w.type === "system-status"));
const musicWidget = computed(() => store.widgets.find((w) => w.type === "music"));
const multiOpenWidgetTypes = ["iframe", "countdown", "countup", "amap-weather"];
const dedicatedWidgetTypes = ["docker"];
const isSingleOpenWidget = (type: string) =>
  !multiOpenWidgetTypes.includes(type) && !dedicatedWidgetTypes.includes(type);
const isDockerComponentCreated = computed(() => !!dockerWidget.value);
const isDockerComponentEnabled = computed(() => !!dockerWidget.value && dockerWidget.value.enable);
const sortedWidgets = computed(() => {
  const list = [...store.widgets];
  const playerIndex = list.findIndex((w) => w.type === "player");
  if (playerIndex > -1) {
    const [player] = list.splice(playerIndex, 1);
    if (player) {
      list.unshift(player);
    }
  }
  return list;
});
const singleOpenWidgets = computed(() =>
  sortedWidgets.value.filter((w) => isSingleOpenWidget(w.type)),
);
const shouldShowSingleWidgetDiagnostic = computed(() => singleOpenWidgets.value.length <= 2);
const singleWidgetDiagnosticTypes = computed(() =>
  singleOpenWidgets.value.map((w) => w.type).join("、") || "无",
);

// Debug Active Tab
watch(activeTab, (val) => {
  console.log("Active Tab Changed:", val);
});

const iconSrc = ref("/ICON.PNG");

// Ensure Docker Widget Exists
onMounted(async () => {
  if (import.meta.env.MODE === "test") return;

  // 移除强制恢复逻辑，避免覆盖用户配置
  // const hasDocker = store.widgets.some((w) => w.type === "docker");
  // if (!hasDocker) { ... }
  updateHour();
  if (daylightTimer) window.clearInterval(daylightTimer);
  daylightTimer = window.setInterval(updateHour, 60 * 1000);
});

onUnmounted(() => {
  if (daylightTimer) window.clearInterval(daylightTimer);
  daylightTimer = null;
});

const testWeatherResult = ref<{ success: boolean; message: string } | null>(null);
const isTestingWeather = ref(false);

const tempInputs = ref<Record<string, string>>({});

const updateTempInput = (key: string, value: string) => {
  tempInputs.value[key] = value;
};

const confirmTempInput = (w: WidgetConfig, field: string, key: string) => {
  if (tempInputs.value[key] !== undefined) {
    if (!w.data) w.data = {};
    w.data[field] = tempInputs.value[key];
    store.markDirty();
    // Clear temp input so it falls back to the saved value
    delete tempInputs.value[key];
  }
};

const testMusicAuthResult = ref<{ success: boolean; message: string } | null>(null);
const isTestingMusicAuth = ref(false);

const selectedMusicSize = ref({ cols: 1, rows: 1 });

watch(
  () => [musicWidget.value?.colSpan, musicWidget.value?.rowSpan],
  ([cols, rows]) => {
    if (cols && rows) {
      selectedMusicSize.value = { cols: Number(cols), rows: Number(rows) };
    }
  },
  { immediate: true },
);

const scrollToMusicSettings = () => {
  activeTab.value = "lucky-stun";
  setTimeout(() => {
    const el = document.getElementById("music-settings");
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, 100);
};

const setMusicSize = (cols: number, rows: number) => {
  const index = store.widgets.findIndex((w) => w.type === "music");
  if (index !== -1) {
    const oldWidget = store.widgets[index];
    if (!oldWidget) return;

    const newLayouts = oldWidget.layouts ? JSON.parse(JSON.stringify(oldWidget.layouts)) : {};

    // Update desktop layout if it exists to ensure GridPanel picks up the change
    if (newLayouts.desktop) {
      newLayouts.desktop.w = cols;
      newLayouts.desktop.h = rows;
    }

    store.widgets[index] = {
      ...oldWidget,
      id: oldWidget.id || "",
      type: oldWidget.type || "music",
      enable: oldWidget.enable ?? true,
      colSpan: cols,
      rowSpan: rows,
      w: cols,
      h: rows,
      layouts: newLayouts,
    };
    store.widgets = [...store.widgets]; // Force reactivity for GridPanel watcher
    store.markDirty();
  }
};

const getApiBase = (url?: string) => {
  let base = url || "/api";
  base = base.replace(/\/$/, "");
  if (!/\/api(\/v\d+)?$/.test(base)) base += "/api";
  return base;
};

const testMusicAuth = async () => {
  if (!musicWidget.value) return;

  const username = musicWidget.value.data.username;
  const password = musicWidget.value.data.password;

  if (!username || !password) {
    testMusicAuthResult.value = { success: false, message: t('settings.validation.enterUsernamePassword') };
    return;
  }

  isTestingMusicAuth.value = true;
  testMusicAuthResult.value = null;

  try {
    const apiBase = getApiBase(musicWidget.value.data.apiUrl);
    const res = await fetch(`${apiBase}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: username, password }),
    });

    if (res.ok) {
      const data = await res.json();
      if (data.token) {
        musicWidget.value.data.token = data.token;

        // Fetch User Profile
        try {
          const profileRes = await fetch(`${apiBase}/auth/profile`, {
            headers: { Authorization: `Bearer ${data.token}` },
          });
          if (profileRes.ok) {
            const profile = await profileRes.json();
            musicWidget.value.data.userProfile = profile;
          }
        } catch (e) {
          console.error("Failed to fetch profile", e);
        }

        store.markDirty();
        testMusicAuthResult.value = { success: true, message: t('settings.messages.musicAuth.success') };
      } else {
        testMusicAuthResult.value = { success: false, message: t('settings.messages.musicAuth.noToken') };
      }
    } else {
      const errText = await res.text();
      testMusicAuthResult.value = {
        success: false,
        message: `${t('settings.messages.loginFailed')} (${res.status}): ${errText}`,
      };
    }
  } catch (e: unknown) {
    console.error("Auth test error:", e);
    testMusicAuthResult.value = { success: false, message: `${t('settings.messages.requestError')}: ${(e as Error).message}` };
  } finally {
    isTestingMusicAuth.value = false;
  }
};

const isUpdatingProfile = ref(false);
const showRenameModal = ref(false);
const newDisplayName = ref("");

const openRenameModal = () => {
  if (!musicWidget.value || !musicWidget.value.data?.token) return;
  newDisplayName.value =
    musicWidget.value.data.userProfile?.displayName || musicWidget.value.data.username || "";
  showRenameModal.value = true;
};

const updateDisplayName = async () => {
  if (!musicWidget.value || !musicWidget.value.data?.token) return;
  const nextName = newDisplayName.value.trim();
  if (!nextName) return;

  isUpdatingProfile.value = true;
  try {
    const apiBase = getApiBase(musicWidget.value.data.apiUrl);
    const res = await fetch(`${apiBase}/auth/myprofile`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${musicWidget.value.data.token}`,
      },
      body: JSON.stringify({ displayName: nextName }),
    });

    if (res.ok) {
      const updated = await res.json();
      // Update local profile
      if (!musicWidget.value.data.userProfile) musicWidget.value.data.userProfile = updated;
      musicWidget.value.data.userProfile.displayName = updated.displayName || nextName;
      store.markDirty();
      // alert("昵称修改成功");
      showRenameModal.value = false;
    } else {
      alert(`${t('settings.messages.nicknameFailed')}: ` + (await res.text()));
    }
  } catch (e: unknown) {
    alert(`${t('settings.messages.requestError')}: ` + (e as Error).message);
  } finally {
    isUpdatingProfile.value = false;
  }
};

const getMusicAvatarUrl = (path?: string) => {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  const apiBase = getApiBase(musicWidget.value?.data?.apiUrl);
  // If it's a relative path like /static/..., prepend API base
  const url = path.startsWith("/") ? `${apiBase}${path}` : `${apiBase}/${path}`;
  return store.getAssetUrl(url);
};

const testWeatherConnection = async (sourceOverride?: string) => {
  isTestingWeather.value = true;
  testWeatherResult.value = null;

  const source = sourceOverride || store.appConfig.weatherSource || "uapi";
  // Use "Shanghai" as a safe default for testing connectivity
  const city = "Shanghai";
  
  let url = "";
  if (source === "qweather") {
    const projectId = store.appConfig.qweatherProjectId || "";
    const keyId = store.appConfig.qweatherKeyId || "";
    const privateKey = store.appConfig.qweatherPrivateKey || "";
    url = `/api/weather?city=${encodeURIComponent(city)}&source=qweather&projectId=${encodeURIComponent(projectId)}&keyId=${encodeURIComponent(keyId)}&privateKey=${encodeURIComponent(privateKey)}`;
  } else if (source === "amap") {
    const key = store.appConfig.amapKey || "";
    url = `/api/weather?city=${encodeURIComponent(city)}&source=amap&key=${encodeURIComponent(key)}`;
  } else {
    // Default / UAPI (OpenMeteo)
    url = `/api/weather?city=${encodeURIComponent(city)}&source=uapi`;
  }

  try {
    const res = await fetch(url);
    const j = await res.json();
    if (res.ok && j.success && j.data) {
      testWeatherResult.value = {
        success: true,
        message: `${t('settings.messages.weatherSuccess')} ${j.data.city} ${t('settings.messages.weather')}: ${j.data.text} ${j.data.temp}°C`,
      };
    } else {
      testWeatherResult.value = {
        success: false,
        message: `${t('settings.messages.weatherFailed')}: ${j.error || t('settings.messages.weatherUnknown')}`,
      };
    }
  } catch (e) {
    testWeatherResult.value = {
      success: false,
      message: `${t('settings.messages.weatherError')}: ${(e as Error).message || String(e)}`,
    };
  } finally {
    isTestingWeather.value = false;
  }
};

const passwordInput = ref("");
const newPasswordInput = ref("");
const hasAdminAccess = computed(
  () => store.isLogged && (store.systemConfig.authMode === "single" || store.username === "admin"),
);
const canManageUsers = computed(() => hasAdminAccess.value && store.systemConfig.authMode === "multi");
const isDockerSystemEnabled = computed(() => Boolean(store.systemConfig.enableDocker));
const isUpdatingDockerSystem = ref(false);

const toggleDockerSystemEnabled = async (checked: boolean) => {
  if (isUpdatingDockerSystem.value) return;
  const current = Boolean(store.systemConfig.enableDocker);
  if (current === checked) return;

  isUpdatingDockerSystem.value = true;
  try {
    const success = await store.updateSystemConfig({ enableDocker: checked });
    if (!success) {
      alert(t('settings.messages.dockerSwitchFailed'));
    }
  } finally {
    isUpdatingDockerSystem.value = false;
  }
};

const toggleDockerMock = (checked: boolean) => {
  const w = dockerWidget.value;
  if (w) {
    if (!w.data) w.data = {};
    w.data.useMock = checked;
    store.markDirty();
  }
};

// Delete Confirmation Logic
const showDeleteWidgetConfirm = ref(false);
const widgetToDeleteId = ref("");
const editingOpacityId = ref<string | null>(null);

const confirmRemoveWidget = () => {
  const index = store.widgets.findIndex((w) => w.id === widgetToDeleteId.value);
  if (index > -1) {
    store.widgets.splice(index, 1);
    store.markDirty();
  }
  showDeleteWidgetConfirm.value = false;
  widgetToDeleteId.value = "";
};
const fileInput = ref<HTMLInputElement | null>(null);
const uploadStatus = ref("");
const musicManagerOpen = ref(false);
const isMusicListLoading = ref(false);
const musicFiles = ref<string[]>([]);
const musicManagerStatus = ref("");

const fetchMusicFiles = async () => {
  isMusicListLoading.value = true;
  musicManagerStatus.value = "";
  try {
    const res = await fetch("/api/music-list");
    if (!res.ok) throw new Error(String(res.status));
    const list = (await res.json()) as unknown;
    musicFiles.value = Array.isArray(list) ? list.map((x) => String(x)) : [];
  } catch {
    musicFiles.value = [];
    musicManagerStatus.value = t('settings.messages.fetchFailed');
  } finally {
    isMusicListLoading.value = false;
  }
};

const toggleMusicManager = async () => {
  musicManagerOpen.value = !musicManagerOpen.value;
  if (musicManagerOpen.value) {
    await fetchMusicFiles();
  }
};

const deleteMusicFile = async (filePath: string) => {
  if (!filePath) return;
  // Removed native confirm as per user request for cleaner UI
  try {
    const token = localStorage.getItem("flat-nas-token");
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch("/api/music", {
      method: "DELETE",
      headers,
      body: JSON.stringify({ path: filePath }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || String(res.status));
    }
    await fetchMusicFiles();
  } catch (e: unknown) {
    console.error(e);
    const msg = e instanceof Error ? e.message : String(e);
    alert(`${t('settings.messages.deleteFailed')}: ${msg}`);
  }
};

const uploadMusic = async (event: Event) => {
  const files = (event.target as HTMLInputElement).files;
  if (!files || files.length === 0) return;

  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    if (file) {
      formData.append("files", file);
    }
  }

  uploadStatus.value = `${t('settings.messages.uploading')} ${files.length} ${t('settings.messages.files')}`;
  try {
    const token = localStorage.getItem("flat-nas-token");
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch("/api/music/upload", {
      method: "POST",
      headers,
      body: formData,
    });
    const data = await res.json();
    if (data.success) {
      uploadStatus.value = `${t('settings.messages.uploadSuccess')} ${data.count} ${t('settings.messages.files')}`;
      if (musicManagerOpen.value) {
        await fetchMusicFiles();
      }
      setTimeout(() => {
        uploadStatus.value = "";
      }, 3000);
    } else {
      uploadStatus.value = `${t('settings.messages.uploadFailed')}: ${data.error || t('settings.messages.weatherUnknown')}`;
    }
  } catch (e) {
    console.error(e);
    uploadStatus.value = t('settings.messages.uploadError');
  }
};

const formatDockerConnectionError = (error: string, socketPath?: string) => {
  const lower = error.toLowerCase();
  if (lower.includes("docker is disabled")) {
    return "Docker 服务已关闭。\n请先打开“Docker 服务”总开关，再进行连接测试。";
  }
  if (lower.includes("docker not available")) {
    return `Docker 未启用或未配置连接地址。\n容器部署请挂载 /var/run/docker.sock 并设置 dockerHost=unix:///var/run/docker.sock\nSocket: ${socketPath || "-"}`;
  }
  if (lower.includes("docker.sock") || lower.includes("unix:///var/run/docker.sock")) {
    return `无法连接 Docker Socket，请确认宿主机 Docker 已启动，并在容器中挂载 /var/run/docker.sock\nSocket: ${socketPath || "-"}`;
  }
  return `连接失败: ${error}\nSocket: ${socketPath || "-"}`;
};

const checkDockerConnection = async () => {
  if (!isDockerSystemEnabled.value) {
    alert("Docker 服务当前已关闭。\n开启总开关后才会尝试连接 Docker Engine。");
    return;
  }
  try {
    const headers = store.getHeaders();
    const res = await fetch("/api/docker/info", { headers });
    const data = await res.json();
    if (data.success && data.state === "ready") {
      alert(
        `连接成功!\n\nSocket: ${data.socketPath}\n版本: ${data.version.Version}\n系统: ${data.info.OSType} / ${data.info.Architecture}\n容器: ${data.info.Containers}\n名称: ${data.info.Name}`,
      );
    } else if (data.state === "disabled") {
      alert("Docker 服务已关闭。\n请先打开“Docker 服务”总开关。");
    } else {
      alert(formatDockerConnectionError(data.error || "Docker 不可用", data.socketPath));
    }
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    alert("网络错误: " + msg);
  }
};

const isExportingDockerLogs = ref(false);
const exportDockerLogs = async () => {
  if (isExportingDockerLogs.value) return;
  if (!isDockerSystemEnabled.value) {
    alert("Docker 服务当前已关闭，已停止日志导出请求。");
    return;
  }
  try {
    isExportingDockerLogs.value = true;
    const headers = store.getHeaders();
    const res = await fetch("/api/docker/export-logs", { headers });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || String(res.status));
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const ts = new Date().toISOString().replace(/[:.]/g, "-");
    const link = document.createElement("a");
    link.href = url;
    link.download = `docker-logs-${ts}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    alert(`${t('settings.messages.exportFailed')}: ${msg}`);
  } finally {
    isExportingDockerLogs.value = false;
  }
};

// Password Confirm Logic
const showPasswordConfirm = ref(false);
const showMultiUserWarning = ref(false);
const pendingAction = ref<(() => void | Promise<void>) | null>(null);
const confirmTitle = ref("");

const requestAuth = (action: () => void | Promise<void>, title: string) => {
  pendingAction.value = action;
  confirmTitle.value = title;
  showPasswordConfirm.value = true;
};

const onAuthSuccess = async () => {
  const action = pendingAction.value;
  pendingAction.value = null;
  if (!action) return;
  await action();
};

const close = () => emit("update:show", false);

const showPassword = ref(false);

const handleLogin = async () => {
  try {
    const success = await store.login("admin", passwordInput.value);
    if (success) {
      alert(t('settings.messages.loginSuccess'));
      passwordInput.value = "";
    }
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : t('settings.validation.enterPassword');
    alert(msg);
  }
};
const handleChangePassword = () => {
  if (!newPasswordInput.value || newPasswordInput.value.length < 4) return alert(t('settings.validation.passwordMin'));
  requestAuth(async () => {
    store.changePassword(newPasswordInput.value);
    store.markDirty();
    await store.saveData(true);
    alert(t('settings.messages.passwordChanged'));
    newPasswordInput.value = "";
  }, t('settings.messages.confirmPassword'));
};

const onMobileDockerDisplayChange = (e: Event) => {
  const checked = (e.target as HTMLInputElement | null)?.checked ?? false;
  const w = dockerWidget.value;
  if (w) {
    w.hideOnMobile = !checked;
    store.markDirty();
  }
};

const handleUltrawideChange = (e: Event) => {
  const checked = (e.target as HTMLInputElement).checked;
  if (checked) {
    alert(t('settings.messages.ultrawideTip'));
  }
};

// Admin User Management
const userList = ref<string[]>([]);
const newUser = ref("");
const newPwd = ref("");
const licenseKey = ref("");

const loadUsers = async () => {
  if (!canManageUsers.value) {
    userList.value = [];
    return;
  }
  const users = await store.fetchUsers();
  if (Array.isArray(users)) {
    userList.value = users;
  }
};

const handleAddUser = async () => {
  if (!newUser.value || !newPwd.value) return alert(t('settings.validation.enterUsernamePassword'));
  try {
    await store.addUser(newUser.value, newPwd.value);
    alert(t('settings.messages.addSuccess'));
    newUser.value = "";
    newPwd.value = "";
    loadUsers();
  } catch (e: unknown) {
    alert((e as Error).message || t('settings.messages.addSuccess'));
  }
};

const handleDeleteUser = async (u: string) => {
  if (!confirm(`${t('settings.messages.confirmDeleteUser')} ${u}？`)) return;
  try {
    await store.deleteUser(u);
    alert(t('settings.messages.deleteSuccess'));
    loadUsers();
  } catch {
    alert(t('settings.messages.deleteFailed'));
  }
};

const handleUploadLicense = async () => {
  if (!licenseKey.value) return alert(t('settings.validation.enterKey'));
  try {
    await store.uploadLicense(licenseKey.value);
    alert(t('settings.messages.licenseSuccess'));
    licenseKey.value = "";
  } catch (e: unknown) {
    alert((e as Error).message || t('settings.messages.licenseFailed'));
  }
};

// Watch for tab change to load users
watch(
  activeTab,
  (val) => {
    if (val === "account" && canManageUsers.value) {
      loadUsers();
    }
  },
  { immediate: true },
);

const toggleAuthMode = async () => {
  const currentMode = store.systemConfig.authMode;
  const newMode = currentMode === "single" ? "multi" : "single";

  if (newMode === "single") {
    if (!confirm(t('settings.messages.confirmSwitchSingle'))) return;
    requestAuth(() => performAuthModeSwitch(newMode), t('settings.messages.confirmSwitchAuth'));
  } else {
    // Show custom warning for multi-user mode switch
    showMultiUserWarning.value = true;
  }
};

const performAuthModeSwitch = async (newMode: string) => {
  const success = await store.updateSystemConfig({ authMode: newMode });
  if (success) {
    close();
    store.logout();
  } else {
    alert(t('settings.messages.switchFailed'));
  }
};

onMounted(() => {
  store.checkUpdate();
});

// 单用户模式：配置版本管理
const versionLabel = ref("");
const versions = ref<{ id: string; label: string; createdAt: number; size: number }[]>([]);
const loadingVersions = ref(false);
const isImporting = ref(false);
/** 上传阶段 | 导入完成后后台补图标 */
const importOverlayMode = ref<"upload" | "icons">("upload");
const importProgress = ref(0);
const importTotal = ref(0);

const findNavItemByIdInStore = (id: string): NavItem | null => {
  for (const g of store.groups) {
    const found = g.items.find((it) => it.id === id);
    if (found) return found;
  }
  return null;
};

// 文件传输：缩略图管理
const isRegeneratingThumbs = ref(false);
const thumbRegenerationStats = ref<{ processed: number; generated: number; errors: string[] } | null>(null);

const regenerateAllThumbs = async () => {
  if (!confirm(t('settings.messages.confirmRegenerateThumbs'))) return;
  
  isRegeneratingThumbs.value = true;
  thumbRegenerationStats.value = null;
  
  try {
    const token = localStorage.getItem("flat-nas-token");
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    
    const response = await fetch("/api/transfer/regenerate-thumbs", {
      method: "POST",
      headers,
    });
    
    if (response.ok) {
      const stats = await response.json();
      thumbRegenerationStats.value = {
        processed: stats.processed || 0,
        generated: stats.generated || 0,
        errors: stats.errors || [],
      };
    } else {
      alert(t('settings.messages.thumbRegenFailed'));
    }
  } catch (err) {
    console.error("Failed to regenerate thumbnails:", err);
    alert(t('settings.messages.thumbRegenFailed'));
  } finally {
    isRegeneratingThumbs.value = false;
  }
};

const fetchVersions = async () => {
  try {
    loadingVersions.value = true;
    const token = localStorage.getItem("flat-nas-token");
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const r = await fetch("/api/config-versions", { headers });
    if (!r.ok) return;
    const j = await r.json();
    versions.value = j.versions || [];
  } finally {
    loadingVersions.value = false;
  }
};

const saveVersion = async () => {
  try {
    const token = localStorage.getItem("flat-nas-token");
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const r = await fetch("/api/config-versions", {
      method: "POST",
      headers,
      body: JSON.stringify({ label: versionLabel.value.trim() }),
    });
    if (!r.ok) {
      const d = await r.json().catch(() => ({}));
      alert(`${t('settings.messages.saveFailed')}: ${d.error || r.status}`);
      return;
    }
    versionLabel.value = "";
    await fetchVersions();
  } catch (e) {
    console.error("[SettingsModal][SaveVersion]", e);
  }
};

const restoreVersion = async (id: string) => {
  try {
    if (!confirm(t('settings.messages.confirmRestoreVersion'))) return;
    const token = localStorage.getItem("flat-nas-token");
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const r = await fetch("/api/config-versions/restore", {
      method: "POST",
      headers,
      body: JSON.stringify({ id }),
    });
    if (!r.ok) {
      const d = await r.json().catch(() => ({}));
      alert(`${t('settings.messages.restoreFailed')}: ${d.error || r.status}`);
      return;
    }
    window.location.reload();
  } catch (e) {
    console.error("[SettingsModal][RestoreVersion]", e);
  }
};

const deleteVersion = async (id: string) => {
  try {
    const token = localStorage.getItem("flat-nas-token");
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const r = await fetch(`/api/config-versions/${encodeURIComponent(id)}`, {
      method: "DELETE",
      headers,
    });
    if (!r.ok) {
      const d = await r.json().catch(() => ({}));
      alert(`${t('settings.messages.deleteFailed')}: ${d.error || r.status}`);
      return;
    }
    await fetchVersions();
  } catch (e) {
    console.error("[SettingsModal][DeleteVersion]", e);
  }
};

onMounted(() => {
  if (hasAdminAccess.value && store.systemConfig.authMode === "single") {
    fetchVersions();
  } else if (store.isLogged) {
    // 非单用户模式下，也允许查看自己的版本
    fetchVersions();
  }
});

const getWebhookUrl = () => {
  return toApiUrl("/api/webhook/lucky/stun");
};

const copyWebhookUrl = () => {
  navigator.clipboard.writeText(getWebhookUrl()).then(() => {
    alert(t('settings.messages.copiedWebhook'));
  });
};

const formatTime = (ts?: number) => {
  if (!ts) return "-";
  return new Date(ts).toLocaleString();
};

onMounted(() => {
  store.fetchLuckyStunData();
});

const isUnknownWidget = (type: string) => {
  const knownTypes = [
    "clock",
    "weather",
    "clockweather",
    "calendar",
    "memo",
    "search",
    "quote",
    "bookmarks",
    "todo",
    "calculator",
    "ip",
    "player",
    "hot",
    "rss",
    "sidebar",
    "iframe",
    "countdown",
    "countup",
    "amap-weather",
    "docker",
    "system-status",
    "status-monitor",
    "file-transfer",
    "music",
    "custom-css",
    "div-card",
  ];

  return !knownTypes.includes(type);
};

const restoreMissingWidgets = () => {
  const defaultWidgets = createDefaultWidgetList(store.isLogged);

  let addedCount = 0;
  defaultWidgets.forEach((def) => {
    const exists = store.widgets.some((w) => w.type === def.type);
    if (!exists) {
      store.widgets.push(def);
      addedCount++;
    }
  });

  if (addedCount > 0) {
    store.markDirty();
    alert(`${t('settings.messages.componentsRestored')} ${addedCount} ${t('settings.messages.missingComponents')}`);
} else {
  alert(t('settings.messages.noMissingComponents'));
  }
};

const addCustomCssWidget = () => {
  const newId = "custom-css-" + Date.now();
  store.widgets.push({
    id: newId,
    type: "custom-css",
    enable: true,
    data: {
      title: t('settings.messages.customComponentTitle'),
      html: t('settings.messages.customComponentHtml'),
      css: ".my-custom-component {\n  padding: 10px;\n  background: linear-gradient(to right, #e0eafc, #cfdef3);\n  border-radius: 8px;\n  text-align: center;\n  height: 100%;\n  display: flex;\n  flex-direction: column;\n  justify-content: center;\n}\n.my-custom-component h3 {\n  margin: 0 0 5px 0;\n  color: #333;\n}",
    },
    colSpan: 1,
    rowSpan: 1,
    isPublic: true,
  });
  store.markDirty();
};

const addAmapWeatherWidget = () => {
  const newId = "amap-weather-" + Date.now();
  store.widgets.push({
    id: newId,
    type: "amap-weather",
    enable: true,
    data: { city: "110101", apiKey: "" },
    colSpan: 1,
    rowSpan: 1,
    isPublic: true,
  });
  store.markDirty();
  alert(t('settings.messages.weatherAdded'));
};

const addMusicWidget = () => {
  const newId = "music-" + Date.now();
  store.widgets.push({
    id: newId,
    type: "music",
    enable: true,
    data: { title: t('settings.messages.musicTitle'), apiUrl: "", username: "", password: "" },
    colSpan: 1,
    rowSpan: 1,
    isPublic: true,
  });
  store.markDirty();
};

const enableDockerWidget = () => {
  const def: WidgetConfig = {
    id: "docker",
    type: "docker",
    enable: true,
    isPublic: true,
    colSpan: 1,
    rowSpan: 1,
    data: { useMock: false },
  };
  const exists = store.widgets.find((w) => w.type === "docker");
  if (!exists) {
    store.widgets.push(def);
    store.markDirty();
  } else {
    exists.enable = true;
    store.markDirty();
  }
};

const toggleSystemStatusMock = (checked: boolean) => {
  const w = systemStatusWidget.value;
  if (w) {
    if (!w.data) w.data = {};
    w.data.useMock = checked;
    store.markDirty();
  }
};

const enableSystemStatusWidget = () => {
  const def: WidgetConfig = {
    id: "system-status",
    type: "system-status",
    enable: true,
    isPublic: true,
    colSpan: 1,
    rowSpan: 1,
    data: { useMock: false },
  };
  const exists = store.widgets.find((w) => w.type === "system-status");
  if (!exists) {
    store.widgets.push(def);
    store.markDirty();
  } else {
    exists.enable = true;
    store.markDirty();
  }
};

const onMobileSystemStatusDisplayChange = (e: Event) => {
  const checked = (e.target as HTMLInputElement | null)?.checked ?? false;
  const w = systemStatusWidget.value;
  if (w) {
    w.hideOnMobile = !checked;
    store.markDirty();
  }
};

const handleExport = async () => {
  try {
    // 强制立即保存，确保后端数据也是最新的
    store.markDirty();

    const backupData = {
      items: store.items,
      widgets: store.widgets,
      appConfig: store.appConfig,
      groups: store.groups,
      rssFeeds: store.rssFeeds,
      rssCategories: store.rssCategories,
    };
    const jsonString = JSON.stringify(backupData, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `flat-nas-backup-${new Date().toISOString().substring(0, 10).replace(/-/g, "")}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (e) {
    alert(t('settings.messages.exportFailed'));
    console.error("[SettingsModal][Export] failed", e);
  }
};

const triggerImport = () => {
  fileInput.value?.click();
};

const AUTO_ICON_CHECK_TIMEOUT_MS = 1500;
const autoIconCache = new Map<string, Promise<string>>();

const checkImage = (url: string, timeoutMs = AUTO_ICON_CHECK_TIMEOUT_MS): Promise<boolean> => {
  return new Promise((resolve) => {
    const img = new Image();
    let settled = false;
    const finalize = (ok: boolean) => {
      if (settled) return;
      settled = true;
      window.clearTimeout(timer);
      img.onload = null;
      img.onerror = null;
      // Stop any pending image work once we already know the result.
      img.src = "";
      resolve(ok);
    };
    const timer = window.setTimeout(() => finalize(false), timeoutMs);
    img.onload = () => finalize(true);
    img.onerror = () => finalize(false);
    img.src = url;
  });
};

const getAutoIcon = async (url: string) => {
  if (!url) return "";
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.toLowerCase();
    const cacheKey = hostname || url;
    let task = autoIconCache.get(cacheKey);

    if (!task) {
      task = (async () => {
        const candidates = [
          `https://www.favicon.vip/get.php?url=${encodeURIComponent(url)}`,
          `https://icon.bqb.cool?url=${encodeURIComponent(url)}`,
          `https://icons.duckduckgo.com/ip3/${hostname}.ico`,
          `${urlObj.origin}/favicon.ico`,
        ];
        for (const src of candidates) {
          if (await checkImage(src)) return src;
        }
        return "";
      })();
      autoIconCache.set(cacheKey, task);
    }

    return await task;
  } catch {
    // ignore
  }
  return "";
};

const handleFileChange = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async (e: ProgressEvent<FileReader>) => {
    let sunPanelItemsNeedingIcons: NavItem[] = [];
    try {
      const content = e.target?.result as string;
      let data = JSON.parse(content);

      // SunPanel format support
      if (Array.isArray(data.icons)) {
        const newGroups: NavGroup[] = data.icons.map(
          (
            g: {
              title?: string;
              children?: {
                title?: string;
                url?: string;
                lanUrl?: string;
                description?: string;
                openMethod?: number;
                icon?: { src?: string };
              }[];
            },
            gIdx: number,
          ) => ({
            id: Date.now().toString() + "_" + gIdx,
            title: g.title || "New Group",
            items: (g.children || []).map(
              (
                c: {
                  title?: string;
                  url?: string;
                  lanUrl?: string;
                  description?: string;
                  openMethod?: number;
                  icon?: { src?: string };
                },
                cIdx: number,
              ) => {
                let icon = c.icon?.src || "";
                // Only keep absolute URLs (http/https), discard relative paths (server-local)
                if (!icon.startsWith("http")) {
                  icon = "";
                }

                return {
                  id: Date.now().toString() + "_" + gIdx + "_" + cIdx,
                  title: c.title || "New Item",
                  url: c.url || "",
                  lanUrl: c.lanUrl || "",
                  icon: icon,
                  description1: c.description || "",
                  // SunPanel: 2 usually means new tab
                  openInNewTab: c.openMethod === 2,
                  isPublic: true,
                };
              },
            ),
          }),
        );

        // SunPanel：先快速导入；图标在「导入成功」后于后台抓取并单独保存（见下方 POST 之后逻辑）
        const allItems = newGroups.flatMap((g) => g.items);
        sunPanelItemsNeedingIcons = allItems.filter((it) => !it.icon && !!(it.url || it.lanUrl));

        // Preserve existing config, append new groups
        const existingGroups = store.groups;
        const finalGroups = [...existingGroups, ...newGroups];

        data = {
          groups: finalGroups,
          items: finalGroups.flatMap((g) => g.items),
          widgets: store.widgets,
          appConfig: store.appConfig,
        };
      } else if ((!data.groups || data.groups.length === 0) && data.items) {
        const items = data.items.map((item: NavItem) => ({
          ...item,
          isPublic: item.isPublic ?? true,
        }));
        data.groups = [{ id: Date.now().toString(), title: "默认分组", items: items }];
      }
      if ("password" in data) {
        delete data.password;
      }

      isImporting.value = true;
      importOverlayMode.value = "upload";
      importProgress.value = 0;
      importTotal.value = 0;

      const token = localStorage.getItem("flat-nas-token");
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const r = await fetch("/api/data/import", {
        method: "POST",
        headers,
        body: JSON.stringify(data),
      });
      if (!r.ok) throw new Error("import_post_failed:" + r.status);

      await store.fetchData();

      if (sunPanelItemsNeedingIcons.length > 0) {
        importOverlayMode.value = "icons";
        importTotal.value = sunPanelItemsNeedingIcons.length;
        importProgress.value = 0;

        const batchSize = 10;
        for (let i = 0; i < sunPanelItemsNeedingIcons.length; i += batchSize) {
          const batch = sunPanelItemsNeedingIcons.slice(i, i + batchSize);
          await Promise.all(
            batch.map(async (refItem) => {
              try {
                const live = findNavItemByIdInStore(refItem.id);
                if (!live || live.icon) return;
                const targetUrl = live.url || live.lanUrl;
                if (targetUrl) {
                  const icon = await getAutoIcon(targetUrl);
                  if (icon) live.icon = icon;
                }
              } finally {
                importProgress.value++;
              }
            }),
          );
        }

        const saveResult = await store.saveData(true, true);
        if (saveResult !== "saved" && saveResult !== "no_change") {
          console.warn("[SettingsModal][Import] post-icon saveData:", saveResult);
          if (saveResult === "conflict") {
            alert(t('settings.messages.configConflict'));
            return;
          }
        }
      }

      alert(t('settings.messages.importSuccess'));
    } catch (err) {
      alert(t('settings.messages.importFailed'));
      console.error("[SettingsModal][Import] failed", err);
    } finally {
      if (fileInput.value) fileInput.value.value = "";
      isImporting.value = false;
      importOverlayMode.value = "upload";
      importProgress.value = 0;
      importTotal.value = 0;
    }
  };
  reader.readAsText(file);
};

const saveDefaultBtnText = ref("设为默认模板");

const handleReset = async () => {
  requestAuth(async () => {
    // 密码验证通过后直接执行
    try {
      const token = localStorage.getItem("flat-nas-token");
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const r = await fetch("/api/reset", {
        method: "POST",
        headers,
      });
      if (!r.ok) {
        const data = await r.json().catch(() => ({}));
        throw new Error(data.error || "reset_failed");
      }
      // 移除成功弹窗，直接刷新
      window.location.reload();
    } catch (e: unknown) {
      const err = e as Error;
      alert("恢复失败: " + (err.message || "未知错误"));
      console.error("[SettingsModal][Reset] failed", e);
    }
  }, "请输入密码以确认恢复初始化");
};

const handleSaveAsDefault = async () => {
  requestAuth(async () => {
    // 密码验证通过后直接执行
    try {
      const token = localStorage.getItem("flat-nas-token");
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const r = await fetch("/api/default/save", {
        method: "POST",
        headers,
      });
      if (!r.ok) {
        const data = await r.json().catch(() => ({}));
        throw new Error(data.error || "save_default_failed");
      }

      // 移除成功弹窗，使用按钮文字反馈
      saveDefaultBtnText.value = "保存成功！";
      setTimeout(() => {
        saveDefaultBtnText.value = "设为默认模板";
      }, 2000);
    } catch (e: unknown) {
      const err = e as Error;
      alert("保存失败: " + (err.message || "未知错误"));
      console.error("[SettingsModal][SaveDefault] failed", e);
    }
  }, "请输入密码以确认保存默认模板");
};

const normalizeFileTransferWidgets = () => {
  const list = store.widgets;
  const all = list.filter((w) => w.type === "file-transfer");
  if (all.length === 0) return;

  const keep = all.find((w) => w.id === "file-transfer") || all[0]!;
  let changed = false;

  for (let i = list.length - 1; i >= 0; i--) {
    const w = list[i];
    if (w && w.type === "file-transfer" && w.id !== keep.id) {
      list.splice(i, 1);
      changed = true;
    }
  }

  if (
    keep.id !== "file-transfer" &&
    !list.some((w) => w.id === "file-transfer" && w.type !== "file-transfer")
  ) {
    keep.id = "file-transfer";
    changed = true;
  }

  if (changed) store.markDirty();
};

// 修复：移除 computed 中的副作用，改用 onMounted 初始化
onMounted(() => {
  store.widgets.forEach((w: WidgetConfig) => {
    if (w.type === "iframe" && !w.data) {
      w.data = { url: "" };
    }
  });
  normalizeFileTransferWidgets();
});

const addIframeWidget = () => {
  const newId = "w-" + Date.now();
  store.widgets.push({
    id: newId,
    type: "iframe",
    enable: true,
    data: { url: "" },
    colSpan: 2,
    rowSpan: 2,
    isPublic: true,
  });
  store.markDirty();
};

const addCountdownWidget = () => {
  const newId = "w-cd-" + Date.now();
  store.widgets.push({
    id: newId,
    type: "countdown",
    enable: true,
    data: {
      targetDate: "",
      title: "重要时刻",
      style: "card",
    },
    colSpan: 1,
    rowSpan: 1,
    isPublic: true,
  });
  store.markDirty();
};

const addCountUpWidget = () => {
  const newId = "w-cup-" + Date.now();
  store.widgets.push({
    id: newId,
    type: "countup",
    enable: true,
    data: {
      startTime: new Date().toISOString().slice(0, 16),
      title: "正计时",
      style: "card",
      isRunning: false,
      totalPauseDuration: 0,
      pauseStartTime: null,
    },
    colSpan: 1,
    rowSpan: 1,
    isPublic: true,
  });
  store.markDirty();
};

const removeWidget = (id: string) => {
  widgetToDeleteId.value = id;
  showDeleteWidgetConfirm.value = true;
};

const deleteWidget = (id: string) => {
  removeWidget(id);
};

// Wallpaper Library Logic
// Wallpaper logic moved to WallpaperLibrary.vue
// Keeping minimal code if needed, or remove completely if unused.
// Since we removed the UI that uses these functions, we can remove the functions too.
// However, to be safe and clean, I will remove the unused refs and functions.

/* Removed: wallpapers, loadingWallpapers, fetchWallpapers, deleteWallpaper, uploadWallpaperInput, triggerWallpaperUpload, handleWallpaperUpload */
/* Removed: mobileWallpapers, loadingMobileWallpapers, fetchMobileWallpapers, deleteMobileWallpaper, uploadMobileWallpaperInput, triggerMobileWallpaperUpload, handleMobileWallpaperUpload */

onMounted(() => {
  // Removed wallpaper fetches
});

// Dragging Logic
const modalPosition = ref({ x: 0, y: 0 });
const isDragging = ref(false);
const dragStart = { x: 0, y: 0 };
const initialModalPosition = { x: 0, y: 0 };

const onMouseDown = (e: MouseEvent) => {
  // Prevent dragging if clicking on interactive elements
  if ((e.target as HTMLElement).closest("button, input, textarea, a, .no-drag")) return;

  isDragging.value = true;
  dragStart.x = e.clientX;
  dragStart.y = e.clientY;
  initialModalPosition.x = modalPosition.value.x;
  initialModalPosition.y = modalPosition.value.y;

  window.addEventListener("mousemove", onMouseMove);
  window.addEventListener("mouseup", onMouseUp);
};

const onMouseMove = (e: MouseEvent) => {
  if (!isDragging.value) return;
  const dx = e.clientX - dragStart.x;
  const dy = e.clientY - dragStart.y;
  modalPosition.value.x = initialModalPosition.x + dx;
  modalPosition.value.y = initialModalPosition.y + dy;
};

const onMouseUp = () => {
  isDragging.value = false;
  window.removeEventListener("mousemove", onMouseMove);
  window.removeEventListener("mouseup", onMouseUp);
};

// Nav Dragging Logic
const navRef = ref<HTMLElement | null>(null);
const isNavDragging = ref(false);
const navStartX = ref(0);
const navScrollLeft = ref(0);

const onNavMouseDown = (e: MouseEvent) => {
  if (!navRef.value) return;
  isNavDragging.value = true;
  navStartX.value = e.pageX - navRef.value.offsetLeft;
  navScrollLeft.value = navRef.value.scrollLeft;
};

const onNavMouseMove = (e: MouseEvent) => {
  if (!isNavDragging.value || !navRef.value) return;
  e.preventDefault();
  const x = e.pageX - navRef.value.offsetLeft;
  const walk = (x - navStartX.value) * 2;
  navRef.value.scrollLeft = navScrollLeft.value - walk;
};

const onNavMouseUp = () => {
  isNavDragging.value = false;
};

watch(
  () => props.show,
  (val) => {
    if (val && activeTab.value === "account" && store.isLogged) {
      if (canManageUsers.value) {
        loadUsers();
      }
      if (store.systemConfig.authMode === "single" || !canManageUsers.value) {
        fetchVersions();
      }
    }
  },
);

watch(activeTab, (val) => {
  if (val === "account" && store.isLogged && (store.systemConfig.authMode === "single" || !canManageUsers.value)) {
    fetchVersions();
  }
});

// ---- 设置面板共享上下文 ----
// 子面板通过 inject(SETTINGS_CTX) 取用，避免几十个 props 层层透传。
const setTab = (tab: string) => {
  activeTab.value = tab;
};
provide(
  SETTINGS_CTX,
  reactive({
    DEFAULT_LATENCY_THRESHOLD_MS,
  LOCALE_FLAGS,
  LOCALE_LABELS,
  activeTab,
  addAmapWeatherWidget,
  addCountUpWidget,
  addCountdownWidget,
  addCustomCssWidget,
  addIframeWidget,
  addMusicWidget,
  applyLatencyThreshold,
  canManageUsers,
  checkDockerConnection,
  confirmTempInput,
  copyWebhookUrl,
  daoliyuLogo,
  daylightMaskPercent,
  deleteMusicFile,
  deleteVersion,
  deleteWidget,
  dockerWidget,
  editingOpacityId,
  enableDockerWidget,
  enableSystemStatusWidget,
  exportDockerLogs,
  fetchMusicFiles,
  fileInput,
  formatTime,
  getMusicAvatarUrl,
  getWebhookUrl,
  handleAddUser,
  handleChangePassword,
  handleDeleteUser,
  handleExport,
  handleFileChange,
  handleLogin,
  handleReset,
  handleSaveAsDefault,
  handleUploadLicense,
  handleWallpaperSelect,
  hasAdminAccess,
  i18nStore,
  isDockerComponentCreated,
  isDockerSystemEnabled,
  isExportingDockerLogs,
  isMusicListLoading,
  isTestingMusicAuth,
  isTestingWeather,
  isUnknownWidget,
  isUpdatingDockerSystem,
  isUpdatingProfile,
  latencyThresholdAppliedToast,
  latencyThresholdDraft,
  latencyThresholdTouched,
  latencyThresholdValidation,
  licenseKey,
  loadingVersions,
  musicFiles,
  musicManagerOpen,
  musicManagerStatus,
  musicVolumePercent,
  musicWidget,
  newPasswordInput,
  newPwd,
  newUser,
  onLatencyThresholdBlur,
  onLatencyThresholdInput,
  onMobileDockerDisplayChange,
  onMobileSystemStatusDisplayChange,
  openRenameModal,
  passwordInput,
  removeWidget,
  resetLatencyThreshold,
  restoreMissingWidgets,
  restoreVersion,
  saveDefaultBtnText,
  saveVersion,
  scrollToMusicSettings,
  selectedMusicSize,
  setMusicSize,
  setSolidColorAsWallpaper,
  setTab,
  shouldShowSingleWidgetDiagnostic,
  showPassword,
  showWallpaperLibrary,
  singleOpenWidgets,
  singleWidgetDiagnosticTypes,
  solidBackgroundColorProxy,
  store,
  styleVariableRows,
  styleVariableStatus,
  systemStatusWidget,
  t,
  tempInputs,
  testMusicAuth,
  testMusicAuthResult,
  testWeatherConnection,
  testWeatherResult,
  toggleAuthMode,
  toggleDockerMock,
  toggleDockerSystemEnabled,
  toggleMusicManager,
  toggleSystemStatusMock,
  toggleWhitelistLatency,
  triggerImport,
  updateTempInput,
  uploadMusic,
  uploadStatus,
  userList,
  versionLabel,
  versions,
  whitelistLatencyEnabled,
  }),
);
</script>

<template>
  <OverlayMotion
    :show="show"
    :z-index="50"
    overlay-class="bg-black/30 backdrop-blur-sm p-3"
    panel-class="w-full max-w-3xl"
  >
    <div
      v-if="isImporting"
      class="fixed inset-0 z-[60] bg-black/50 backdrop-blur-sm flex items-center justify-center"
    >
      <div class="bg-white rounded-xl p-6 shadow-2xl max-w-sm w-full mx-4 text-center space-y-4">
        <div
          class="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent mx-auto"
        ></div>
        <div>
          <h3 class="text-lg font-bold text-gray-900">
            {{ importOverlayMode === "upload" ? $t('settings.messages.importingConfig') : $t('settings.messages.fetchingIcons') }}
          </h3>
          <p class="text-sm text-gray-500 mt-1">
            <template v-if="importOverlayMode === 'upload'">
              {{ $t('settings.messages.savingToServer') }}
            </template>
            <template v-else>
              {{ $t('settings.messages.configSavedFetchingIcons') }}
            </template>
          </p>
        </div>
        <div v-if="importOverlayMode === 'icons' && importTotal > 0" class="space-y-1">
          <div class="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
            <div
              class="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out"
              :style="{ width: `${(importProgress / importTotal) * 100}%` }"
            ></div>
          </div>
          <p class="text-xs text-gray-400">{{ $t('settings.messages.iconProgress') }} {{ importProgress }} / {{ importTotal }}</p>
        </div>
      </div>
    </div>

    <div
      class="backdrop-blur-xl rounded-2xl shadow-2xl w-full max-w-3xl overflow-hidden flex flex-col md:flex-row h-[600px] md:h-[480px] relative"
      :class="isNightDaylightMode ? 'night-settings bg-slate-900/60 text-slate-100 border border-white/10' : 'bg-white/90'"
      :style="{ transform: `translate(${modalPosition.x}px, ${modalPosition.y}px)` }"
      @wheel.stop
    >
      <button
        @click="close"
        class="absolute top-4 right-4 bg-red-100 hover:bg-red-200 text-red-500 hover:text-red-900 z-10 w-7 h-7 rounded-full flex items-center justify-center shadow-sm transition-colors"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2.5"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div
        class="w-full md:w-1/4 bg-transparent border-b md:border-b-0 md:border-r border-gray-100 p-3 flex flex-col md:flex-col shrink-0 cursor-move glass-panel"
        @mousedown="onMouseDown"
      >
        <h3 class="text-xl font-bold text-gray-900 mb-3 md:mb-4 px-2">{{ $t('settings.title') }}</h3>
        <nav
          ref="navRef"
          class="flex flex-row md:flex-col gap-1 md:gap-0 md:space-y-0.5 overflow-x-auto md:overflow-visible pb-1 md:pb-0 no-drag cursor-grab active:cursor-grabbing overscroll-contain"
          @mousedown="onNavMouseDown"
          @mousemove="onNavMouseMove"
          @mouseup="onNavMouseUp"
          @mouseleave="onNavMouseUp"
          @wheel.stop.passive="handleNavWheel"
        >
          <button
            @click="activeTab = 'style'"
            :class="
              activeTab === 'style'
                ? 'selected-outline text-gray-900'
                : 'border border-transparent text-gray-600 hover:bg-gray-50'
            "
            class="whitespace-nowrap md:whitespace-normal w-auto md:w-full shrink-0 text-left px-3 py-1.5 rounded-lg text-sm transition-colors"
          >
            {{ $t('settings.tabs.style') }}
          </button>
          <button
            @click="activeTab = 'widgets'"
            :class="
              activeTab === 'widgets'
                ? 'selected-outline text-gray-900'
                : 'border border-transparent text-gray-600 hover:bg-gray-50'
            "
            class="whitespace-nowrap md:whitespace-normal w-auto md:w-full shrink-0 text-left px-3 py-1.5 rounded-lg text-sm transition-colors"
          >
            {{ $t('settings.tabs.widgets') }}
          </button>

          <button
            @click="activeTab = 'universal-window'"
            :class="
              activeTab === 'universal-window'
                ? 'selected-outline text-gray-900'
                : 'border border-transparent text-gray-600 hover:bg-gray-50'
            "
            class="whitespace-nowrap md:whitespace-normal w-auto md:w-full shrink-0 text-left px-3 py-1.5 rounded-lg text-sm transition-colors"
          >
            {{ $t('settings.tabs.universalWindow') }}
          </button>
          <button
            @click="activeTab = 'docker'"
            :class="
              activeTab === 'docker'
                ? 'selected-outline text-gray-900'
                : 'border border-transparent text-gray-600 hover:bg-gray-50'
            "
            class="whitespace-nowrap md:whitespace-normal w-auto md:w-full shrink-0 text-left px-3 py-1.5 rounded-lg text-sm transition-colors"
          >
            {{ $t('settings.tabs.docker') }}
          </button>
          <button
            @click="activeTab = 'account'"
            :class="
              activeTab === 'account'
                ? 'selected-outline text-gray-900'
                : 'border border-transparent text-gray-600 hover:bg-gray-50'
            "
            class="whitespace-nowrap md:whitespace-normal w-auto md:w-full shrink-0 text-left px-3 py-1.5 rounded-lg text-sm transition-colors"
          >
            {{ $t('settings.tabs.account') }}
          </button>
          <button
            @click="activeTab = 'network'"
            :class="[
              'px-3 py-1.5 text-sm transition-colors text-left flex items-center gap-1.5',
              activeTab === 'network'
                ? 'selected-outline text-gray-900'
                : 'border border-transparent text-gray-600 hover:bg-gray-50',
            ]"
            class="whitespace-nowrap md:whitespace-normal w-auto md:w-full shrink-0 rounded-lg"
          >
            {{ $t('settings.tabs.network') }}
          </button>
          <button
            @click="activeTab = 'lucky-stun'"
            :class="
              activeTab === 'lucky-stun'
                ? 'selected-outline text-gray-900'
                : 'border border-transparent text-gray-600 hover:bg-gray-50'
            "
            class="whitespace-nowrap md:whitespace-normal w-auto md:w-full shrink-0 text-left px-3 py-1.5 rounded-lg text-sm transition-colors"
          >
            {{ $t('settings.tabs.luckyStun') }}
          </button>
          <button
            @click="activeTab = 'about'"
            :class="
              activeTab === 'about'
                ? 'selected-outline text-gray-900'
                : 'border border-transparent text-red-500 hover:bg-red-50 font-medium'
            "
            class="whitespace-nowrap md:whitespace-normal w-auto md:w-full shrink-0 text-left px-3 py-1.5 rounded-lg text-sm transition-colors"
          >
            {{ $t('settings.tabs.about') }}
          </button>
          <button
            @click="activeTab = 'language'"
            :class="
              activeTab === 'language'
                ? 'selected-outline text-gray-900'
                : 'border border-transparent text-gray-600 hover:bg-gray-50'
            "
            class="whitespace-nowrap md:whitespace-normal w-auto md:w-full shrink-0 text-left px-3 py-1.5 rounded-lg text-sm transition-colors"
          >
            {{ $t('settings.tabs.language') }}
          </button>
        </nav>
        <div v-if="iconSrc" class="mt-auto px-3 pb-3 hidden md:flex justify-center">
          <img :src="iconSrc" class="w-1/4 h-auto rounded-lg shadow-sm" alt="Custom Icon" />
        </div>
      </div>

      <div class="flex-1 flex flex-col bg-transparent overflow-hidden glass-panel">
        <div class="flex-1 p-3 overflow-y-auto overscroll-contain" @wheel.stop>
          <StylePanel />
          <WidgetsPanel />
          <DockerPanel />
          <UniversalWindowPanel />
          <NetworkPanel />
          <LuckyStunPanel />
          <AccountPanel />
          <AboutPanel />
          <LanguagePanel />
        </div>
      </div>
    </div>
  </OverlayMotion>
  <PasswordConfirmModal
    v-model:show="showPasswordConfirm"
    :title="confirmTitle"
    :on-success="onAuthSuccess"
  />

  <!-- Multi-User Warning Modal -->
  <OverlayMotion
    :show="showMultiUserWarning"
    :z-index="80"
    overlay-class="bg-black/40 backdrop-blur-sm p-4 pt-[calc(1rem+env(safe-area-inset-top))] pb-[calc(1rem+env(safe-area-inset-bottom))]"
    panel-class="max-w-sm"
  >
    <div class="bg-white rounded-xl shadow-xl p-6 w-full border border-gray-100">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-2xl">
          !
        </div>
        <h3 class="text-base font-bold text-gray-900">{{ $t('settings.extraSections.switchModeWarning') }}</h3>
      </div>

      <p class="text-sm text-gray-600 mb-6 leading-relaxed">
        请先导出配置！<br />
        切换到多用户模式会导致当前单用户配置丢失（数据隔离），是否确认继续？
      </p>

      <div class="flex gap-3">
        <button
          @click="showMultiUserWarning = false"
          class="flex-1 px-4 py-2.5 min-h-[44px] bg-gray-100 text-gray-600 rounded-lg text-sm font-bold hover:bg-gray-200 transition-colors"
        >
          取消
        </button>
        <button
          @click="
            showMultiUserWarning = false;
            requestAuth(() => performAuthModeSwitch('multi'), t('settings.messages.confirmSwitchAuth'));
          "
          class="flex-1 px-4 py-2.5 min-h-[44px] bg-gray-900 text-white rounded-lg text-sm font-bold hover:bg-gray-800 transition-colors shadow-md"
        >
          确认切换
        </button>
      </div>
    </div>
  </OverlayMotion>

  <!-- Delete Confirmation Modal -->
  <OverlayMotion
    :show="showDeleteWidgetConfirm"
    :z-index="70"
    overlay-class="bg-black/20 backdrop-blur-sm p-4 pt-[calc(1rem+env(safe-area-inset-top))] pb-[calc(1rem+env(safe-area-inset-bottom))]"
    panel-class="max-w-sm"
  >
    <div class="bg-white rounded-xl shadow-xl p-6 w-full border border-gray-100">
      <h3 class="text-base font-bold text-gray-900 mb-2">{{ $t('settings.extraSections.confirmDeleteTitle') }}</h3>
      <p class="text-sm text-gray-500 mb-6">{{ $t('settings.extraSections.confirmDeleteWindowDesc') }}</p>
      <div class="flex gap-3">
        <button
          @click="showDeleteWidgetConfirm = false"
          class="flex-1 px-4 py-2 min-h-[44px] bg-gray-100 text-gray-600 rounded-lg text-sm font-bold hover:bg-gray-200 transition-colors"
        >
          取消
        </button>
        <button
          @click="confirmRemoveWidget"
          class="flex-1 px-4 py-2 min-h-[44px] bg-gray-900 text-white rounded-lg text-sm font-bold hover:bg-gray-800 transition-colors"
        >
          删除
        </button>
      </div>
    </div>
  </OverlayMotion>

  <OverlayMotion
    :show="showRenameModal"
    :z-index="90"
    overlay-class="bg-black/40 backdrop-blur-sm p-4 pt-[calc(1rem+env(safe-area-inset-top))] pb-[calc(1rem+env(safe-area-inset-bottom))]"
    panel-class="max-w-sm"
  >
    <div class="bg-white rounded-xl shadow-xl w-full p-4 border border-gray-100">
      <div class="text-base font-bold text-gray-900">修改昵称</div>
      <div class="text-xs text-gray-500 mt-1">将同步更新到道理鱼音乐账户资料</div>

      <input
        v-model="newDisplayName"
        type="text"
        class="mt-3 w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-gray-900 outline-none"
        placeholder="请输入新的昵称"
        @keyup.enter="updateDisplayName"
      />

      <div class="mt-4 flex justify-end gap-2">
        <button
          @click="showRenameModal = false"
          class="px-4 py-2 min-h-[44px] text-gray-600 hover:bg-gray-100 rounded-lg text-sm transition-colors"
        >
          取消
        </button>
        <button
          @click="updateDisplayName"
          :disabled="isUpdatingProfile"
          class="px-4 py-2 min-h-[44px] bg-gray-900 text-white rounded-lg text-sm font-bold hover:bg-gray-800 disabled:opacity-50 transition-colors"
        >
          {{ isUpdatingProfile ? "保存中..." : "保存" }}
        </button>
      </div>
    </div>
  </OverlayMotion>

</template>

<style scoped>
.night-settings {
  color: #f8fafc;
}
.night-settings :deep(.bg-white\/90), .night-settings :deep(.bg-white\/80), .night-settings :deep(.bg-white\/70), .night-settings :deep(.bg-white\/60), .night-settings :deep(.bg-white), .night-settings :deep(.bg-gray-50), .night-settings :deep(.bg-gray-100), .night-settings :deep(.bg-white\/90):hover, .night-settings :deep(.bg-white\/80):hover, .night-settings :deep(.bg-white\/70):hover, .night-settings :deep(.bg-white\/60):hover, .night-settings :deep(.bg-white):hover, .night-settings :deep(.bg-gray-50):hover, .night-settings :deep(.bg-gray-100):hover {
  background-color: rgba(15, 23, 42, 0.55) !important;
  backdrop-filter: blur(12px);
}
/* 夜间模式：侧栏等使用 hover:bg-gray-50 的按钮悬停时用深色背景，避免与浅色文字同色 */ .night-settings :deep(.hover\:bg-gray-50):hover, .night-settings :deep(.hover\:bg-gray-100):hover {
  background-color: rgba(15, 23, 42, 0.55) !important;
  backdrop-filter: blur(8px);
}
.night-settings :deep(.text-gray-900), .night-settings :deep(.text-gray-800), .night-settings :deep(.text-gray-700), .night-settings :deep(.text-gray-600), .night-settings :deep(.text-gray-500), .night-settings :deep(.text-gray-400) {
  color: #f8fafc !important;
  text-shadow: 0 0 2px rgba(255, 255, 255, 0.6);
}
.night-settings :deep(.border-gray-100), .night-settings :deep(.border-gray-200), .night-settings :deep(.border-gray-300), .night-settings :deep(.border-gray-400) {
  border-color: rgba(255, 255, 255, 0.12) !important;
}
.night-settings :deep(input::placeholder), .night-settings :deep(textarea::placeholder) {
  color: rgba(248, 250, 252, 0.6);
}
.night-settings :deep(.glass-panel), .night-settings :deep(.glass-card), .night-settings :deep(.glass-chip) {
  color: #f8fafc;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.55);
}
</style>

<!-- 面板拆成子组件后，普通类名（非 :deep）匹配不到父组件的 scope id，故放全局 -->
<style>
.glass-panel, .glass-card, .glass-chip {
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.glass-chip:hover {
  background-color: rgba(255, 255, 255, 0.12);
}
.selected-outline {
  border: 2px solid rgba(255, 255, 255, 0.95);
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.12);
  font-weight: 700;
}
.selectable-outline:focus-visible, .selectable-outline:active {
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.95);
}
</style>

