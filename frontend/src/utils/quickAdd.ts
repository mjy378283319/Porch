import type { BookmarkCategory, BookmarkItem } from "@/types";

const PREFIX = "#add=";

interface QuickAddOptions {
  getWidgets: () => any[];
  markDirty: () => void;
}

/**
 * 处理「快速收藏」小书签跳转，形如 `#add=<url>&title=<title>`。
 *
 * 设计取舍：小书签只做一次页面跳转，不在目标站点注入任何脚本，
 * 因此不会拖慢任何网站（上游浏览器助手在有站点的页面上会一直转圈）。
 * 令牌不离开 Porch 自己这一侧，跨站也不需要 CORS。
 *
 * @returns 需要提示给用户的结果文案；当前 URL 不是快速收藏跳转时返回 null
 */
export function consumeQuickAdd(options: QuickAddOptions): string | null {
  if (typeof window === "undefined") return null;

  const hash = window.location.hash;
  if (!hash.startsWith(PREFIX)) return null;

  const params = new URLSearchParams(hash.slice(1));
  const rawUrl = params.get("add");
  const rawTitle = params.get("title") || rawUrl || "";

  // 先清掉 hash，避免用户刷新时重复添加
  window.history.replaceState(
    null,
    "",
    window.location.pathname + window.location.search,
  );

  if (!rawUrl) return "快速收藏失败：缺少网址参数";

  let url = rawUrl.trim();
  if (!/^https?:\/\//i.test(url)) url = "http://" + url;

  const widget = options.getWidgets().find((w) => w?.type === "bookmarks");
  if (!widget) return "快速收藏失败：请先在设置里启用「收藏夹」组件";

  const categories: BookmarkCategory[] = Array.isArray(widget.data) ? widget.data : [];
  if (!categories.length) return "快速收藏失败：收藏夹里还没有分类";

  const target = categories[0];
  if (!Array.isArray(target.children)) target.children = [];

  const duplicated = target.children.some(
    (child) => (child as BookmarkItem)?.url === url,
  );
  if (duplicated) return `已收藏过：${rawTitle || url}`;

  const item: BookmarkItem = {
    id: `${Date.now()}`,
    title: rawTitle.trim() || url,
    url,
    type: "link",
  };
  target.children.push(item);
  options.markDirty();

  return `已收藏到「${target.title || "默认分类"}」：${item.title}`;
}

/**
 * 生成可拖到书签栏的「快速收藏」小书签代码。
 * 指向当前部署地址，子路径部署时同样可用。
 */
export function buildQuickAddBookmarklet(): string {
  if (typeof window === "undefined") return "";
  const base = window.location.origin + window.location.pathname.replace(/[^/]*$/, "");
  return (
    "javascript:(function(){var u=encodeURIComponent(location.href)," +
    "t=encodeURIComponent(document.title||'');" +
    `var w=window.open('${base}#add='+u+'&title='+t,'_blank');` +
    `if(!w)location.href='${base}#add='+u+'&title='+t;})()`
  );
}
