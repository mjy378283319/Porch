<script setup lang="ts">
// 该面板由 SettingsModal.vue 拆分而来：模板保持原样，状态通过 inject 取父级上下文。
import { inject, toRef } from "vue";
import { SETTINGS_CTX } from "./context";

const ctx = inject(SETTINGS_CTX) as Record<string, any>;

const LOCALE_FLAGS = toRef(ctx, "LOCALE_FLAGS");
const LOCALE_LABELS = toRef(ctx, "LOCALE_LABELS");
const activeTab = toRef(ctx, "activeTab");
const i18nStore = toRef(ctx, "i18nStore");
</script>

<template>
          <div v-if="activeTab === 'language'" class="space-y-4">
            <div class="bg-white/60 border border-gray-100 rounded-xl p-4">
              <h4 class="text-base font-bold mb-4 text-gray-900">{{ $t('settings.language.title') }}</h4>
              <div class="space-y-3">
                <div
                  v-for="locale in i18nStore.availableLocales"
                  :key="locale"
                  @click="i18nStore.setLocale(locale, true)"
                  :class="[
                    'flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all border',
                    i18nStore.currentLocale === locale
                      ? 'bg-gray-900 text-white border-gray-900'
                      : 'bg-white border-gray-200 hover:border-gray-400'
                  ]"
                >
                  <div class="flex items-center gap-3">
                    <span class="text-lg">{{ LOCALE_FLAGS[locale] }}</span>
                    <span class="font-medium">{{ LOCALE_LABELS[locale] }}</span>
                  </div>
                  <svg
                    v-if="i18nStore.currentLocale === locale"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    class="w-5 h-5"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </div>
              </div>
              <p class="mt-4 text-xs text-gray-500">
                 {{ $t('settings.language.tip') }}
               </p>
            </div>
          </div>
</template>
