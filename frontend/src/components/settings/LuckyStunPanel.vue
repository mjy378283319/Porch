<script setup lang="ts">
// 该面板由 SettingsModal.vue 拆分而来：模板保持原样，状态通过 inject 取父级上下文。
import { inject, toRef } from "vue";
import { SETTINGS_CTX } from "./context";

const ctx = inject(SETTINGS_CTX) as Record<string, any>;

const activeTab = toRef(ctx, "activeTab");
const addAmapWeatherWidget = toRef(ctx, "addAmapWeatherWidget");
const addMusicWidget = toRef(ctx, "addMusicWidget");
const browserHelperHandshakeLink = toRef(ctx, "browserHelperHandshakeLink");
const copyBrowserHelperHandshakeLink = toRef(ctx, "copyBrowserHelperHandshakeLink");
const copyWebhookUrl = toRef(ctx, "copyWebhookUrl");
const formatTime = toRef(ctx, "formatTime");
const getMusicAvatarUrl = toRef(ctx, "getMusicAvatarUrl");
const getWebhookUrl = toRef(ctx, "getWebhookUrl");
const isTestingMusicAuth = toRef(ctx, "isTestingMusicAuth");
const isTestingWeather = toRef(ctx, "isTestingWeather");
const isUpdatingProfile = toRef(ctx, "isUpdatingProfile");
const musicWidget = toRef(ctx, "musicWidget");
const openBrowserHelperHandshakeLink = toRef(ctx, "openBrowserHelperHandshakeLink");
const openRenameModal = toRef(ctx, "openRenameModal");
const removeWidget = toRef(ctx, "removeWidget");
const selectedMusicSize = toRef(ctx, "selectedMusicSize");
const setMusicSize = toRef(ctx, "setMusicSize");
const store = toRef(ctx, "store");
const styleVariableRows = toRef(ctx, "styleVariableRows");
const styleVariableStatus = toRef(ctx, "styleVariableStatus");
const t = toRef(ctx, "t");
const testMusicAuth = toRef(ctx, "testMusicAuth");
const testMusicAuthResult = toRef(ctx, "testMusicAuthResult");
const testWeatherConnection = toRef(ctx, "testWeatherConnection");
const testWeatherResult = toRef(ctx, "testWeatherResult");

import ScriptManager from "../ScriptManager.vue";
</script>

