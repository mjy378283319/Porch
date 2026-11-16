import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import type { SupportedLocale } from "@/plugins/i18n";
import { SUPPORTED_LOCALES, DEFAULT_LOCALE, getI18n } from "@/plugins/i18n";

export type { SupportedLocale } from "@/plugins/i18n";

/**
 * i18n 状态管理 Store
 * - 维护当前语言状态
 * - 按需动态加载语言包（import() 异步模块）
 * - 持久化到 localStorage
 */
export const useI18nStore = defineStore("i18n", () => {
  // Pinia setup store 不在 Vue 组件上下文中，不能调用 useI18n()，
  // 需要通过模块级单例 getI18n() 获取 i18n 实例
  const i18n = getI18n();

  const currentLocale = ref<SupportedLocale>(DEFAULT_LOCALE);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const availableLocales = computed(() => [...SUPPORTED_LOCALES]);

  const isRTL = computed(() => false);

  /**
   * 自用版固定简体中文。保留接口签名，避免其它调用点改动。
   */
  async function setLocale(_locale: SupportedLocale, _persist = false) {
    currentLocale.value = DEFAULT_LOCALE;
    const localeRef = i18n.locale;
    if (typeof localeRef !== "string") {
      (localeRef as { value: string }).value = DEFAULT_LOCALE;
    }
    localStorage.removeItem("porch-locale");
    loading.value = false;
    error.value = null;
  }

  /**
   * 清掉旧版本残留的语言选择，固定中文。
   */
  function initLocale(_savedLocale?: string) {
    void setLocale(DEFAULT_LOCALE, false);
  }

  return {
    currentLocale,
    loading,
    error,
    availableLocales,
    isRTL,
    setLocale,
    initLocale,
  };
});

/**
 * Composable 封装：便捷访问 i18n 实例
 */
export function useAppI18n() {
  const i18n = useI18n();
  const store = useI18nStore();

  return {
    t: i18n.t,
    locale: i18n.locale,
    currentLocale: store.currentLocale,
    availableLocales: store.availableLocales,
    setLocale: store.setLocale,
    loading: store.loading,
  };
}
