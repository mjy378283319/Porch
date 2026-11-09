<script setup lang="ts">
// 该面板由 SettingsModal.vue 拆分而来：模板保持原样，状态通过 inject 取父级上下文。
import { inject, toRef } from "vue";
import { SETTINGS_CTX } from "./context";

const ctx = inject(SETTINGS_CTX) as Record<string, any>;

const activeTab = toRef(ctx, "activeTab");
const addCustomCssWidget = toRef(ctx, "addCustomCssWidget");
const daoliyuLogo = toRef(ctx, "daoliyuLogo");
const deleteMusicFile = toRef(ctx, "deleteMusicFile");
const deleteWidget = toRef(ctx, "deleteWidget");
const editingOpacityId = toRef(ctx, "editingOpacityId");
const fetchMusicFiles = toRef(ctx, "fetchMusicFiles");
const isMusicListLoading = toRef(ctx, "isMusicListLoading");
const isUnknownWidget = toRef(ctx, "isUnknownWidget");
const musicFiles = toRef(ctx, "musicFiles");
const musicManagerOpen = toRef(ctx, "musicManagerOpen");
const musicManagerStatus = toRef(ctx, "musicManagerStatus");
const musicVolumePercent = toRef(ctx, "musicVolumePercent");
const restoreMissingWidgets = toRef(ctx, "restoreMissingWidgets");
const scrollToMusicSettings = toRef(ctx, "scrollToMusicSettings");
const setTab = toRef(ctx, "setTab");
const shouldShowSingleWidgetDiagnostic = toRef(ctx, "shouldShowSingleWidgetDiagnostic");
const singleOpenWidgets = toRef(ctx, "singleOpenWidgets");
const singleWidgetDiagnosticTypes = toRef(ctx, "singleWidgetDiagnosticTypes");
const store = toRef(ctx, "store");
const t = toRef(ctx, "t");
const toggleMusicManager = toRef(ctx, "toggleMusicManager");
const uploadMusic = toRef(ctx, "uploadMusic");
const uploadStatus = toRef(ctx, "uploadStatus");

import RssSettings from "../RssSettings.vue";
import SearchSettings from "../SearchSettings.vue";
</script>