<template>
          <div v-if="activeTab === 'lucky-stun'" class="p-4 space-y-4">
            <div class="flex items-center gap-2 mb-4">
              <h4 class="text-base font-bold text-gray-900 border-l-4 border-gray-900 pl-3">
                {{ $t('settings.tabs.luckyStun') }}
              </h4>
            </div>

            <div class="bg-gray-50 border border-gray-100 rounded-xl p-4 mb-6 space-y-3">
              <div class="flex items-center justify-between gap-3">
                <div>
                  <h4 class="text-base font-bold text-gray-900">{{ $t('settings.extraSections.browserHelperComms') }}</h4>
                  <p class="text-xs text-gray-500 mt-1">
                    {{ $t('settings.extraSections.browserHelperDesc') }}
                  </p>
                </div>
              </div>

              <template v-if="browserHelperHandshakeLink">
                <a
                  :href="browserHelperHandshakeLink"
                  :data-flatnas-helper-link="browserHelperHandshakeLink"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="block w-full px-3 py-2 rounded-lg border border-gray-200 bg-white text-[11px] text-blue-600 break-all hover:border-blue-300 transition-colors"
                >
                  {{ browserHelperHandshakeLink }}
                </a>
                <div class="flex flex-wrap items-center gap-2">
                  <button
                    @click="copyBrowserHelperHandshakeLink"
                    class="px-3 py-1.5 bg-gray-900 hover:bg-black text-white text-xs rounded-lg transition-colors"
                  >
                    复制握手链接
                  </button>
                  <button
                    @click="openBrowserHelperHandshakeLink"
                    class="px-3 py-1.5 bg-white border border-gray-200 hover:border-gray-300 text-gray-700 text-xs rounded-lg transition-colors"
                  >
                    打开握手页
                  </button>
                  <a
                    href="https://qdnas.icu/c/8/g/14"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded-lg transition-colors inline-block"
                  >
                    下载浏览器助手
                  </a>
                </div>
                <p class="text-[11px] text-gray-500">
                  {{ $t('settings.extraSections.helperNotDetected') }}
                </p>
              </template>
              <p v-else class="text-[11px] text-amber-600">
                {{ $t('settings.extraSections.noLoginToken') }}
              </p>
            </div>


            <!-- Music Widget Settings -->
            <div id="music-settings" class="bg-gray-50 border border-gray-100 rounded-xl p-4 mb-6">
              <div class="flex items-center justify-between mb-4">
                <h4 class="text-base font-bold text-gray-900">{{ $t('settings.extraSections.musicSettings') }}</h4>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    :checked="!!musicWidget"
                    @change="
                      (e) => {
                        if ((e.target as HTMLInputElement).checked) addMusicWidget();
                        else if (musicWidget) {
                          removeWidget(musicWidget.id);
                        }
                      }
                    "
                    class="sr-only peer"
                  />
                  <div
                    class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"
                  ></div>
                </label>
              </div>

              <div v-if="musicWidget && musicWidget.data" class="space-y-3 animate-fade-in">
                <div>
                  <label class="block text-xs font-bold text-gray-600 mb-1">{{ $t('settings.extraSections.apiAddress') }}</label>
                  <input
                    v-model="musicWidget.data.apiUrl"
                    @change="store.markDirty()"
                    class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-gray-900 outline-none"
                    :placeholder="$t('settings.extraSections.placeholderMusicApiUrl')"
                  />
                </div>

                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">{{ $t('settings.sections.username') }}</label>
                    <input
                      v-model="musicWidget.data.username"
                      @change="store.markDirty()"
                      type="text"
                      class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-gray-900 outline-none"
                      :placeholder="$t('settings.extraSections.placeholderUsername')"
                      autocomplete="off"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">{{ $t('settings.sections.password') }}</label>
                    <input
                      v-model="musicWidget.data.password"
                      @change="store.markDirty()"
                      type="password"
                      class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-gray-900 outline-none"
                      :placeholder="$t('settings.extraSections.placeholderPassword')"
                      autocomplete="new-password"
                    />
                  </div>
                </div>

                <div class="flex items-center gap-2 mt-2">
                  <button
                    @click="testMusicAuth"
                    class="px-3 py-1.5 bg-gray-900 hover:bg-gray-800 text-white text-xs rounded transition-colors flex items-center gap-1"
                    :disabled="isTestingMusicAuth"
                  >
                    <span v-if="isTestingMusicAuth" class="animate-spin text-xs">●</span>
                    {{ isTestingMusicAuth ? $t('settings.extraSections.loggingIn') : $t('settings.extraSections.loginAndTest') }}
                  </button>
                  <span
                    v-if="testMusicAuthResult"
                    class="text-xs"
                    :class="testMusicAuthResult.success ? 'text-gray-600' : 'text-gray-500'"
                  >
                    {{ testMusicAuthResult.message }}
                  </span>
                  <span class="text-[15px] text-gray-400"
                    >{{ $t('settings.extraSections.musicSettingsTip') }}</span
                  >
                </div>

                <div
                  v-if="musicWidget.data.token"
                  class="bg-white border border-gray-200 rounded-lg p-3"
                >
                  <div class="flex items-center gap-3">
                    <img
                      v-if="musicWidget.data.userProfile?.avatar"
                      :src="getMusicAvatarUrl(musicWidget.data.userProfile.avatar)"
                      class="w-10 h-10 rounded-full object-cover border border-gray-200 bg-white"
                      alt="Avatar"
                    />
                    <div
                      v-else
                      class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 font-bold text-sm"
                    >
                      {{
                        (
                          musicWidget.data.userProfile?.displayName ||
                          musicWidget.data.username ||
                          "U"
                        )
                          .charAt(0)
                          .toUpperCase()
                      }}
                    </div>

                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2">
                        <span class="text-sm font-bold text-gray-900 truncate">
                          {{
                            musicWidget.data.userProfile?.displayName || musicWidget.data.username
                          }}
                        </span>
                        <button
                          @click="openRenameModal"
                          class="text-xs text-gray-500 hover:text-gray-900 shrink-0"
                          :disabled="isUpdatingProfile"
                        >
                          {{ $t('settings.extraSections.editProfile') }}
                        </button>
                      </div>
                      <div class="text-[10px] text-gray-500 truncate">
                        {{
                          musicWidget.data.userProfile?.id
                            ? `ID: ${musicWidget.data.userProfile.id}`
                            : $t('settings.extraSections.notFetchedProfile')
                        }}
                      </div>
                    </div>

                    <button
                      @click="
                        () => {
                          if (musicWidget && musicWidget.data) {
                            musicWidget.data.token = '';
                            musicWidget.data.userProfile = null;
                            store.markDirty();
                            testMusicAuthResult = null;
                          }
                        }
                      "
                      class="px-3 py-1.5 bg-gray-100 border border-gray-200 text-gray-600 rounded-lg text-xs font-bold hover:bg-gray-200 transition-colors"
                    >
                      {{ $t('settings.extraSections.logoutMusic') }}
                    </button>
                  </div>
                </div>

                <div>
                  <label class="block text-xs font-bold text-gray-600 mb-2">{{ $t('settings.extraSections.componentSize') }}</label>
                  <div class="flex items-center gap-4">
                    <div class="flex gap-3">
                      <label class="flex items-center gap-2 cursor-pointer">
                        <input
                          type="radio"
                          name="music-size"
                          :checked="selectedMusicSize.cols === 1 && selectedMusicSize.rows === 1"
                          @change="selectedMusicSize = { cols: 1, rows: 1 }"
                          class="text-gray-900 accent-blue-400"
                        />
                        <span class="text-sm">{{ $t('settings.extraSections.mini') }}</span>
                      </label>
                      <label class="flex items-center gap-2 cursor-pointer">
                        <input
                          type="radio"
                          name="music-size"
                          :checked="selectedMusicSize.cols === 2 && selectedMusicSize.rows === 3"
                          @change="selectedMusicSize = { cols: 2, rows: 3 }"
                          class="text-gray-900 accent-blue-400"
                        />
                        <span class="text-sm">{{ $t('settings.extraSections.standard') }}</span>
                      </label>
                    </div>
                    <button
                      v-if="
                        musicWidget.colSpan !== selectedMusicSize.cols ||
                        musicWidget.rowSpan !== selectedMusicSize.rows
                      "
                      @click="setMusicSize(selectedMusicSize.cols, selectedMusicSize.rows)"
                      class="px-3 py-1 bg-gray-900 text-white text-xs rounded hover:bg-gray-800 transition-colors animate-fade-in"
                    >
                      确定
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Custom CSS Section -->
            <div class="bg-gray-50 border border-gray-100 rounded-xl p-4 mb-6">
              <h4 class="text-base font-bold mb-4 text-gray-900">{{ $t('settings.extraSections.customCss') }}</h4>
              <div>
                <ScriptManager
                  v-if="store.appConfig.customCssList"
                  v-model="store.appConfig.customCssList"
                  type="css"
                  placeholder="/* 输入自定义 CSS 代码 */
