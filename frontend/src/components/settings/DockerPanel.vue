<script setup lang="ts">
// 该面板由 SettingsModal.vue 拆分而来：模板保持原样，状态通过 inject 取父级上下文。
import { inject, toRef } from "vue";
import { SETTINGS_CTX } from "./context";

const ctx = inject(SETTINGS_CTX) as Record<string, any>;

const activeTab = toRef(ctx, "activeTab");
const checkDockerConnection = toRef(ctx, "checkDockerConnection");
const dockerWidget = toRef(ctx, "dockerWidget");
const enableDockerWidget = toRef(ctx, "enableDockerWidget");
const enableSystemStatusWidget = toRef(ctx, "enableSystemStatusWidget");
const exportDockerLogs = toRef(ctx, "exportDockerLogs");
const hasAdminAccess = toRef(ctx, "hasAdminAccess");
const isDockerComponentCreated = toRef(ctx, "isDockerComponentCreated");
const isDockerSystemEnabled = toRef(ctx, "isDockerSystemEnabled");
const isExportingDockerLogs = toRef(ctx, "isExportingDockerLogs");
const isUpdatingDockerSystem = toRef(ctx, "isUpdatingDockerSystem");
const onMobileDockerDisplayChange = toRef(ctx, "onMobileDockerDisplayChange");
const onMobileSystemStatusDisplayChange = toRef(ctx, "onMobileSystemStatusDisplayChange");
const store = toRef(ctx, "store");
const systemStatusWidget = toRef(ctx, "systemStatusWidget");
const t = toRef(ctx, "t");
const toggleDockerMock = toRef(ctx, "toggleDockerMock");
const toggleDockerSystemEnabled = toRef(ctx, "toggleDockerSystemEnabled");
const toggleSystemStatusMock = toRef(ctx, "toggleSystemStatusMock");

import DockerWidget from "../DockerWidget.vue";
import SystemStatusWidget from "../SystemStatusWidget.vue";
</script>

