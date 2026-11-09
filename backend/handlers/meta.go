package handlers

import (
	"html"
	"io"
	"net/http"
	"net/url"
	"regexp"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// 只做"够用"的解析：标题与图标。导航页的书签大多结构简单，
// 引入完整的 HTML 解析器（golang.org/x/net/html）会多一个依赖且没必要。
var (
	metaTitleRe = regexp.MustCompile(`(?is)<title[^>]*>(.*?)</title>`)
	metaLinkRe  = regexp.MustCompile(`(?is)<link\b[^>]*>`)
	metaHrefRe  = regexp.MustCompile(`(?is)href\s*=\s*["']([^"']+)["']`)
	metaRelRe   = regexp.MustCompile(`(?is)rel\s*=\s*["']([^"']+)["']`)
)

// metaMaxBytes 限制读取体积，避免把大文件整个读进内存。
const metaMaxBytes = 512 << 10

var metaClient = &http.Client{
	Timeout: 8 * time.Second,
}

// FetchMeta 抓取目标网页的标题与图标，供「添加书签」自动填充。
//
// 返回 {"title": "...", "icon": "https://..."}；抓取失败不报错，
// 一律返回 200 + 空字段，让前端走自己的 favicon 兜底，避免控制台刷 500。
func FetchMeta(c *gin.Context) {
	raw := strings.TrimSpace(c.Query("url"))
	if raw == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "url is required"})
		return
	}
	if !strings.Contains(raw, "://") {
		raw = "http://" + raw
	}

	parsed, err := url.Parse(raw)
	if err != nil || parsed.Host == "" || (parsed.Scheme != "http" && parsed.Scheme != "https") {
		c.JSON(http.StatusBadRequest, gin.H{"error": "unsupported url"})
		return
	}

	result := gin.H{"title": "", "icon": ""}

	req, err := http.NewRequest(http.MethodGet, parsed.String(), nil)
	if err != nil {
		c.JSON(http.StatusOK, result)
		return
	}
	req.Header.Set("User-Agent", "Mozilla/5.0 (compatible; FlatNas/1.0)")
	req.Header.Set("Accept", "text/html,application/xhtml+xml")

	resp, err := metaClient.Do(req)
	if err != nil {
		c.JSON(http.StatusOK, result)
		return
	}
	defer resp.Body.Close()

	bodyBytes, _ := io.ReadAll(io.LimitReader(resp.Body, metaMaxBytes))
	body := string(bodyBytes)

	if m := metaTitleRe.FindStringSubmatch(body); len(m) > 1 {
		// 压缩连续空白并解实体（&amp; 之类），否则书签标题会带一堆换行
		title := strings.Join(strings.Fields(html.UnescapeString(m[1])), " ")
		if runes := []rune(title); len(runes) > 120 {
			title = string(runes[:120])
		}
		if title != "" {
			result["title"] = title
		}
	}

	icon := ""
	contentType := strings.ToLower(resp.Header.Get("Content-Type"))
	// Content-Type 缺失时也尝试解析，很多小站不给这个头
	if contentType == "" || strings.Contains(contentType, "html") {
		icon = pickIconURL(body, parsed)
	}
	if icon == "" {
		// 兜底：绝大多数站点根目录都有 favicon.ico
		icon = parsed.Scheme + "://" + parsed.Host + "/favicon.ico"
	}
	result["icon"] = icon

	c.JSON(http.StatusOK, result)
}

// pickIconURL 从 <link rel="...icon..."> 里挑图标，把相对路径转成绝对地址。
// apple-touch-icon 通常是大尺寸图标，优先返回；否则取第一个声明的 icon。
func pickIconURL(pageHTML string, base *url.URL) string {
	fallback := ""
	for _, tag := range metaLinkRe.FindAllString(pageHTML, 50) {
		rel := ""
		if m := metaRelRe.FindStringSubmatch(tag); len(m) > 1 {
			rel = strings.ToLower(m[1])
		}
		if !strings.Contains(rel, "icon") {
			continue
		}

		href := ""
		if m := metaHrefRe.FindStringSubmatch(tag); len(m) > 1 {
			href = strings.TrimSpace(m[1])
		}
		// data: 内联图标虽然能用，但体积可能很大，交给前端兜底
		if href == "" || strings.HasPrefix(href, "data:") {
			continue
		}

		abs := resolveMetaURL(base, href)
		if abs == "" {
			continue
		}
		if strings.Contains(rel, "apple-touch-icon") {
			return abs
		}
		if fallback == "" {
			fallback = abs
		}
	}
	return fallback
}

// resolveMetaURL 把可能的相对引用解析成绝对 URL，解析不出来就返回空串。
func resolveMetaURL(base *url.URL, ref string) string {
	u, err := url.Parse(ref)
	if err != nil {
		return ""
	}
	resolved := base.ResolveReference(u)
	if resolved.Host == "" || (resolved.Scheme != "http" && resolved.Scheme != "https") {
		return ""
	}
	return resolved.String()
}
