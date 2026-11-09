<script setup lang="ts">
// 该面板由 SettingsModal.vue 拆分而来：模板保持原样，状态通过 inject 取父级上下文。
import { inject, toRef } from "vue";
import { SETTINGS_CTX } from "./context";

const ctx = inject(SETTINGS_CTX) as Record<string, any>;

const activeTab = toRef(ctx, "activeTab");
const canManageUsers = toRef(ctx, "canManageUsers");
const deleteVersion = toRef(ctx, "deleteVersion");
const fileInput = toRef(ctx, "fileInput");
const handleAddUser = toRef(ctx, "handleAddUser");
const handleChangePassword = toRef(ctx, "handleChangePassword");
const handleDeleteUser = toRef(ctx, "handleDeleteUser");
const handleExport = toRef(ctx, "handleExport");
const handleFileChange = toRef(ctx, "handleFileChange");
const handleLogin = toRef(ctx, "handleLogin");
const handleReset = toRef(ctx, "handleReset");
const handleSaveAsDefault = toRef(ctx, "handleSaveAsDefault");
const handleUploadLicense = toRef(ctx, "handleUploadLicense");
const hasAdminAccess = toRef(ctx, "hasAdminAccess");
const licenseKey = toRef(ctx, "licenseKey");
const loadingVersions = toRef(ctx, "loadingVersions");
const newPasswordInput = toRef(ctx, "newPasswordInput");
const newPwd = toRef(ctx, "newPwd");
const newUser = toRef(ctx, "newUser");
const passwordInput = toRef(ctx, "passwordInput");
const restoreVersion = toRef(ctx, "restoreVersion");
const saveDefaultBtnText = toRef(ctx, "saveDefaultBtnText");
const saveVersion = toRef(ctx, "saveVersion");
const showPassword = toRef(ctx, "showPassword");
const store = toRef(ctx, "store");
const t = toRef(ctx, "t");
const toggleAuthMode = toRef(ctx, "toggleAuthMode");
const triggerImport = toRef(ctx, "triggerImport");
const userList = toRef(ctx, "userList");
const versionLabel = toRef(ctx, "versionLabel");
const versions = toRef(ctx, "versions");
</script>

