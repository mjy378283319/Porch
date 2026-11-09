import type { InjectionKey } from "vue";

/**
 * 设置面板共享上下文。
 *
 * SettingsModal.vue 里维护着上百个 ref/computed/函数，9 个 tab 面板都要用。
 * 与其把几十个 props 层层透传（还容易漏、类型难维护），父组件统一 provide 一个
 * reactive 对象，子面板 inject 之后用 toRef 取自己需要的字段：
 *
 *   const ctx = inject(SETTINGS_CTX) as Record<string, any>;
 *   const appConfig = toRef(ctx, "appConfig");
 *
 * 用 toRef 而不是解构：解构会把 reactive 解包后的值定格在当时，
 * toRef 的读取会追踪依赖、写入会回写到原 ref，v-model 才依然可写。
 */
export const SETTINGS_CTX: InjectionKey<Record<string, any>> = Symbol("flatnas:settings-ctx");
