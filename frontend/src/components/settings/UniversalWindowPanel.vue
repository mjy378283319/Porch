<script setup lang="ts">
// 该面板由 SettingsModal.vue 拆分而来：模板保持原样，状态通过 inject 取父级上下文。
import { inject, toRef } from "vue";
import { SETTINGS_CTX } from "./context";

const ctx = inject(SETTINGS_CTX) as Record<string, any>;

const activeTab = toRef(ctx, "activeTab");
const addAmapWeatherWidget = toRef(ctx, "addAmapWeatherWidget");
const addCountUpWidget = toRef(ctx, "addCountUpWidget");
const addCountdownWidget = toRef(ctx, "addCountdownWidget");
const addIframeWidget = toRef(ctx, "addIframeWidget");
const confirmTempInput = toRef(ctx, "confirmTempInput");
const removeWidget = toRef(ctx, "removeWidget");
const store = toRef(ctx, "store");
const tempInputs = toRef(ctx, "tempInputs");
const updateTempInput = toRef(ctx, "updateTempInput");

import ProxyToggle from "../ProxyToggle.vue";
</script>

<template>
          <div v-if="activeTab === 'universal-window'" class="space-y-4">
            <!-- Universal Window Widget Section -->
            <div class="flex items-center justify-between mb-4 border-b border-gray-100 pb-4">
              <div class="flex items-center gap-2">
                <h4 class="text-base font-bold text-gray-900 border-l-4 border-gray-900 pl-3">
                  {{ $t('settings.extraSections.universalWindow') }}
                </h4>
                <span class="text-xs text-gray-500 px-2 py-1 rounded-full glass-chip selected-outline">{{ $t('settings.extraSections.multiOpen') }}</span>
                <button
                  @click="addIframeWidget"
                  class="px-3 py-1.5 text-xs font-medium text-gray-900 rounded-lg transition-colors flex items-center gap-1 ml-2 glass-chip selectable-outline"
                >
                  <span class="text-base leading-none">+</span> {{ $t('settings.extraSections.addWindow') }}
                </button>
              </div>
            </div>

            <template v-for="w in store.widgets" :key="'iframe-' + w.id">
              <div
                v-if="w.type === 'iframe'"
                class="flex flex-col gap-3 p-4 border border-gray-100 rounded-xl hover:shadow-md transition-all glass-card"
              >
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-4">
                    <div
                      class="w-10 h-10 rounded-full bg-white flex items-center justify-center text-sm font-medium text-gray-700 shadow-sm"
                    >
                      {{ $t('settings.widgetAbbr.iframe') }}
                    </div>
                    <div class="flex flex-col">
                      <span class="font-bold text-gray-700">{{ $t('settings.extraSections.universalWindow') }}</span>
                      <span class="text-[10px] text-gray-400 font-mono">ID: {{ w.id }}</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-6">
                    <button
                      @click="removeWidget(w.id)"
                      class="text-red-400 hover:text-red-600 text-xs underline px-2"
                      :title="$t('settings.extraSections.deleteWindow')"
                    >
                      {{ $t('settings.extraSections.modalDelete') }}
                    </button>
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-[10px] text-gray-400 font-medium">{{ $t('settings.sections.publicAccess') }}</span
                      ><label class="relative inline-flex items-center cursor-pointer"
                        ><input
                          type="checkbox"
                          v-model="w.isPublic"
                          class="sr-only peer"
                          @change="store.markDirty()" />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"
                        ></div
                      ></label>
                    </div>
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-[10px] text-gray-400 font-medium">{{ $t('settings.sections.mobileAccess') }}</span
                      ><label class="relative inline-flex items-center cursor-pointer"
                        ><input
                          type="checkbox"
                          :checked="!w.hideOnMobile"
                          class="sr-only peer"
                          @change="
                            (e) => {
                              w.hideOnMobile = !(e.target as HTMLInputElement).checked;
                              store.markDirty();
                            }
                          " />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-orange-500"
                        ></div
                      ></label>
                    </div>
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-[10px] text-gray-400 font-medium">{{ $t('settings.sections.enabled') }}</span
                      ><label class="relative inline-flex items-center cursor-pointer"
                        ><input
                          type="checkbox"
                          v-model="w.enable"
                          class="sr-only peer"
                          @change="store.markDirty()" />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-500"
                        ></div
                      ></label>
                    </div>
                  </div>
                </div>
                <div class="w-full bg-white/60 p-3 rounded-lg border border-gray-100 space-y-3">
                  <div>
                    <div class="flex justify-between items-center mb-1">
                      <label class="block text-xs font-bold text-gray-600"
                        >{{ $t('settings.extraSections.publicNetworkUrl') }}</label
                      >
                      <ProxyToggle v-model="w.data.useProxy" @update:model-value="store.markDirty()" />
                    </div>
                    <div class="flex gap-2">
                      <input
                        :value="tempInputs[`${w.id}-url`] ?? w.data.url"
                        @input="
                          (e: Event) =>
                            updateTempInput(`${w.id}-url`, (e.target as HTMLInputElement).value)
                        "
                        type="url"
                        :placeholder="$t('settings.extraSections.placeholderExampleUrl')"
                        class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-xs focus:border-gray-900 outline-none"
                        @keydown.enter="confirmTempInput(w, 'url', `${w.id}-url`)"
                      />
                      <button
                        @click="confirmTempInput(w, 'url', `${w.id}-url`)"
                        class="px-3 py-2 bg-yellow-500 text-white rounded-lg text-xs font-bold hover:bg-yellow-600 transition-colors whitespace-nowrap"
                      >
                        {{ $t('settings.extraSections.modalConfirm') }}
                      </button>
                    </div>
                  </div>
                  <div>
                    <label
                      class="block text-xs font-bold text-gray-600 mb-1 flex items-center gap-1"
                    >
                      <span>{{ $t('settings.extraSections.lanUrlLabel') }}</span>
                      <span class="text-[10px] font-normal text-gray-400 px-1.5 rounded glass-chip selected-outline"
                        >{{ $t('settings.extraSections.lanPriority') }}</span
                      >
                    </label>
                    <div class="flex gap-2">
                      <input
                        :value="tempInputs[`${w.id}-lanUrl`] ?? w.data.lanUrl"
                        @input="
                          (e: Event) =>
                            updateTempInput(`${w.id}-lanUrl`, (e.target as HTMLInputElement).value)
                        "
                        type="url"
                        :placeholder="$t('settings.extraSections.placeholderLanUrl')"
                        class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-xs focus:border-gray-900 outline-none"
                        @keydown.enter="confirmTempInput(w, 'lanUrl', `${w.id}-lanUrl`)"
                      />
                      <button
                        @click="confirmTempInput(w, 'lanUrl', `${w.id}-lanUrl`)"
                        class="px-3 py-2 bg-yellow-500 text-white rounded-lg text-xs font-bold hover:bg-yellow-600 transition-colors whitespace-nowrap"
                      >
                        确定
                      </button>
                    </div>
                  </div>
                  <p class="text-[10px] text-gray-500 mt-1">
                    目标站点若禁止被嵌入（X-Frame-Options 或 CSP frame-ancestors），这里会显示空白。
                    可改用「新标签打开」，或在该站点的响应头里单独放行本域。
                  </p>
                  <p class="text-[10px] text-gray-400 mt-1">
                    {{ $t('settings.extraSections.networkSwitchHint') }}
                  </p>
                </div>
              </div>
            </template>

            <!-- Amap Weather Widget Section -->
            <div class="flex items-center justify-between mb-4 border-b border-gray-100 pb-4 mt-8">
              <div class="flex items-center gap-2">
                <h4 class="text-base font-bold text-gray-900 border-l-4 border-gray-900 pl-3">
                  {{ $t('settings.extraSections.amapWeatherFull') }}
                </h4>
                <span class="text-xs text-gray-500 px-2 py-1 rounded-full glass-chip selected-outline">{{ $t('settings.extraSections.multiOpen') }}</span>
                <button
                  @click="addAmapWeatherWidget"
                  class="px-3 py-1.5 text-xs font-medium text-gray-900 rounded-lg transition-colors flex items-center gap-1 ml-2 glass-chip selectable-outline"
                >
                  <span class="text-base leading-none">+</span> {{ $t('settings.extraSections.addWeatherWidget') }}
                </button>
              </div>
            </div>

            <template v-for="w in store.widgets" :key="'amap-' + w.id">
              <div
                v-if="w.type === 'amap-weather'"
                class="flex flex-col gap-3 p-4 border border-gray-100 rounded-xl bg-gray-50 hover:bg-white hover:shadow-md transition-all"
              >
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-4">
                    <div
                      class="w-10 h-10 rounded-full bg-white flex items-center justify-center text-sm font-medium text-gray-700 shadow-sm"
                    >
                      {{ $t('settings.widgetAbbr.amap-weather') }}
                    </div>
                    <div class="flex flex-col">
                      <span class="font-bold text-gray-700">{{ $t('settings.extraSections.amapWeatherFull') }}</span>
                      <span class="text-[10px] text-gray-400 font-mono">ID: {{ w.id }}</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-6">
                    <button
                      @click="removeWidget(w.id)"
                      class="text-gray-400 hover:text-gray-900 text-xs underline px-2"
                      :title="$t('settings.extraSections.deleteComponent')"
                    >
                      删除
                    </button>
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-[10px] text-gray-400 font-medium">{{ $t('settings.sections.publicAccess') }}</span
                      ><label class="relative inline-flex items-center cursor-pointer"
                        ><input
                          type="checkbox"
                          v-model="w.isPublic"
                          class="sr-only peer"
                          @change="store.markDirty()" />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"
                        ></div
                      ></label>
                    </div>
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-[10px] text-gray-400 font-medium">{{ $t('settings.sections.mobileAccess') }}</span
                      ><label class="relative inline-flex items-center cursor-pointer"
                        ><input
                          type="checkbox"
                          :checked="!w.hideOnMobile"
                          class="sr-only peer"
                          @change="
                            (e) => {
                              w.hideOnMobile = !(e.target as HTMLInputElement).checked;
                              store.markDirty();
                            }
                          " />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-orange-500"
                        ></div
                      ></label>
                    </div>
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-[10px] text-gray-400 font-medium">{{ $t('settings.sections.enabled') }}</span
                      ><label class="relative inline-flex items-center cursor-pointer"
                        ><input
                          type="checkbox"
                          v-model="w.enable"
                          class="sr-only peer"
                          @change="store.markDirty()" />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-500"
                        ></div
                      ></label>
                    </div>
                  </div>
                </div>
              </div>
            </template>

            <!-- Countdown Widget Section -->
            <div class="flex items-center justify-between mb-4 border-b border-gray-100 pb-4 mt-8">
              <div class="flex items-center gap-2">
                <h4 class="text-base font-bold text-gray-900 border-l-4 border-gray-900 pl-3">
                  {{ $t('settings.extraSections.countdownSection') }}
                </h4>
                <span class="text-xs text-gray-500 px-2 py-1 rounded-full glass-chip selected-outline">{{ $t('settings.extraSections.multiOpen') }}</span>
                <button
                  @click="addCountdownWidget"
                  class="px-3 py-1.5 text-xs font-medium text-gray-900 rounded-lg transition-colors flex items-center gap-1 ml-2 glass-chip selectable-outline"
                >
                  <span class="text-base leading-none">+</span> {{ $t('settings.extraSections.addCountdown') }}
                </button>
              </div>
            </div>

            <template v-for="w in store.widgets" :key="'cd-' + w.id">
              <div
                v-if="w.type === 'countdown'"
                class="flex flex-col gap-3 p-4 border border-gray-100 rounded-xl bg-gray-50 hover:bg-white hover:shadow-md transition-all"
              >
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-4">
                    <div
                      class="w-10 h-10 rounded-full bg-white flex items-center justify-center text-sm font-medium text-gray-700 shadow-sm">
                      {{ $t('settings.widgetAbbr.countdown') }}
                    </div>
                    <div class="flex flex-col">
                      <span class="font-bold text-gray-700">{{ $t('settings.extraSections.countdownSection') }}</span>
                      <span class="text-[10px] text-gray-400 font-mono">ID: {{ w.id }}</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-6">
                    <button
                      @click="removeWidget(w.id)"
                      class="text-gray-400 hover:text-gray-900 text-xs underline px-2"
                      :title="$t('settings.extraSections.deleteComponent')"
                    >
                      删除
                    </button>
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-[10px] text-gray-400 font-medium">{{ $t('settings.sections.publicAccess') }}</span
                      ><label class="relative inline-flex items-center cursor-pointer"
                        ><input
                          type="checkbox"
                          v-model="w.isPublic"
                          class="sr-only peer"
                          @change="store.markDirty()" />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"
                        ></div
                      ></label>
                    </div>
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-[10px] text-gray-400 font-medium">{{ $t('settings.sections.mobileAccess') }}</span
                      ><label class="relative inline-flex items-center cursor-pointer"
                        ><input
                          type="checkbox"
                          :checked="!w.hideOnMobile"
                          class="sr-only peer"
                          @change="
                            (e) => {
                              w.hideOnMobile = !(e.target as HTMLInputElement).checked;
                              store.markDirty();
                            }
                          " />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-orange-500"
                        ></div
                      ></label>
                    </div>
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-[10px] text-gray-400 font-medium">{{ $t('settings.sections.enabled') }}</span
                      ><label class="relative inline-flex items-center cursor-pointer"
                        ><input
                          type="checkbox"
                          v-model="w.enable"
                          class="sr-only peer"
                          @change="store.markDirty()" />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-500"
                        ></div
                      ></label>
                    </div>
                  </div>
                </div>
                <div class="w-full bg-white/60 p-3 rounded-lg border border-gray-100 space-y-3">
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">标题</label>
                    <input
                      v-model="w.data.title"
                      type="text"
                      :placeholder="$t('settings.extraSections.placeholderCountdownTitle')"
                      class="w-full px-3 py-2 border border-gray-200 rounded-lg text-xs focus:border-gray-900 outline-none"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">目标时间</label>
                    <input
                      v-model="w.data.targetDate"
                      type="datetime-local"
                      class="w-full px-3 py-2 border border-gray-200 rounded-lg text-xs focus:border-gray-900 outline-none"
                    />
                  </div>
                </div>
              </div>
            </template>

            <!-- CountUp Widget Section -->
            <div class="flex items-center justify-between mb-4 border-b border-gray-100 pb-4 mt-8">
              <div class="flex items-center gap-2">
                <h4 class="text-base font-bold text-gray-900 border-l-4 border-gray-900 pl-3">
                  {{ $t('settings.extraSections.countupSection') }}
                </h4>
                <span class="text-xs text-gray-500 px-2 py-1 rounded-full glass-chip selected-outline">{{ $t('settings.extraSections.multiOpen') }}</span>
                <button
                  @click="addCountUpWidget"
                  class="px-3 py-1.5 text-xs font-medium text-gray-900 rounded-lg transition-colors flex items-center gap-1 ml-2 glass-chip selectable-outline"
                >
                  <span class="text-base leading-none">+</span> {{ $t('settings.extraSections.addCountup') }}
                </button>
              </div>
            </div>

            <template v-for="w in store.widgets" :key="'cup-' + w.id">
              <div
                v-if="w.type === 'countup'"
                class="flex flex-col gap-3 p-4 border border-gray-100 rounded-xl bg-gray-50 hover:bg-white hover:shadow-md transition-all"
              >
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-4">
                    <div
                      class="w-10 h-10 rounded-full bg-white flex items-center justify-center text-sm font-medium text-gray-700 shadow-sm"
                    >
                      正
                    </div>
                    <div class="flex flex-col">
                      <span class="font-bold text-gray-700">{{ $t('settings.extraSections.countupSection') }}</span>
                      <span class="text-[10px] text-gray-400 font-mono">ID: {{ w.id }}</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-6">
                    <button
                      @click="removeWidget(w.id)"
                      class="text-gray-400 hover:text-gray-900 text-xs underline px-2"
                      :title="$t('settings.extraSections.deleteComponent')"
                    >
                      删除
                    </button>
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-[10px] text-gray-400 font-medium">{{ $t('settings.sections.publicAccess') }}</span
                      ><label class="relative inline-flex items-center cursor-pointer"
                        ><input
                          type="checkbox"
                          v-model="w.isPublic"
                          class="sr-only peer"
                          @change="store.markDirty()" />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"
                        ></div
                      ></label>
                    </div>
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-[10px] text-gray-400 font-medium">{{ $t('settings.sections.mobileAccess') }}</span
                      ><label class="relative inline-flex items-center cursor-pointer"
                        ><input
                          type="checkbox"
                          :checked="!w.hideOnMobile"
                          class="sr-only peer"
                          @change="
                            (e) => {
                              w.hideOnMobile = !(e.target as HTMLInputElement).checked;
                              store.markDirty();
                            }
                          " />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-orange-500"
                        ></div
                      ></label>
                    </div>
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-[10px] text-gray-400 font-medium">{{ $t('settings.sections.enabled') }}</span
                      ><label class="relative inline-flex items-center cursor-pointer"
                        ><input
                          type="checkbox"
                          v-model="w.enable"
                          class="sr-only peer"
                          @change="store.markDirty()" />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-500"
                        ></div
                      ></label>
                    </div>
                  </div>
                </div>
                <div class="w-full bg-white/60 p-3 rounded-lg border border-gray-100 space-y-3">
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">标题</label>
                    <input
                      v-model="w.data.title"
                      type="text"
                      :placeholder="$t('settings.extraSections.placeholderCountupTitle')"
                      class="w-full px-3 py-2 border border-gray-200 rounded-lg text-xs focus:border-gray-900 outline-none"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">开始时间</label>
                    <input
                      v-model="w.data.startTime"
                      type="datetime-local"
                      step="1"
                      class="w-full px-3 py-2 border border-gray-200 rounded-lg text-xs focus:border-gray-900 outline-none"
                    />
                  </div>
                </div>
              </div>
            </template>
          </div>

</template>