<template>
          <div v-if="activeTab === 'docker'" class="space-y-4">
            <div class="flex items-center justify-between mb-4 mr-8">
              <h4 class="text-base font-bold text-gray-900 border-l-4 border-gray-900 pl-3">
                Docker 管理 (内测中)
              </h4>
              <div
                v-if="dockerWidget || isDockerSystemEnabled"
                class="flex items-center gap-3 text-xs mr-[10px]"
              >
                <button
                  @click="exportDockerLogs"
                  :disabled="isExportingDockerLogs || !isDockerSystemEnabled"
                  class="text-gray-900 px-3 py-1 rounded-lg transition-colors font-bold disabled:opacity-60 glass-chip selectable-outline"
                >
                  {{ isExportingDockerLogs ? "导出中" : "导出日志" }}
                </button>
                <button
                  @click="checkDockerConnection"
                  :disabled="!isDockerSystemEnabled || isUpdatingDockerSystem"
                  class="text-gray-900 px-3 py-1 rounded-lg transition-colors font-bold disabled:opacity-50 glass-chip selectable-outline"
                >
                  测试连接
                </button>
              </div>
            </div>

            <div class="space-y-3 mb-6 pb-6 border-b border-gray-100">
              <div class="flex items-center justify-between">
                <div>
                  <div class="text-sm font-bold text-gray-900">{{ $t('settings.sections.dockerService') }}</div>
                  <p class="mt-1 text-xs text-gray-500">
                    {{ $t('settings.sections.dockerServiceDesc', { windowsSocket: 'npipe:////./pipe/docker_engine', linuxSocket: 'unix:///var/run/docker.sock' }) }}
                  </p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer shrink-0">
                  <input
                    type="checkbox"
                    :checked="isDockerSystemEnabled"
                    :disabled="isUpdatingDockerSystem || !hasAdminAccess"
                    :aria-label="$t('settings.extraSections.dockerServiceAriaLabel')"
                    @change="(e) => toggleDockerSystemEnabled((e.target as HTMLInputElement).checked)"
                    class="sr-only peer"
                  />
                  <div
                    class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white peer-disabled:opacity-50 after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-500 shrink-0"
                  ></div>
                  <span class="text-sm text-gray-700 ml-3 whitespace-nowrap">
                    {{ isUpdatingDockerSystem ? $t('settings.sections.switching') : isDockerSystemEnabled ? $t('settings.sections.enabled') : $t('settings.sections.disabled') }}
                  </span>
                </label>
              </div>

              <div
                class="rounded-xl border px-3 py-2 text-xs"
                :class="
                  isDockerSystemEnabled
                    ? 'border-emerald-200 bg-emerald-50/70 text-emerald-700'
                    : 'border-amber-200 bg-amber-50/70 text-amber-700'
                "
              >
                <p>
                  {{
                    isDockerSystemEnabled
                      ? $t('settings.sections.dockerEnabledDesc')
                      : $t('settings.sections.dockerDisabledDesc')
                  }}
                </p>
                <p class="mt-1 text-[11px] opacity-80">
                  “Docker 服务”是系统级总开关，“显示 Docker 组件”只影响首页卡片显示，“模拟数据”只影响组件展示数据来源。
                </p>
                <p v-if="!hasAdminAccess" class="mt-1 text-[11px] opacity-80">
                  {{ $t('settings.sections.dockerNote2') }}
                </p>
              </div>
            </div>

            <!-- Host Status Widget Section -->
            <div class="space-y-3 mb-6 pb-6 border-b border-gray-100">
              <div class="flex items-center justify-between">
                <span class="text-sm font-bold text-gray-900">{{ $t('settings.sections.hostStatusWidget') }}</span>
                <div class="flex items-center gap-4">
                  <div
                    v-if="systemStatusWidget && systemStatusWidget.enable"
                    class="flex items-center gap-2 animate-fade-in"
                  >
                    <div class="flex items-center gap-2">
                      <span class="text-xs text-gray-700 font-medium">{{ $t('settings.sections.publicAccessLabel') }}</span>
                      <label class="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          v-model="systemStatusWidget.isPublic"
                          class="sr-only peer"
                        />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"
                        ></div>
                      </label>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-xs text-gray-700 font-medium">{{ $t('settings.sections.mobileDisplay') }}</span>
                      <label class="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          :checked="!systemStatusWidget.hideOnMobile"
                          @change="onMobileSystemStatusDisplayChange"
                          class="sr-only peer"
                        />
                        <div
                          class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-orange-500"
                        ></div>
                      </label>
                    </div>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      :checked="systemStatusWidget?.enable"
                      :aria-label="$t('settings.sections.enabled')"
                      @change="
                        (e) => {
                          if ((e.target as HTMLInputElement).checked) enableSystemStatusWidget();
                          else if (systemStatusWidget) {
                            systemStatusWidget.enable = false;
                            store.markDirty();
                          }
                        }
                      "
                      class="sr-only peer"
                    />
                    <div
                      class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-500"
                    ></div>
                    <span class="text-sm text-gray-700 ml-3">{{ $t('settings.sections.enabled') }}</span>
                  </label>
                </div>
              </div>

              <div
                v-if="systemStatusWidget && systemStatusWidget.enable"
                class="animate-fade-in space-y-3"
              >
                <div class="flex flex-wrap items-center gap-4 border-t border-gray-100 pt-3">
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-gray-500">{{ $t('settings.sections.useMockData') }}</span>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        :checked="!!systemStatusWidget.data?.useMock"
                        @change="
                          (e) => toggleSystemStatusMock((e.target as HTMLInputElement).checked)
                        "
                        class="sr-only peer"
                      />
                      <div
                        class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"
                      ></div>
                    </label>
                  </div>
                </div>
                <div class="h-40 w-full max-w-sm">
                  <SystemStatusWidget :widget="systemStatusWidget" />
                </div>
              </div>
            </div>

            <div class="space-y-4">
              <!-- 未启用时的提示 -->
              <template v-if="!isDockerComponentCreated">
                <div class="flex items-center justify-between">
                  <span class="text-sm font-bold text-gray-900">{{ $t('settings.sections.containerManagement') }}</span>
                  <button
                    @click="enableDockerWidget"
                    class="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-black transition-colors shadow-sm text-sm"
                  >
                    启用容器管理
                  </button>
                </div>
              </template>

              <!-- 已启用后的管理区 -->
              <template v-else>
                <!-- 主控制区 -->
                <div class="flex items-center justify-between">
                  <span class="text-sm font-bold text-gray-900">容器管理</span>
                  <div class="flex items-center gap-4">
                    <div class="flex items-center gap-4 animate-fade-in">
                      <div class="flex items-center gap-2">
                        <span class="text-xs text-gray-700 font-medium">公开访问</span>
                        <label class="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" v-model="dockerWidget.isPublic" class="sr-only peer" />
                          <div
                            class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"
                          ></div>
                        </label>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="text-xs text-gray-700 font-medium">手机端显示</span>
                        <label class="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" :checked="!dockerWidget.hideOnMobile" @change="onMobileDockerDisplayChange" class="sr-only peer" />
                          <div
                            class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-orange-500"
                          ></div>
                        </label>
                      </div>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" v-model="dockerWidget.enable" :aria-label="$t('settings.sections.containerManagementWidget')" class="sr-only peer" />
                      <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-500"></div>
                      <span class="text-sm text-gray-700 ml-3">{{ $t('settings.sections.containerManagementWidget') }}</span>
                    </label>
                  </div>
                </div>

                <!-- 功能配置区 -->
                <div class="flex flex-wrap items-center gap-4 border-t border-gray-100 pt-3">
                  <!-- 模拟数据 -->
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-gray-500">{{ $t('settings.sections.mockData') }}</span>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        :checked="!!dockerWidget.data?.useMock"
                        @change="(e) => toggleDockerMock((e.target as HTMLInputElement).checked)"
                        class="sr-only peer"
                      />
                      <div
                        class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"
                      ></div>
                    </label>
                  </div>

                  <!-- 自动升级 -->
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-gray-500">{{ $t('settings.sections.autoUpdate') }}</span>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        :checked="!!dockerWidget.data?.autoUpdate"
                        @change="
                          (e) => {
                            if (!dockerWidget.data) dockerWidget.data = {};
                            dockerWidget.data.autoUpdate = (e.target as HTMLInputElement).checked;
                            store.markDirty();
                          }
                        "
                        class="sr-only peer"
                      />
                      <div
                        class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"
                      ></div>
                    </label>
                  </div>

                  <!-- 升级配置 -->
                  <div class="flex items-center gap-2">
                    <span class="text-[10px] text-gray-500">{{ $t('settings.extraSections.keepVersions') }}</span>
                    <input
                      type="number"
                      min="1"
                      max="20"
                      :disabled="!dockerWidget?.data?.autoUpdate"
                      :value="dockerWidget?.data?.autoUpdateKeepImages ?? 2"
                      @change="
                        (e) => {
                          if (!dockerWidget.data) dockerWidget.data = {};
                          dockerWidget.data.autoUpdateKeepImages = Math.max(
                            1,
                            Math.min(20, Number((e.target as HTMLInputElement).value || 2)),
                          );
                          store.markDirty();
                        }
                      "
                      class="w-16 px-2 py-1 border border-gray-200 rounded text-xs focus:border-gray-900 outline-none disabled:bg-gray-50 disabled:text-gray-400"
                    />
                    <span class="text-[10px] text-gray-500">{{ $t('settings.extraSections.unitCount') }}</span>
                  </div>

                  <div class="flex items-center gap-2">
                    <span class="text-[10px] text-gray-500">{{ $t('settings.extraSections.diskThreshold') }}</span>
                    <input
                      type="number"
                      min="0"
                      step="0.5"
                      :disabled="!dockerWidget?.data?.autoUpdate"
                      :value="dockerWidget?.data?.autoUpdateMinFreeGB ?? 5"
                      @change="
                        (e) => {
                          if (!dockerWidget.data) dockerWidget.data = {};
                          dockerWidget.data.autoUpdateMinFreeGB = Math.max(
                            0,
                            Number((e.target as HTMLInputElement).value || 5),
                          );
                          store.markDirty();
                        }
                      "
                      class="w-20 px-2 py-1 border border-gray-200 rounded text-xs focus:border-gray-900 outline-none disabled:bg-gray-50 disabled:text-gray-400"
                    />
                    <span class="text-[10px] text-gray-500">GB</span>
                  </div>

                  <!-- 内网主机 -->
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-gray-700 font-medium">{{ $t('settings.extraSections.intranetHost') }}</span>
                    <input
                      :value="dockerWidget?.data?.lanHost"
                      @change="
                        (e) => {
                          if (!dockerWidget.data) dockerWidget.data = {};
                          dockerWidget.data.lanHost = (e.target as HTMLInputElement).value;
                          store.markDirty();
                        }
                      "
                      type="text"
                      :placeholder="$t('settings.extraSections.placeholderIntranetHost')"
                      class="px-2 py-1 border border-gray-200 rounded text-xs focus:border-gray-900 outline-none"
                    />
                  </div>
                </div>

                <!-- 容器预览（始终可见） -->
                <div class="border-t border-gray-100 pt-3">
                  <div
                    v-if="isDockerSystemEnabled"
                    class="h-[500px]"
                  >
                    <DockerWidget :widget="dockerWidget" :compact="true" />
                  </div>
                  <div
                    v-else
                    class="h-[160px] rounded-2xl border border-dashed border-gray-200 bg-gray-50/80 flex items-center justify-center text-center px-6"
                  >
                    <div class="text-sm text-gray-500 space-y-2">
                      <p>{{ $t('settings.extraSections.dockerServiceClosed') }}</p>
                      <p class="text-xs text-gray-400">
                        {{ $t('settings.extraSections.dockerServiceClosedDesc') }}
                      </p>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>

</template>
