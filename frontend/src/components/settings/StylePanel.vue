<script setup lang="ts">
// 该面板由 SettingsModal.vue 拆分而来：模板保持原样，状态通过 inject 取父级上下文。
import { inject, toRef } from "vue";
import { SETTINGS_CTX } from "./context";

const ctx = inject(SETTINGS_CTX) as Record<string, any>;

const activeTab = toRef(ctx, "activeTab");
const daylightMaskPercent = toRef(ctx, "daylightMaskPercent");
const handleWallpaperSelect = toRef(ctx, "handleWallpaperSelect");
const setSolidColorAsWallpaper = toRef(ctx, "setSolidColorAsWallpaper");
const showWallpaperLibrary = toRef(ctx, "showWallpaperLibrary");
const solidBackgroundColorProxy = toRef(ctx, "solidBackgroundColorProxy");
const store = toRef(ctx, "store");

import IconUploader from "../IconUploader.vue";
import WallpaperLibrary from "../WallpaperLibrary.vue";
</script>

<template>
          <div v-if="activeTab === 'style'" class="space-y-4">
            <div class="bg-white/60 border border-gray-100 rounded-xl p-4">
              <h4 class="text-base font-bold mb-4 text-gray-900">{{ $t('settings.sections.basicInfo') }}</h4>
              <div class="space-y-2">
                <div>
                  <label class="text-sm font-medium text-gray-700 mb-1 block">{{ $t('settings.sections.siteTitle') }}</label>
                  <input
                    v-model="store.appConfig.customTitle"
                    type="text"
                    class="w-full px-2 py-2 border border-gray-200 rounded-xl focus:border-gray-900 outline-none text-sm"
                  />
                </div>
                <div>
                  <label class="text-sm font-medium text-gray-700 mb-1 block">{{ $t('settings.sections.backgroundImage') }}</label>
                  <div class="border border-gray-200 rounded-xl p-2 bg-white/60">
                    <IconUploader
                      v-model="store.appConfig.background"
                      @update:modelValue="store.markDirty()"
                      :crop="false"
                      :previewStyle="{
                        filter: `blur(${store.appConfig.backgroundBlur ?? 0}px)`,
                        transform: 'scale(1.1)',
                      }"
                      :overlayStyle="{
                        backgroundColor: `rgba(0,0,0,${store.appConfig.backgroundMask ?? 0})`,
                      }"
                    />
                    <div class="mt-2 flex justify-between items-center">
                      <button
                        v-if="store.appConfig.background"
                        @click="
                          store.appConfig.background = '';
                          store.markDirty();
                        "
                        class="text-xs text-red-500 hover:text-red-600 px-2 py-1 rounded bg-red-50 hover:bg-red-100 transition-colors"
                      >
                        清除背景
                      </button>
                      <button
                        @click="showWallpaperLibrary = true"
                        class="text-xs text-blue-600 hover:text-blue-700 font-bold flex items-center gap-1 ml-auto px-2 py-1 rounded bg-blue-50 hover:bg-blue-100 transition-colors"
                      >
                        {{ $t('settings.sections.manageWallpaperLibrary') }}
                      </button>
                    </div>
                  </div>
                </div>
                <div class="space-y-2">
                  <div class="flex items-center justify-between rounded-xl border border-gray-100 bg-white/70 px-3 py-2">
                    <div class="flex flex-col">
                      <span class="text-sm font-medium text-gray-700">{{ $t('settings.sections.dayMode') }}</span>
                      <span class="text-[11px] text-gray-400"
                        >{{ $t('settings.sections.dayModeDesc') }}
                        {{ daylightMaskPercent }}%</span
                      >
                    </div>
                    <div class="flex items-center gap-2">
                      <div
                        class="flex items-center gap-1 px-2 py-1 rounded-lg border border-gray-200 bg-white/80 text-gray-700"
                      >
                        <input
                          v-model.number="daylightMaskPercent"
                          type="number"
                          min="0"
                          max="100"
                          step="1"
                          class="w-12 text-xs bg-transparent outline-none"
                        />
                        <span class="text-xs">%</span>
                      </div>
                      <label class="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          class="sr-only peer"
                          :checked="store.appConfig.daylightModeEnabled"
                          @change="
                            (e) => {
                              store.appConfig.daylightModeEnabled = (
                                e.target as HTMLInputElement
                              ).checked;
                              store.markDirty();
                            }
                          "
                        />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-yellow-400"
                        ></div>
                      </label>
                    </div>
                  </div>
                  <div class="flex items-center justify-between rounded-xl border border-gray-100 bg-white/70 px-3 py-2">
                    <div class="flex flex-col">
                      <span class="text-sm font-medium text-gray-700">{{ $t('settings.sections.weatherEffect') }}</span>
                      <span class="text-[11px] text-gray-400">{{ $t('settings.sections.weatherEffectDesc') }}</span>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        class="sr-only peer"
                        :checked="store.appConfig.weatherEffectEnabled"
                        @change="
                          (e) => {
                            store.appConfig.weatherEffectEnabled = (
                              e.target as HTMLInputElement
                            ).checked;
                            store.markDirty();
                          }
                        "
                      />
                      <div
                        class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"
                      ></div>
                    </label>
                  </div>
                </div>
                <div>
                  <label class="text-sm font-medium text-gray-700 mb-1 block">{{ $t('settings.sections.solidColor') }}</label>
                  <div class="flex items-center gap-2">
                    <input
                      type="color"
                      v-model="solidBackgroundColorProxy"
                      class="w-10 h-10 rounded cursor-pointer border-0 p-0"
                    />
                    <input
                      v-model="store.appConfig.solidBackgroundColor"
                      @change="store.markDirty()"
                      type="text"
                      placeholder="#f3f4f6"
                      class="flex-1 px-2 py-2 border border-gray-200 rounded-xl focus:border-gray-900 outline-none text-sm"
                    />
                    <button
                      @click="
                        store.appConfig.solidBackgroundColor = '';
                        store.markDirty();
                      "
                      class="px-3 h-8 rounded-lg bg-red-50 hover:bg-red-100 flex items-center justify-center text-red-500 transition-colors text-xs font-medium"
                      :title="$t('settings.extraSections.clearSolidBg')"
                    >
                      {{ $t('settings.extraSections.resetBtn') }}
                    </button>
                    <button
                      @click="setSolidColorAsWallpaper"
                      class="px-3 h-8 rounded-lg bg-blue-50 hover:bg-blue-100 flex items-center justify-center text-blue-600 transition-colors text-xs font-medium"
                      :title="$t('settings.sections.setAsWallpaper')"
                    >
                      {{ $t('settings.sections.setAsWallpaper') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <WallpaperLibrary v-model:show="showWallpaperLibrary" @select="handleWallpaperSelect" />

            <div class="bg-white/60 border border-gray-100 rounded-xl p-4">
              <h4 class="text-base font-bold mb-4 text-gray-900">{{ $t('settings.sections.layout') }}</h4>
              <div class="mb-2">
                <h5 class="text-sm font-medium text-gray-700 mb-2">{{ $t('settings.sections.topBarLayout') }}</h5>
                <div class="flex gap-2">
                  <button
                    @click="store.appConfig.titleAlign = 'left'"
                    class="flex-1 p-2 border-2 rounded-xl flex items-center justify-center gap-2 transition-colors"
                    :class="
                      store.appConfig.titleAlign === 'left'
                        ? 'selected-outline text-gray-900'
                        : 'border-gray-200 text-gray-500 bg-white hover:bg-gray-50'
                    "
                  >
                    <span class="text-sm">{{ $t('settings.sections.standardLayout') }}</span>
                  </button>
                  <button
                    @click="store.appConfig.titleAlign = 'right'"
                    class="flex-1 p-2 border-2 rounded-xl flex items-center justify-center gap-2 transition-colors"
                    :class="
                      store.appConfig.titleAlign === 'right'
                        ? 'selected-outline text-gray-900'
                        : 'border-gray-200 text-gray-500 bg-white hover:bg-gray-50'
                    "
                  >
                    <span class="text-sm">{{ $t('settings.sections.invertedLayout') }}</span>
                  </button>
                  <button
                    @click="
                      store.appConfig.hideHeaderOnMobile = !store.appConfig.hideHeaderOnMobile
                    "
                    class="flex flex-1 p-2 border-2 rounded-xl items-center justify-center gap-2 transition-colors"
                    :class="
                      store.appConfig.hideHeaderOnMobile
                        ? 'selected-outline text-gray-900'
                        : 'border-gray-200 text-gray-500 bg-white hover:bg-gray-50'
                    "
                  >
                    <span class="text-sm">{{ $t('settings.sections.hideHeaderOnMobile') }}</span>
                  </button>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4 mb-2">
                <div>
                  <h4 class="text-sm font-medium text-gray-700 mb-1">{{ $t('settings.sections.titleSizeLabel') }}</h4>
                  <input
                    type="range"
                    v-model.number="store.appConfig.titleSize"
                    min="20"
                    max="80"
                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-400"
                  />
                </div>
                <div>
                  <h4 class="text-sm font-medium text-gray-700 mb-1">{{ $t('settings.sections.titleColorLabel') }}</h4>
                  <div class="flex items-center gap-2">
                    <input
                      type="color"
                      v-model="store.appConfig.titleColor"
                      class="w-10 h-10 rounded cursor-pointer border-0 p-0"
                    />
                    <button
                      @click="store.appConfig.titleColor = '#ffffff'"
                      class="px-3 h-8 rounded-lg bg-red-50 hover:bg-red-100 flex items-center justify-center text-red-500 transition-colors text-xs font-medium"
                      :title="$t('settings.extraSections.resetColor')"
                    >
                      {{ $t('settings.extraSections.resetBtn') }}
                    </button>
                  </div>
                </div>
              </div>
              <div class="mb-2">
                <h5 class="text-sm font-medium text-gray-700 mb-2">{{ $t('settings.sections.webLayout') }}</h5>
                <div
                  class="flex items-center justify-between border border-gray-200 rounded-xl p-3"
                >
                  <span class="text-sm font-bold text-gray-900">{{ $t('settings.sections.displayMode') }}</span>
                  <div class="flex items-center gap-2">
                    <div
                      class="relative h-9 w-[180px] rounded-full bg-gray-100/90 p-1 flex items-center select-none shadow-inner focus-within:ring-2 focus-within:ring-green-300/60 focus-within:ring-offset-2 focus-within:ring-offset-white/60"
                    >
                      <div
                        class="absolute top-1 bottom-1 left-1 w-[calc(50%-4px)] rounded-full bg-green-500 shadow-sm shadow-green-500/25 transition-transform duration-200"
                        :class="
                          store.appConfig.webGroupPagination
                            ? 'translate-x-[calc(100%+4px)]'
                            : 'translate-x-0'
                        "
                      ></div>
                      <button
                        type="button"
                        class="relative z-10 w-1/2 h-full text-xs font-bold rounded-full transition-colors focus-visible:outline-none"
                        :class="
                          store.appConfig.webGroupPagination
                            ? 'text-gray-600 hover:text-gray-800'
                            : 'text-white'
                        "
                        @click="store.appConfig.webGroupPagination = false"
                      >
                        {{ $t('settings.sections.singleColumn') }}
                      </button>
                      <button
                        type="button"
                        class="relative z-10 w-1/2 h-full text-xs font-bold rounded-full transition-colors focus-visible:outline-none"
                        :class="
                          store.appConfig.webGroupPagination
                            ? 'text-white'
                            : 'text-gray-600 hover:text-gray-800'
                        "
                        @click="store.appConfig.webGroupPagination = true"
                      >
                        {{ $t('settings.sections.pageByGroup') }}
                      </button>
                    </div>
                    <button
                      type="button"
                      class="h-9 px-3 rounded-xl text-xs font-bold border transition-colors focus-visible:outline-none"
                      :disabled="!store.appConfig.webGroupPagination"
                      :class="
                        !store.appConfig.webGroupPagination
                          ? 'bg-gray-50 text-gray-300 border-gray-100 cursor-not-allowed'
                          : store.appConfig.webGroupPaginationDisableFlip
                            ? 'bg-red-500 text-white border-red-500 hover:bg-red-600'
                            : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
                      "
                      @click="
                        store.appConfig.webGroupPaginationDisableFlip =
                          !store.appConfig.webGroupPaginationDisableFlip
                      "
                    >
                      {{ $t('settings.sections.disablePagination') }}
                    </button>
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-4 mt-4">
                <div>
                  <h4 class="text-sm font-medium text-gray-700 mb-1">{{ $t('settings.sections.widgetAreaSize') }}</h4>
                  <div class="flex items-center gap-2">
                    <input
                      type="number"
                      v-model.number="store.appConfig.widgetAreaCols"
                      min="0.5"
                      step="0.5"
                      max="16"
                      class="w-20 px-2 py-2 border border-gray-200 rounded-xl focus:border-gray-900 outline-none text-sm bg-white"
                    />
                    <span class="text-xs text-gray-400 select-none">×</span>
                    <input
                      type="number"
                      v-model.number="store.appConfig.widgetAreaRows"
                      min="0.5"
                      step="0.5"
                      max="16"
                      class="w-20 px-2 py-2 border border-gray-200 rounded-xl focus:border-gray-900 outline-none text-sm bg-white"
                    />
                    <span class="ml-auto text-xs text-gray-500 w-14 text-right"
                      >{{ store.appConfig.widgetAreaCols ?? 4 }}×{{
                        store.appConfig.widgetAreaRows ?? 4
                      }}</span
                    >
                  </div>
                </div>
                <div>
                  <h4 class="text-sm font-medium text-gray-700 mb-1">{{ $t('settings.sections.groupVerticalGap') }}</h4>
                  <div class="flex items-center gap-2">
                    <input
                      type="range"
                      v-model.number="store.appConfig.groupGap"
                      min="0"
                      max="100"
                      step="5"
                      class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-400"
                    />
                    <span class="text-xs text-gray-500 w-6">{{
                      store.appConfig.groupGap ?? 30
                    }}</span>
                  </div>
                </div>
                <div>
                  <h4 class="text-sm font-medium text-gray-700 mb-1">{{ $t('settings.sections.mouseHoverEffect') }}</h4>
                  <select
                    v-model="store.appConfig.mouseHoverEffect"
                    class="w-full px-3 py-2 border border-gray-200 rounded-xl focus:border-gray-900 outline-none text-sm bg-white"
                  >
                    <option value="scale">{{ $t('settings.sections.hoverScale') }}</option>
                    <option value="lift">{{ $t('settings.sections.hoverLift') }}</option>
                    <option value="glow">{{ $t('settings.sections.hoverGlow') }}</option>
                    <option value="none">{{ $t('settings.sections.hoverNone') }}</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="bg-white/60 border border-gray-100 rounded-xl p-4">
              <h4 class="text-base font-bold mb-4 text-gray-900">{{ $t('settings.sections.footerSettings') }}</h4>
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <label class="text-sm font-medium text-gray-700">{{ $t('settings.sections.showVisitorStats') }}</label>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      v-model="store.appConfig.showFooterStats"
                      class="sr-only peer"
                    />
                    <div
                      class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
                    ></div>
                  </label>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="text-sm font-medium text-gray-700 mb-1 block"
                      >{{ $t('settings.sections.footerHeight') }}</label
                    >
                    <div class="text-xs text-gray-500 mb-1">{{ $t('settings.sections.footerHeightDesc') }}</div>
                    <input
                      type="number"
                      v-model="store.appConfig.footerHeight"
                      class="w-full px-3 py-2 border border-gray-200 rounded-xl focus:border-gray-900 outline-none text-sm"
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-700 mb-1 block"
                      >{{ $t('settings.sections.footerContentWidth') }}</label
                    >
                    <div class="text-xs text-gray-500 mb-1">{{ $t('settings.sections.footerContentWidthDesc') }}</div>
                    <input
                      type="number"
                      v-model="store.appConfig.footerWidth"
                      class="w-full px-3 py-2 border border-gray-200 rounded-xl focus:border-gray-900 outline-none text-sm"
                      placeholder="1280"
                    />
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="text-sm font-medium text-gray-700 mb-1 block"
                      >{{ $t('settings.sections.footerMarginBottom') }}</label
                    >
                    <div class="text-xs text-gray-500 mb-1">{{ $t('settings.sections.footerMarginBottomDesc') }}</div>
                    <input
                      type="number"
                      v-model="store.appConfig.footerMarginBottom"
                      class="w-full px-3 py-2 border border-gray-200 rounded-xl focus:border-gray-900 outline-none text-sm"
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-700 mb-1 block"
                      >{{ $t('settings.sections.footerFontSize') }}</label
                    >
                    <div class="text-xs text-gray-500 mb-1">{{ $t('settings.sections.footerFontSizeDesc') }}</div>
                    <input
                      type="number"
                      v-model="store.appConfig.footerFontSize"
                      class="w-full px-3 py-2 border border-gray-200 rounded-xl focus:border-gray-900 outline-none text-sm"
                      placeholder="12"
                    />
                  </div>
                </div>
                <div>
                  <label class="text-sm font-medium text-gray-700 mb-1 block"
                    >{{ $t('settings.sections.customFooterHtml') }}</label
                  >
                  <textarea
                    v-model="store.appConfig.footerHtml"
                    rows="3"
                    :placeholder="$t('settings.sections.customFooterHtmlPlaceholder')"
                    class="w-full px-3 py-2 border border-gray-200 rounded-xl focus:border-gray-900 outline-none text-sm font-mono"
                  ></textarea>
                </div>
              </div>
            </div>
          </div>

</template>