<template>
          <div v-if="activeTab === 'account'" class="min-h-full flex flex-col justify-center">
            <div v-if="!store.isLogged" class="text-center">
              <h4 class="text-xl font-bold mb-6 text-gray-900">{{ $t('settings.extraSections.loginAsAdmin') }}</h4>
              <input
                v-model="passwordInput"
                type="password"
                :placeholder="$t('settings.extraSections.placeholderPasswordLogin')"
                class="w-full max-w-xs px-4 py-3 border border-gray-200 rounded-xl mb-4 mx-auto text-center focus:border-gray-900 outline-none"
                @keyup.enter="handleLogin"
              />
              <button
                @click="handleLogin"
                class="bg-gray-900 text-white px-10 py-3 rounded-xl font-bold hover:bg-gray-800 transition-colors"
              >
                登 录
              </button>
            </div>
            <div v-else class="max-w-sm mx-auto w-full">
              <div class="bg-gray-50 p-5 rounded-xl border border-gray-100 mb-6">
                <h5 class="text-sm font-bold text-gray-900 mb-3">{{ $t('settings.extraSections.backupRestoreSection') }}</h5>
                <div class="grid grid-cols-2 gap-3">
                  <button
                    @click="handleExport"
                    class="col-span-2 bg-white text-gray-700 border border-gray-200 px-4 py-2 rounded-lg text-sm font-bold hover:bg-gray-50 transition-colors"
                  >
                    📤 导出配置
                  </button>
                  <button
                    @click="triggerImport"
                    class="col-span-2 bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-gray-800 transition-colors"
                  >
                    📥 导入配置
                  </button>
                  <button
                    v-if="hasAdminAccess"
                    @click="handleSaveAsDefault"
                    class="bg-gray-800 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-gray-900 transition-all"
                  >
                    {{ saveDefaultBtnText }}
                  </button>
                  <button
                    @click="handleReset"
                    class="bg-white text-gray-600 border border-gray-200 px-4 py-2 rounded-lg text-sm font-bold hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors"
                  >
                    🧹 恢复初始化
                  </button>
                  <input
                    ref="fileInput"
                    type="file"
                    accept=".navbak,.json"
                    class="hidden"
                    @change="handleFileChange"
                  />
                </div>
              </div>
              <div
                v-if="hasAdminAccess"
                class="bg-gray-50 p-5 rounded-xl border border-gray-200 mb-6"
              >
                <h5 class="text-sm font-bold text-gray-900 mb-3">{{ $t('settings.extraSections.systemMode') }}</h5>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-700"
                    >当前模式：{{
                      store.systemConfig.authMode === "single" ? $t('settings.extraSections.singleUserMode') : $t('settings.extraSections.multiUserMode')
                    }}</span
                  >
                  <button
                    v-if="hasAdminAccess"
                    @click="toggleAuthMode"
                    class="px-4 py-2 rounded-lg text-sm font-bold text-white transition-all bg-gray-900 hover:bg-gray-800"
                  >
                    {{ $t('settings.extraSections.switchToMode', { mode: store.systemConfig.authMode === 'single' ? $t('settings.extraSections.multiUserMode') : $t('settings.extraSections.singleUserMode') }) }}
                  </button>
                  <span
                    v-else
                    class="px-4 py-2 rounded-lg text-sm font-bold text-gray-500 bg-gray-100"
                  >
                    仅管理员可切换
                  </span>
                </div>
                <p class="text-xs text-gray-500 mt-2">
                  {{
                    store.systemConfig.authMode === "single"
                      ? $t('settings.extraSections.singleModeHint')
                      : $t('settings.extraSections.multiModeHint')
                  }}
                </p>
                <p class="text-xs text-gray-500 mt-1">
                  {{ $t('settings.extraSections.defaultPasswords') }}
                </p>
              </div>
              <div class="bg-gray-50 p-5 rounded-xl border border-gray-200 mb-6">
                <h5 class="text-sm font-bold text-gray-900 mb-3">{{ $t('settings.extraSections.configVersionsSection') }}</h5>
                <div class="flex gap-2 items-center mb-2">
                  <input
                    v-model="versionLabel"
                    :placeholder="$t('settings.extraSections.placeholderVersionLabel')"
                    class="flex-1 px-3 py-2 rounded-lg border border-gray-300 text-sm focus:border-gray-900 outline-none"
                  />
                  <button
                    @click="saveVersion"
                    class="px-4 py-2 rounded-lg text-sm font-bold text-white transition-all bg-gray-900 hover:bg-gray-800"
                  >
                    保存为版本
                  </button>
                </div>
                <div class="text-[10px] text-gray-500 mb-2">
                  {{
                    store.systemConfig.authMode === "single"
                      ? $t('settings.extraSections.saveLocation')
                      : $t('settings.extraSections.saveLocationUser')
                  }}
                </div>
                <div class="max-h-40 overflow-y-auto space-y-1">
                  <div v-if="loadingVersions" class="text-xs text-gray-500">{{ $t('settings.extraSections.loadingVersions') }}</div>
                  <div v-else-if="versions.length === 0" class="text-xs text-gray-400 text-center py-4">
                    {{ $t('settings.extraSections.noVersionsSaved') }}
                  </div>
                  <div
                    v-for="v in versions"
                    :key="v.id"
                    class="flex items-center justify-between bg-white px-3 py-2 rounded-lg border border-gray-200"
                  >
                    <div class="flex-1">
                      <div class="text-sm font-medium text-gray-900 truncate">
                        {{ v.label || $t('settings.extraSections.unnamedVersion') }}
                      </div>
                      <div class="text-[10px] text-gray-500">
                        {{ new Date(v.createdAt).toLocaleString() }} ·
                        {{ Math.round(v.size / 1024) }}KB
                      </div>
                    </div>
                    <div class="flex gap-2">
                      <button
                        @click="restoreVersion(v.id)"
                        class="text-xs px-2 py-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
                      >
                        恢复
                      </button>
                      <button
                        @click="deleteVersion(v.id)"
                        class="text-xs px-2 py-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
                      >
                        删除
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div class="bg-gray-50 p-5 rounded-xl border border-gray-200 mb-6">
                <h5 class="text-sm font-medium text-gray-700 mb-1">{{ $t('settings.extraSections.changePasswordSection') }}</h5>
                <p class="text-xs text-gray-500 mb-2">{{ $t('settings.extraSections.modifyPasswordHint') }}</p>
                <div class="flex gap-2">
                  <div class="relative flex-1">
                    <input
                      v-model="newPasswordInput"
                      :type="showPassword ? 'text' : 'password'"
                      :placeholder="$t('settings.extraSections.placeholderNewPassword')"
                      class="w-full px-3 py-2 rounded-lg border border-gray-300 pr-10 focus:border-gray-900 outline-none"
                    />
                    <button
                      @click="showPassword = !showPassword"
                      class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 focus:outline-none"
                      type="button"
                      tabindex="-1"
                      :title="showPassword ? $t('settings.extraSections.hidePassword') : $t('settings.extraSections.showPassword')"
                    >
                      <svg
                        v-if="showPassword"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke-width="1.5"
                        stroke="currentColor"
                        class="w-5 h-5"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"
                        />
                      </svg>
                      <svg
                        v-else
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke-width="1.5"
                        stroke="currentColor"
                        class="w-5 h-5"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
                        />
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                      </svg>
                    </button>
                  </div>
                  <button
                    @click="handleChangePassword"
                    class="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm hover:bg-gray-800 transition-colors"
                  >
                    修改
                  </button>
                </div>
              </div>
              <!-- Admin User Management UI -->
              <div
                v-if="canManageUsers"
                class="bg-gray-50 p-5 rounded-xl border border-gray-200 mb-6"
              >
                <h5 class="text-sm font-bold text-gray-900 mb-3">👥 用户管理 (Admin)</h5>

                <!-- Add User -->
                <div class="flex flex-col gap-2 mb-4">
                  <div class="flex gap-2">
                    <input
                      v-model="newUser"
                      placeholder="用户名"
                      class="flex-1 px-3 py-2 rounded-lg border border-gray-300 text-sm focus:border-gray-900 outline-none"
                    />
                    <input
                      v-model="newPwd"
                      type="password"
                      placeholder="密码"
                      class="flex-1 px-3 py-2 rounded-lg border border-gray-300 text-sm focus:border-gray-900 outline-none"
                    />
                  </div>
                  <button
                    @click="handleAddUser"
                    class="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-gray-800 transition-colors"
                  >
                    添加用户
                  </button>
                </div>

                <!-- User List -->
                <div class="space-y-2 max-h-40 overflow-y-auto">
                  <div
                    v-for="u in userList"
                    :key="u"
                    class="flex justify-between items-center bg-white px-3 py-2 rounded-lg border border-gray-200"
                  >
                    <span class="text-sm text-gray-700 font-medium">
                      {{ u }}
                      <span v-if="u === 'admin'" class="text-xs text-gray-500">{{ $t('settings.extraSections.admin') }}</span>
                    </span>
                    <button
                      v-if="u !== 'admin'"
                      @click="handleDeleteUser(u)"
                      class="text-gray-400 hover:text-gray-600 text-xs font-bold px-2"
                    >
                      删除
                    </button>
                  </div>
                </div>

                <!-- License Management -->
                <div class="mt-4 pt-4 border-t border-gray-200">
                  <h6 class="text-xs font-bold text-gray-900 mb-2">🔑 授权密钥 (License Key)</h6>
                  <div class="flex gap-2">
                    <input
                      v-model="licenseKey"
                      :placeholder="$t('settings.extraSections.placeholderLicenseKey')"
                      class="flex-1 px-3 py-2 rounded-lg border border-gray-300 text-sm focus:border-gray-900 outline-none"
                    />
                    <button
                      @click="handleUploadLicense"
                      class="bg-gray-900 text-white px-3 py-2 rounded-lg text-sm font-bold hover:bg-gray-800 whitespace-nowrap transition-colors"
                    >
                      导入
                    </button>
                  </div>
                  <p class="text-[10px] text-gray-500 mt-1">
                    导入有效密钥可解除5个用户的注册限制。
                  </p>
                </div>
              </div>

              <button
                @click="store.logout"
                class="w-full text-gray-700 py-3 rounded-xl font-bold border border-gray-200 transition-colors glass-chip selectable-outline"
              >
                退出登录
              </button>
            </div>
          </div>
</template>