.card-item {
  border-radius: 20px;
}"
                  @change="store.updateCustomScripts()"
                />
                <div class="text-xs text-gray-500 mt-2">
                  {{ $t('settings.extraSections.customCssTip') }}
                </div>
                <div class="mt-3 rounded-xl border border-gray-100 bg-white/70">
                  <div class="px-3 py-2 text-xs font-bold text-gray-700">{{ $t('settings.extraSections.styleVariableTable') }}</div>
                  <div
                    class="grid grid-cols-[minmax(0,1fr)_minmax(0,2fr)_minmax(0,1fr)] gap-y-2 gap-x-3 px-3 pb-3 text-xs"
                  >
                    <div class="text-[10px] font-semibold text-gray-400">{{ $t('settings.extraSections.styleVarName') }}</div>
                    <div class="text-[10px] font-semibold text-gray-400">{{ $t('settings.extraSections.styleVarDesc') }}</div>
                    <div class="text-[10px] font-semibold text-gray-400">{{ $t('settings.extraSections.styleVarValue') }}</div>
                    <template v-for="row in styleVariableRows" :key="row.name">
                      <div class="font-mono text-[11px] text-gray-700">{{ row.name }}</div>
                      <div class="text-gray-500">{{ row.desc }}</div>
                      <div class="font-mono text-[11px] text-gray-600">{{ row.value }}</div>
                    </template>
                  </div>
                  <div
                    class="flex items-center justify-between px-3 py-2 border-t border-gray-100 text-[10px] text-gray-500"
                  >
                    <span>{{ $t('settings.extraSections.styleVarContrast') }}{{ styleVariableStatus.contrast }}</span>
                    <span>{{ $t('settings.extraSections.styleVarVisual') }}{{ styleVariableStatus.visual }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Custom JS Section -->
            <div class="bg-gray-50 border border-gray-100 rounded-xl p-4 mb-6">
              <h4 class="text-base font-bold mb-4 text-gray-900">{{ $t('settings.extraSections.customJs') }}</h4>

              <div
                v-if="!store.appConfig.customJsDisclaimerAgreed"
                class="p-4 bg-white rounded-lg border border-gray-200 shadow-sm"
              >
                <h5 class="font-bold text-gray-700 mb-2 flex items-center gap-2">{{ $t('settings.extraSections.jsDisclaimerTitle') }}</h5>
                <div class="text-sm text-gray-600 mb-3 leading-relaxed">
                  {{ $t('settings.extraSections.jsDisclaimerDesc1') }}
                  <ul class="list-disc list-inside ml-2 mt-1 space-y-1 text-xs">
                    <li>{{ $t('settings.extraSections.jsDisclaimerXss') }}</li>
                    <li>{{ $t('settings.extraSections.jsDisclaimerCrash') }}</li>
                    <li>{{ $t('settings.extraSections.jsDisclaimerLeak') }}</li>
                  </ul>
                </div>
                <p class="text-sm text-gray-600 mb-4 font-bold">
                  {{ $t('settings.extraSections.jsDisclaimerDesc2') }}
                </p>
                <label class="flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    v-model="store.appConfig.customJsDisclaimerAgreed"
                    class="w-4 h-4 text-gray-900 rounded border-gray-300 focus:ring-blue-400 accent-blue-400"
                  />
                  <span class="text-sm font-medium text-gray-700"
                    >{{ $t('settings.extraSections.jsDisclaimerAgree') }}</span
                  >
                </label>
              </div>

              <div v-else>
                <ScriptManager
                  v-if="store.appConfig.customJsList"
                  v-model="store.appConfig.customJsList"
                  type="js"
                  placeholder="// 输入自定义 JS 代码
console.log('Hello from Custom JS!');
document.querySelector('.card-item').addEventListener('click', () => {
  alert('Clicked!');
});"
                  @change="store.updateCustomScripts()"
                />
                <div class="text-xs text-gray-500 mt-2 flex justify-between items-center">
                  <span>{{ $t('settings.extraSections.customJsTip') }}</span>
                  <button
                    @click="store.appConfig.customJsDisclaimerAgreed = false"
                    class="text-xs text-gray-500 hover:text-gray-600 underline"
                  >
                    撤销免责声明并禁用
                  </button>
                </div>
              </div>
            </div>

            <!-- Weather Service Settings -->
            <div class="bg-gray-50 border border-gray-100 rounded-xl p-4 mb-6">
              <div class="flex items-center justify-between mb-4">
                <h4 class="text-base font-bold text-gray-900">{{ $t('settings.extraSections.weatherServiceSettings') }}</h4>
              </div>
              <div class="space-y-3">
                <div>
                  <label class="block text-xs font-bold text-gray-600 mb-2">{{ $t('settings.extraSections.weatherSourceSelect') }}</label>
                  <div class="flex items-center gap-4 mb-3">
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        v-model="store.appConfig.weatherSource"
                        value="uapi"
                        class="text-gray-900 accent-blue-400"
                      />
                      <span class="text-sm">{{ $t('settings.extraSections.openMeteo') }}</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        v-model="store.appConfig.weatherSource"
                        value="amap"
                        class="text-gray-900 accent-blue-400"
                      />
                      <span class="text-sm">{{ $t('settings.extraSections.amapSource') }}</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        v-model="store.appConfig.weatherSource"
                        value="qweather"
                        class="text-gray-900 accent-blue-400"
                      />
                      <span class="text-sm">{{ $t('settings.extraSections.qweatherSource') }}</span>
                    </label>
                  </div>

                  <!-- OpenMeteo Settings -->
                  <div v-if="(!store.appConfig.weatherSource || store.appConfig.weatherSource === 'uapi')" class="animate-fade-in mt-2 mb-4 p-3 bg-blue-50 rounded-lg border border-blue-100">
                    <p class="text-xs text-blue-700 mb-2">
                      {{ $t('settings.extraSections.openMeteoDesc') }}
                    </p>
                    <div class="flex items-center gap-2">
                      <button
                        @click="testWeatherConnection('uapi')"
                        class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors flex items-center gap-1"
                        :disabled="isTestingWeather"
                      >
                        <span v-if="isTestingWeather" class="animate-spin text-xs">●</span>
                        {{ isTestingWeather ? $t('settings.extraSections.weatherTesting') : $t('settings.extraSections.weatherTestBtn') }}
                      </button>
                      <span
                        v-if="testWeatherResult"
                        class="text-xs"
                        :class="testWeatherResult.success ? 'text-green-600' : 'text-red-500'"
                      >
                        {{ testWeatherResult.message }}
                      </span>
                    </div>
                  </div>
                </div>

                <div v-if="store.appConfig.weatherSource === 'amap'" class="animate-fade-in">
                  <label class="block text-xs font-bold text-gray-600 mb-1">{{ $t('settings.extraSections.amapApiKey') }}</label>
                  <input
                    v-model="store.appConfig.amapKey"
                    class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-gray-900 outline-none"
                    :placeholder="$t('settings.extraSections.placeholderAmapKey')"
                  />
                  <div class="flex items-center justify-between mt-2">
                    <p class="text-[10px] text-gray-500">
                      {{ $t('settings.extraSections.applyForAmapKey') }}
                    </p>
                    <button
                      @click="addAmapWeatherWidget"
                      class="px-3 py-1 text-xs font-medium bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors flex items-center gap-1"
                    >
                      <span>+</span> {{ $t('settings.extraSections.addWeatherComponentToDesktop') }}
                    </button>
                  </div>
                </div>

                <div
                  v-if="store.appConfig.weatherSource === 'qweather'"
                  class="animate-fade-in space-y-2"
                >
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Project ID</label>
                    <input
                      v-model="store.appConfig.qweatherProjectId"
                      class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-gray-900 outline-none"
                      placeholder="请输入 Project ID"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Key ID</label>
                    <input
                      v-model="store.appConfig.qweatherKeyId"
                      class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-gray-900 outline-none"
                      placeholder="请输入 Key ID"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Private Key</label>
                    <textarea
                      v-model="store.appConfig.qweatherPrivateKey"
                      class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-gray-900 outline-none min-h-[80px]"
                      placeholder="请输入 Private Key (需包含 -----BEGIN PRIVATE KEY----- 头尾)"
                    ></textarea>
                  </div>
                  <p class="text-[10px] text-gray-500 mt-1">
                    请前往
                    <a
                      href="https://console.qweather.com/"
                      target="_blank"
                      class="text-gray-600 underline hover:text-gray-900"
                      >和风天气控制台</a
                    >
                    获取 JWT 凭证。
                  </p>
                  <div class="flex items-center gap-2 mt-2">
                    <button
                      @click="testWeatherConnection('qweather')"
                      class="px-3 py-1.5 bg-gray-900 hover:bg-gray-800 text-white text-xs rounded transition-colors flex items-center gap-1"
                      :disabled="isTestingWeather"
                    >
                      <span v-if="isTestingWeather" class="animate-spin text-xs">●</span>
                      {{ isTestingWeather ? "测试中..." : "测试连接" }}
                    </button>
                    <span
                      v-if="testWeatherResult"
                      class="text-xs"
                      :class="testWeatherResult.success ? 'text-gray-600' : 'text-gray-500'"
                    >
                      {{ testWeatherResult.message }}
                    </span>
                  </div>
                </div>

                <div>
                  <label class="block text-xs font-bold text-gray-600 mb-1">自定义天气源 URL</label>
                  <input
                    v-model="store.appConfig.weatherApiUrl"
                    class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-gray-900 outline-none"
                    placeholder="默认使用内置源，输入 URL 以自定义"
                  />
                  <p class="text-[10px] text-gray-500 mt-1">
                    若填写，将直接请求该地址获取天气数据。返回格式需包含：
                    <code>{ data: { temp, text, city, humidity, today: { min, max } } }</code>
                  </p>
                </div>
              </div>
            </div>

            <!-- Webhook Settings -->
            <div class="bg-gray-50 border border-gray-100 rounded-xl p-4">
              <div class="flex items-center justify-between mb-4">
                <h4 class="text-base font-bold text-gray-900">{{ $t('settings.extraSections.webhookSettings') }}</h4>
              </div>

              <div class="mb-6">
                <h5 class="font-bold text-gray-900 mb-2">{{ $t('settings.extraSections.webhookAddress') }}</h5>
                <div class="flex items-center gap-2 bg-white/60 p-2 rounded border border-gray-200">
                  <code class="text-xs text-gray-600 flex-1 break-all">{{ getWebhookUrl() }}</code>
                  <button
                    @click="copyWebhookUrl"
                    class="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded hover:bg-blue-200 font-bold transition-colors"
                  >
                    复制
                  </button>
                </div>
                <p class="text-xs text-gray-500 mt-2">
                  请在 STUN 穿透配置中，将全局 Webhook 的地址设置为上述地址，并使用以下配置：
                </p>

                <div class="mt-3 space-y-3 bg-white/60 p-3 rounded-lg border border-gray-200">
                  <div>
                    <div class="flex items-center gap-2 mb-1">
                      <span class="text-xs font-bold text-gray-700">{{ $t('settings.extraSections.webhookHeader') }}</span>
                    </div>
                    <code
                      class="block text-xs text-gray-600 font-mono bg-gray-50 p-1.5 rounded border border-gray-200"
                      >Content-Type: application/json</code
                    >
                  </div>
                  <div>
                    <div class="flex items-center gap-2 mb-1">
                      <span class="text-xs font-bold text-gray-700">{{ $t('settings.extraSections.webhookBody') }}</span>
                    </div>
                    <pre
                      class="text-xs text-gray-600 font-mono bg-gray-50 p-1.5 rounded border border-gray-200 whitespace-pre"
                    >
{
  "stun": "success",
  "ip": "#{ip}",
  "port": "#{port}"
}</pre
                    >
                  </div>
                </div>
              </div>

              <div class="space-y-3">
                <h5 class="font-bold text-gray-900">{{ $t('settings.extraSections.latestStatus') }}</h5>
                <div
                  v-if="store.luckyStunData && store.luckyStunData.data"
                  class="grid grid-cols-2 gap-3"
                >
                  <div class="bg-white/60 p-3 rounded-lg border border-gray-200">
                    <div class="text-xs text-gray-500 mb-1">{{ $t('settings.extraSections.statusLabel') }}</div>
                    <div
                      class="font-bold"
                      :class="
                        store.luckyStunData.data.stun === 'success'
                          ? 'text-gray-900'
                          : 'text-gray-500'
                      "
                    >
                      {{ store.luckyStunData.data.stun || "未知" }}
                    </div>
                  </div>
                  <div class="bg-white/60 p-3 rounded-lg border border-gray-200">
                    <div class="text-xs text-gray-500 mb-1">{{ $t('settings.extraSections.pubIp') }}</div>
                    <div class="font-bold text-gray-900 font-mono break-all">
                      {{ store.luckyStunData.data.ip || "-" }}
                    </div>
                  </div>
                  <div class="bg-white/60 p-3 rounded-lg border border-gray-200">
                    <div class="text-xs text-gray-500 mb-1">{{ $t('settings.extraSections.port') }}</div>
                    <div class="font-bold text-gray-900">
                      {{ store.luckyStunData.data.port || "-" }}
                    </div>
                  </div>
                  <div class="bg-white/60 p-3 rounded-lg border border-gray-200">
                    <div class="text-xs text-gray-500 mb-1">{{ $t('settings.extraSections.updateTime') }}</div>
                    <div class="text-xs text-gray-900">
                      {{ formatTime(store.luckyStunData.ts) }}
                    </div>
                  </div>
                </div>
                <div
                  v-else
                  class="text-center py-8 text-gray-400 text-sm bg-white rounded-xl border border-dashed border-gray-200"
                >
                  {{ $t('settings.extraSections.noWebhookData') }}
                </div>
              </div>

              <div class="flex justify-end mt-4">
                <button
                  @click="store.fetchLuckyStunData"
                  class="text-sm text-gray-500 hover:text-gray-900 hover:underline flex items-center gap-1 font-bold transition-colors"
                >
                  <span>🔄</span> {{ $t('settings.extraSections.refreshData') }}
                </button>
              </div>
            </div>

          </div>

</template>
