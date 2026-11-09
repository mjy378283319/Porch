<script setup lang="ts">
// 该面板由 SettingsModal.vue 拆分而来：模板保持原样，状态通过 inject 取父级上下文。
import { inject, toRef } from "vue";
import { SETTINGS_CTX } from "./context";

const ctx = inject(SETTINGS_CTX) as Record<string, any>;

const DEFAULT_LATENCY_THRESHOLD_MS = toRef(ctx, "DEFAULT_LATENCY_THRESHOLD_MS");
const activeTab = toRef(ctx, "activeTab");
const applyLatencyThreshold = toRef(ctx, "applyLatencyThreshold");
const latencyThresholdAppliedToast = toRef(ctx, "latencyThresholdAppliedToast");
const latencyThresholdDraft = toRef(ctx, "latencyThresholdDraft");
const latencyThresholdTouched = toRef(ctx, "latencyThresholdTouched");
const latencyThresholdValidation = toRef(ctx, "latencyThresholdValidation");
const onLatencyThresholdBlur = toRef(ctx, "onLatencyThresholdBlur");
const onLatencyThresholdInput = toRef(ctx, "onLatencyThresholdInput");
const resetLatencyThreshold = toRef(ctx, "resetLatencyThreshold");
const store = toRef(ctx, "store");
const toggleWhitelistLatency = toRef(ctx, "toggleWhitelistLatency");
const whitelistLatencyEnabled = toRef(ctx, "whitelistLatencyEnabled");
</script>

<template>
          <div v-if="activeTab === 'network'" class="p-4 space-y-4">
            <div class="flex items-center gap-3 mb-4">
              <h4 class="text-base font-bold text-gray-900 border-l-4 border-gray-900 pl-3">
                {{ $t('settings.extraSections.networkDetectionSettings') }}
              </h4>
            </div>

            <div class="bg-gray-50 border border-gray-100 rounded-xl p-4 space-y-3">
              <div class="flex items-start gap-2">
                <span
                  class="text-xs text-gray-500 font-medium border border-gray-200 rounded px-1.5 py-0.5 mt-0.5"
                  >注</span
                >
                <p class="text-xs text-gray-600 leading-relaxed">
                  {{ $t('settings.extraSections.domainWhitelistHint') }}
                </p>
              </div>

              <div class="space-y-2">
                <label class="block text-sm font-medium text-gray-700">{{ $t('settings.extraSections.domainWhitelist') }}</label>
                <textarea
                  v-model="store.appConfig.internalDomains"
                  @change="store.markDirty()"
                  rows="5"
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg text-xs focus:border-gray-900 outline-none font-mono"
                  :placeholder="$t('settings.extraSections.placeholderDomainWhitelist')"
                ></textarea>
              </div>
            </div>

            <div class="bg-gray-50 border border-gray-100 rounded-xl p-4">
              <h5 class="text-sm font-medium text-gray-700 mb-3">{{ $t('settings.extraSections.whitelistLatencyMode') }}</h5>
              <div class="flex items-center gap-3 mb-3">
                <button
                  type="button"
                  @click="toggleWhitelistLatency"
                  class="px-3 py-1.5 rounded-lg text-xs font-bold transition-colors border whitespace-nowrap"
                  :class="
                    whitelistLatencyEnabled
                      ? 'bg-blue-50 text-blue-600 border-blue-200 hover:bg-blue-100'
                      : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
                  "
                >
                  {{ whitelistLatencyEnabled ? $t('settings.extraSections.whitelistLatencyEnabled') : $t('settings.extraSections.enableWhitelistLatency') }}
                </button>
                <span class="text-[11px] text-gray-500">
                  {{ whitelistLatencyEnabled ? $t('settings.extraSections.whitelistLatencyDesc') : $t('settings.extraSections.whitelistLatencyDisabledDesc') }}
                </span>
              </div>
              <div v-if="whitelistLatencyEnabled" class="flex items-center gap-2">
                <input
                  :value="latencyThresholdDraft"
                  inputmode="numeric"
                  @input="onLatencyThresholdInput"
                  @blur="onLatencyThresholdBlur"
                  @keydown.enter.prevent="applyLatencyThreshold"
                  placeholder="20–30000"
                  class="w-32 px-3 py-2 border rounded-lg text-xs outline-none font-mono focus:border-gray-900"
                  :class="
                    latencyThresholdTouched && !latencyThresholdValidation.ok
                      ? 'border-red-300'
                      : 'border-gray-200'
                  "
                />
                <span class="text-xs text-gray-500">ms</span>
                <button
                  type="button"
                  @click="applyLatencyThreshold"
                  :disabled="!latencyThresholdValidation.ok"
                  class="px-3 py-2 rounded-lg text-xs font-bold transition-colors whitespace-nowrap"
                  :class="
                    latencyThresholdValidation.ok
                      ? 'bg-blue-600 text-white hover:bg-blue-500'
                      : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  "
                >
                  {{ $t('settings.extraSections.confirmApplyDefaults') }}
                </button>
                <button
                  type="button"
                  @click="resetLatencyThreshold"
                  class="px-3 py-2 bg-white text-gray-600 border border-gray-200 rounded-lg text-xs font-bold hover:bg-gray-50 transition-colors whitespace-nowrap"
                >
                  {{ $t('settings.extraSections.resetToDefault') }}
                </button>
                <div class="text-[10px] text-gray-400">
                  {{ $t('settings.extraSections.defaultLatency', { ms: DEFAULT_LATENCY_THRESHOLD_MS }) }}
                </div>
              </div>
              <p
                v-if="latencyThresholdTouched && !latencyThresholdValidation.ok"
                class="mt-2 text-[11px] text-red-600"
              >
                {{ latencyThresholdValidation.error }}
              </p>
              <p v-else-if="latencyThresholdAppliedToast" class="mt-2 text-[11px] text-green-600">
                {{ latencyThresholdAppliedToast }}
              </p>
              <p v-else class="mt-2 text-[11px] text-gray-500">
                {{ $t('settings.extraSections.latencyThresholdDesc', { ms: DEFAULT_LATENCY_THRESHOLD_MS }) }}
              </p>
            </div>
          </div>

</template>