<template>
          <div v-if="activeTab === 'widgets'" class="space-y-4">
            <div class="flex items-center justify-between mb-4 mr-8">
              <h4 class="text-base font-bold text-gray-900 border-l-4 border-gray-900 pl-3">
                {{ $t('settings.sections.desktopWidgets') }}
              </h4>
              <div class="flex items-center gap-3 text-xs mr-[10px]">
                <button
                  @click="restoreMissingWidgets"
                  class="text-gray-600 hover:text-gray-900 underline mr-2"
                >
                  恢复默认组件
                </button>
                <button
                  @click="addCustomCssWidget"
                  class="text-gray-600 hover:text-gray-900 underline mr-2"
                >
                  + 自定义组件
                </button>
              </div>
            </div>

            <div
              v-if="shouldShowSingleWidgetDiagnostic"
              class="rounded-xl border border-amber-200 bg-amber-50/80 p-4 text-sm text-amber-900"
            >
              <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div class="space-y-1">
                  <div class="font-bold">{{ $t('settings.sections.singleWidgetDiagnostic') }}</div>
                  <p class="text-xs leading-relaxed text-amber-800">
                    {{ $t('settings.sections.singleWidgetDiagnosticDesc', { count: singleOpenWidgets.length, total: store.widgets.length, types: singleWidgetDiagnosticTypes }) }}
                  </p>
                </div>
                <button
                  type="button"
                  @click="restoreMissingWidgets"
                  class="shrink-0 rounded-lg bg-amber-600 px-3 py-2 text-xs font-bold text-white transition-colors hover:bg-amber-700"
                >
                  恢复默认组件
                </button>
              </div>
            </div>

            <!-- Normal Widgets Grid -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
              <template v-for="w in singleOpenWidgets" :key="w.id">
                <div
                  :class="[
                    'border border-gray-100 rounded-xl bg-white/60 hover:shadow-md transition-all relative',
                    w.type === 'player'
                      ? 'col-span-2 md:col-span-4 flex flex-col gap-3 p-4 md:grid md:grid-cols-[auto_1fr_auto] md:items-center md:gap-4'
                      : 'flex flex-col items-stretch gap-2 p-3',
                  ]"
                >
                  <button
                    v-if="isUnknownWidget(w.type)"
                    @click="deleteWidget(w.id)"
                    class="absolute top-1 right-1 w-5 h-5 flex items-center justify-center bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-full text-xs transition-colors z-20"
                    :title="$t('settings.sections.deleteWidget')"
                  >
                    ✕
                  </button>
                  <template v-if="w.type === 'player'">
                    <div class="flex items-center gap-3 flex-shrink-0">
                      <div
                        class="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center text-sm font-medium text-gray-700 shadow-sm"
                      >
                        {{ $t('settings.widgetAbbr.player') }}
                      </div>
                      <span class="font-bold text-gray-700 text-sm">{{ $t('settings.sections.randomMusic') }}</span>
                    </div>
                    <div class="flex flex-wrap items-center gap-2">
                      <label
                        class="px-3 py-1.5 text-gray-700 text-xs rounded-lg cursor-pointer transition-colors flex items-center gap-1 whitespace-nowrap glass-chip selectable-outline"
                      >
                        <span>{{ $t('settings.sections.uploadMusic') }}</span>
                        <input
                          type="file"
                          accept="audio/*"
                          class="hidden"
                          multiple
                          @change="uploadMusic"
                        />
                      </label>
                      <button
                        type="button"
                        @click="toggleMusicManager"
                        class="px-3 py-1.5 text-gray-700 text-xs rounded-lg cursor-pointer transition-colors flex items-center gap-1 whitespace-nowrap glass-chip selectable-outline"
                      >
                        {{ musicManagerOpen ? $t('settings.sections.collapseFiles') : $t('settings.sections.fileManagement') }} ({{ musicFiles.length }})
                      </button>
                      <span
                        v-if="uploadStatus"
                        class="text-xs"
                        :class="(uploadStatus.includes(t('settings.messages.uploadFailed')) || uploadStatus.includes('失败')) ? 'text-red-500' : 'text-green-500'"
                        >{{ uploadStatus }}</span
                      >
                    </div>
                    <div class="flex flex-col items-stretch gap-2 md:items-end">
                      <div class="flex items-center gap-2 justify-end">
                        <span class="text-xs text-gray-500 whitespace-nowrap">{{ $t('settings.sections.musicVolume') }}</span>
                        <input
                          v-model.number="musicVolumePercent"
                          type="range"
                          min="0"
                          max="100"
                          step="1"
                          class="w-28 h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-400"
                        />
                      </div>
                      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        <div class="flex flex-col items-center gap-0.5">
                          <span class="text-[10px] text-gray-400 scale-90">{{ $t('settings.sections.publicAccess') }}</span>
                          <label
                            class="relative inline-flex items-center cursor-pointer"
                            :title="$t('settings.sections.publicAccess')"
                            ><input type="checkbox" v-model="w.isPublic" class="sr-only peer" @change="store.saveData()" />
                            <div
                              class="w-7 h-4 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-blue-500"
                            ></div
                          ></label>
                        </div>
                        <div class="flex flex-col items-center gap-0.5">
                          <span class="text-[10px] text-gray-400 scale-90">{{ $t('settings.sections.enabled') }}</span>
                          <label
                            class="relative inline-flex items-center cursor-pointer"
                            :title="$t('settings.sections.enabled')"
                            ><input type="checkbox" v-model="w.enable" class="sr-only peer" @change="store.saveData()" />
                            <div
                              class="w-7 h-4 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-green-500"
                            ></div
                          ></label>
                        </div>
                        <div class="flex flex-col items-center gap-0.5">
                          <span class="text-[10px] text-gray-400 scale-90">{{ $t('settings.sections.mobileAccess') }}</span>
                          <label
                            class="relative inline-flex items-center cursor-pointer"
                            :title="$t('settings.sections.mobileAccess')"
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
                              class="w-7 h-4 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-orange-500"
                            ></div
                          ></label>
                        </div>
                        <div class="flex flex-col items-center gap-0.5">
                          <span class="text-[10px] text-gray-400 scale-90">{{ $t('settings.sections.autoPlay') }}</span>
                          <label
                            class="relative inline-flex items-center cursor-pointer"
                            :title="$t('settings.sections.autoPlayTitle')"
                            ><input
                              type="checkbox"
                              v-model="store.appConfig.autoPlayMusic"
                              @change="store.markDirty()"
                              class="sr-only peer" />
                            <div
                              class="w-7 h-4 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-blue-600"
                            ></div
                          ></label>
                        </div>
                      </div>
                    </div>
                    <div v-if="musicManagerOpen" class="md:col-start-1 md:col-span-3 space-y-2">
                      <div class="flex items-center gap-2">
                        <button
                          type="button"
                          @click="fetchMusicFiles"
                          class="px-3 py-1.5 bg-gray-100 text-gray-700 text-xs rounded-lg cursor-pointer hover:bg-gray-200 transition-colors flex items-center gap-1 whitespace-nowrap"
                          :disabled="isMusicListLoading"
                        >
                          {{ isMusicListLoading ? $t('settings.sections.refreshing') : $t('settings.sections.refreshList') }}
                        </button>
                        <span v-if="musicManagerStatus" class="text-xs text-red-500">{{
                          musicManagerStatus
                        }}</span>
                        <span v-else class="text-xs text-gray-500"
                          >{{ $t('settings.sections.totalFiles', { count: musicFiles.length }) }}</span
                        >
                      </div>
                      <div
                        class="border border-gray-100 rounded-xl bg-gray-50 p-3 max-h-44 overflow-auto"
                      >
                        <div v-if="isMusicListLoading" class="text-xs text-gray-500">{{ $t('settings.extraSections.loadingVersions') }}</div>
                        <div v-else-if="musicFiles.length === 0" class="text-xs text-gray-500">
                          {{ $t('settings.sections.noMusicFiles') }}
                        </div>
                        <div v-else class="space-y-1">
                          <div
                            v-for="f in musicFiles"
                            :key="f"
                            class="flex items-center gap-2 text-xs"
                          >
                            <span class="flex-1 truncate text-gray-700" :title="f">{{ f }}</span>
                            <button
                              type="button"
                              class="px-2 py-1 rounded-md bg-red-50 text-red-600 hover:bg-red-100 transition-colors"
                              @click="deleteMusicFile(f)"
                            >
                              {{ $t('settings.sections.delete') }}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    <div
                      class="flex flex-col items-center gap-1.5 scale-100 cursor-pointer hover:bg-gray-50 rounded-lg transition-colors w-full py-1"
                      @click="
                        w.type === 'music'
                          ? scrollToMusicSettings()
                          : w.type === 'system-status'
                            ? setTab('docker')
                            : (editingOpacityId = w.id)
                      "
                      :title="
                        w.type === 'music' || w.type === 'system-status'
                          ? $t('settings.sections.clickToSettings')
                          : $t('settings.sections.clickToStyle')
                      "
                    >
                      <template v-if="editingOpacityId === w.id">
                        <div class="w-full px-2" @click.stop>
                          <label class="text-[10px] text-gray-500 block mb-1"
                            >{{ $t('settings.sections.opacity') }}
                            {{
                              Math.round((w.opacity ?? (w.type === "search" ? 0.9 : 1)) * 100)
                            }}%</label
                          >
                          <input
                            type="range"
                            min="0.1"
                            max="1"
                            step="0.1"
                            :value="w.opacity ?? (w.type === 'search' ? 0.9 : 1)"
                            @input="
                              (e) => {
                                w.opacity = parseFloat((e.target as HTMLInputElement).value);
                                store.markDirty();
                              }
                            "
                            class="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-400"
                          />
                          <div class="flex items-center justify-between mt-2 gap-2">
                            <label class="text-[10px] text-gray-500">{{ $t('settings.sections.textColor') }}</label>
                            <div class="flex items-center gap-2">
                              <input
                                type="color"
                                :value="
                                  w.textColor || (w.type === 'search' ? '#111827' : '#374151')
                                "
                                @input="
                                  (e) => {
                                    w.textColor = (e.target as HTMLInputElement).value;
                                    store.markDirty();
                                  }
                                "
                                @change="store.markDirty()"
                                class="w-5 h-5 p-0 border-0 rounded-full cursor-pointer overflow-hidden shadow-sm"
                                :title="$t('settings.extraSections.selectColor')"
                              />
                              <button
                                v-if="w.textColor"
                                @click.stop="
                                  w.textColor = undefined;
                                  store.markDirty();
                                "
                                class="text-[10px] text-red-400 hover:text-red-600"
                                :title="$t('settings.extraSections.resetColor')"
                              >
                                ✕
                              </button>
                            </div>
                          </div>
                          <button
                            @click.stop="editingOpacityId = null"
                            class="mt-2 text-xs text-gray-600 hover:text-gray-900 w-full text-center border-t border-gray-100 pt-1"
                          >
                            {{ $t('settings.sections.done') }}
                          </button>
                        </div>
                      </template>
                      <template v-else>
                        <div
                          class="w-9 h-9 rounded-full bg-gray-50 flex items-center justify-center text-xs font-medium text-gray-700 shadow-sm"
                        >
                          <img
                            v-if="w.type === 'music'"
                            :src="daoliyuLogo"
                            class="w-6 h-6 object-contain"
                          />
                          <template v-else>
                            {{ $t(`settings.widgetAbbr.${w.type}`, w.type) }}
                          </template>
                        </div>
                        <span
                          class="font-bold text-gray-700 text-xs leading-snug text-center truncate w-full px-1"
                        >
                          {{
                            w.type === "custom-css"
                              ? (w.data?.title || $t('settings.widgetTypes.custom-css'))
                              : $t(`settings.widgetTypes.${w.type}`, `未知组件 (${w.type})`)
                          }}
                        </span>
                      </template>
                    </div>
                    <div class="grid grid-cols-3 gap-1.5 w-full mt-1">
                      <div class="flex flex-col items-center gap-0.5">
                        <span class="text-[10px] text-gray-400 scale-90">公开</span>
                        <label class="relative inline-flex items-center cursor-pointer" title="公开"
                          ><input type="checkbox" v-model="w.isPublic" class="sr-only peer" @change="store.saveData()" />
                          <div
                            class="w-7 h-4 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-blue-500"
                          ></div
                        ></label>
                      </div>
                      <div class="flex flex-col items-center gap-0.5">
                        <span class="text-[10px] text-gray-400 scale-90">启用</span>
                        <label class="relative inline-flex items-center cursor-pointer" title="启用"
                          ><input type="checkbox" v-model="w.enable" class="sr-only peer" @change="store.saveData()" />
                          <div
                            class="w-7 h-4 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-green-500"
                          ></div
                        ></label>
                      </div>
                      <div class="flex flex-col items-center gap-0.5">
                        <span class="text-[10px] text-gray-400 scale-90">手机</span>
                        <label class="relative inline-flex items-center cursor-pointer" title="手机"
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
                            class="w-7 h-4 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-orange-500"
                          ></div
                        ></label>
                      </div>
                      <div v-if="w.type === 'player'" class="flex flex-col items-center gap-0.5">
                        <span class="text-[10px] text-gray-400 scale-90">自动</span>
                        <label
                          class="relative inline-flex items-center cursor-pointer"
                          title="自动播放"
                          ><input
                            type="checkbox"
                            v-model="store.appConfig.autoPlayMusic"
                            @change="store.markDirty()"
                            class="sr-only peer" />
                          <div
                            class="w-7 h-4 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-blue-600"
                          ></div
                        ></label>
                      </div>
                    </div>
                  </template>
                </div>
              </template>
            </div>

            <div class="border-2 border-gray-900 rounded-xl p-4 mt-6 bg-white">
              <h4 class="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
                高级组件配置
              </h4>
              <div class="space-y-8">
                <RssSettings />
                <div class="border-t border-gray-200"></div>
                <SearchSettings />
              </div>
            </div>
          </div>

</template>
