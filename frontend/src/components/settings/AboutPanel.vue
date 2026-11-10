<script setup lang="ts">
// 该面板由 SettingsModal.vue 拆分而来：模板保持原样，状态通过 inject 取父级上下文。
import { inject, toRef } from "vue";
import { SETTINGS_CTX } from "./context";

const ctx = inject(SETTINGS_CTX) as Record<string, any>;

const activeTab = toRef(ctx, "activeTab");
const store = toRef(ctx, "store");
const t = toRef(ctx, "t");
</script>

<template>
          <div v-if="activeTab === 'about'" class="min-h-full flex flex-col p-8 -mt-4">
            <div class="bg-white/60 border border-gray-100 rounded-xl p-4">
              <h5 class="text-sm font-bold text-gray-900 mb-2">{{ $t('settings.about.thanks') }}</h5>
              <div class="text-xs text-gray-600 leading-relaxed">
                <div class="text-sm">
                  <span class="font-medium text-gray-800">{{ $t('settings.about.feeders') }}：</span>
                  <span class="font-bold text-base text-gray-900">你应爱</span>；小浣熊；*俊；*牛社区主理人；*a；*甜蜜主理人；*坤；T*t;*O；*陈等
                </div>
                <div class="mt-2">
                  <span class="font-medium text-gray-800">{{ $t('settings.about.specialThanks') }}：</span>
                  Excel;徐大大;时也,命也;大星;友人A;汪仔饭;Assassin;多度;Wheezer;苍蝇炖粉条等
                </div>
              </div>
            </div>
            <div
              class="mt-4 bg-white/60 border border-gray-100 rounded-xl p-4 flex flex-row items-center justify-center gap-6"
            >
              <div
                class="text-lg font-bold text-gray-700"
                style="writing-mode: vertical-rl; text-orientation: mixed"
              >
                {{ $t('settings.about.feedAuthor') }}
              </div>
              <div class="flex flex-row flex-wrap items-start justify-center gap-6">
                <div class="flex flex-col items-center gap-2">
                  <img
                    src="/public/alipay.jpg"
                    class="w-36 h-36 rounded-lg shadow-sm border border-gray-100 object-contain transition-all"
                    alt="Alipay"
                  />
                  <span class="text-sm text-gray-500">{{ $t('settings.about.alipay') }}</span>
                </div>
                <div class="flex flex-col items-center gap-2">
                  <img
                    src="/public/wechat.jpg"
                    class="w-36 h-36 rounded-lg shadow-sm border border-gray-100 object-contain transition-all"
                    alt="WeChat"
                  />
                  <span class="text-sm text-gray-500">{{ $t('settings.about.wechat') }}</span>
                </div>
              </div>
            </div>

            <div class="mt-auto pt-4">
              <div class="bg-white/60 border border-gray-100 rounded-xl p-4">
                <div class="flex items-center justify-between gap-4">
                  <div class="flex items-baseline gap-2">
                    <span class="text-xs text-gray-500">{{ $t('settings.about.qqGroup') }}</span>
                    <span class="text-lg text-gray-700 font-mono">613835409</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-lg text-gray-400 font-mono">v{{ store.currentVersion }}</span>
                  </div>
                </div>

                <div class="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2">
                  <div class="text-xs text-gray-500">
                    {{ $t('settings.about.officialSite') }}：
                    <a
                      href="https://porch.top/"
                      target="_blank"
                      class="text-gray-600 underline hover:text-gray-900"
                    >
                      https://porch.top/
                    </a>
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ $t('settings.about.wiki') }}：
                    <a
                      href="http://qdnas.icu/"
                      target="_blank"
                      class="text-gray-600 underline hover:text-gray-900"
                    >
                      http://qdnas.icu/
                    </a>
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ $t('settings.about.iconLibrary') }}：
                    <a
                      href="https://nasicon.top/"
                      target="_blank"
                      class="text-gray-600 underline hover:text-gray-900"
                    >
                      https://nasicon.top/
                    </a>
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ $t('settings.about.iconLibrary2') }}：
                    <a
                      href="https://2.nasicon.top/"
                      target="_blank"
                      class="text-gray-600 underline hover:text-gray-900"
                    >
                      https://2.nasicon.top/
                    </a>
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ $t('settings.about.iconLibrary3') }}：
                    <a
                      href="https://4.nasicon.top/"
                      target="_blank"
                      class="text-gray-600 underline hover:text-gray-900"
                    >
                      https://4.nasicon.top/
                    </a>
                  </div>
                </div>

                <div class="mt-4 flex items-center justify-end gap-6">
                  <a
                    href="https://github.com/Garry-QD/FlatNas"
                    target="_blank"
                    class="text-gray-700 hover:text-gray-900 hover:opacity-80 transition-opacity"
                    title="GitHub"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                      class="w-6 h-6"
                    >
                      <path
                        d="M12 .296c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.332-1.754-1.332-1.754-1.09-.744.084-.729.084-.729 1.205.084 1.84 1.236 1.84 1.236 1.07 1.835 2.807 1.305 3.492.998.108-.776.418-1.305.762-1.604-2.665-.305-5.467-1.335-5.467-5.932 0-1.31.465-2.38 1.235-3.22-.135-.304-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23a11.52 11.52 0 013.003-.405c1.02.006 2.045.138 3.003.405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.872.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.922.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.296c0-6.627-5.373-12-12-12"
                      />
                    </svg>
                  </a>
                  <a
                    href="https://gitee.com/gjx0808/FlatNas"
                    target="_blank"
                    class="text-gray-700 hover:text-gray-900 hover:opacity-80 transition-opacity"
                    title="Gitee"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                      class="w-6 h-6"
                    >
                      <path
                        fill-rule="evenodd"
                        clip-rule="evenodd"
                        d="M11.984 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.811 17.914l-.943-.896c-.342-.325-.92-.332-1.19-.026l-2.72 3.067a.772.772 0 0 1-1.05.09l-6.55-5.314a.775.775 0 0 1 .1-1.267l6.894-4.003a.775.775 0 0 1  1.03.22l2.214 3.285a.775.775 0 0 0 1.19.12l1.024-.967a.775.775 0 0 0 .08-1.02l-3.65-5.504a.775.775 0 0 0-1.17-.14l-8.78 7.32a.775.775 0 0 0-.15 1.08l7.87 6.38a.775.775 0 0 0 1.05-.09l3.58-4.034a.775.775 0 0 0 .02-1.08z"
                      />
                    </svg>
                  </a>
                  <a
                    href="https://hub.docker.com/r/qdnas/flatnas"
                    target="_blank"
                    class="text-blue-600 hover:text-blue-700 hover:opacity-80 transition-opacity"
                    title="Docker"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                      class="w-6 h-6"
                    >
                      <path
                        d="M13.84 10.74H16v2.14h-2.16v-2.14zm-2.38 0h2.16v2.14h-2.16v-2.14zm-2.38 0h2.16v2.14H9.08v-2.14zm-2.38 0h2.16v2.14H6.7v-2.14zm2.38-2.32h2.16v2.14H9.08V8.42zm2.38 0h2.16v2.14h-2.16V8.42zm-2.38-2.32h2.16v2.14H9.08V6.1zM22.45 11.09c-.2-.14-.66-.28-1.2-.2a3.22 3.22 0 00-1.52.72 4.86 4.86 0 00-.98-1.6l-.22-.2-.2.22a4.42 4.42 0 00-.9 1.46 8.92 8.92 0 00-.56 2.1H1.53a.25.25 0 00-.24.28 8.47 8.47 0 001.14 3.24c1.22 1.86 3.22 2.8 5.98 2.8 5.98 0 10.4-2.76 12.16-7.56.66.04 2.08-.02 2.42-1.3.02-.06.18-.72-.54-1.06z"
                      />
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          </div>

</template>
