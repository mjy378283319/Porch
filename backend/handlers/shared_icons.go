package handlers

import (
	"crypto/sha256"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"flatnasgo-backend/config"

	"github.com/gin-gonic/gin"
)

// 共享图标：用户上传后可通过 /shared-icons/<file> 公开直链访问，供 Porch、
// 其它容器或 Unraid 应用引用。上传/删除需登录，列表公开便于外部应用枚举。

const maxSharedIconSize = 5 * 1024 * 1024

type sharedIconItem struct {
	Name       string `json:"name"`
	Path       string `json:"path"`
	SizeBytes  int64  `json:"sizeBytes"`
	ModifiedAt string `json:"modifiedAt"`
}

func isSafeSharedIconName(name string) bool {
	if name == "" || name != filepath.Base(name) {
		return false
	}
	if strings.Contains(name, "..") || strings.ContainsAny(name, "/\\") {
		return false
	}
	ext := strings.ToLower(filepath.Ext(name))
	return ext == ".png" || ext == ".jpg" || ext == ".jpeg" || ext == ".gif" ||
		ext == ".webp" || ext == ".svg" || ext == ".ico"
}

// ListSharedIcons 公开枚举共享图标目录。
func ListSharedIcons(c *gin.Context) {
	entries, err := os.ReadDir(config.SharedIconsDir)
	if err != nil {
		if os.IsNotExist(err) {
			c.JSON(http.StatusOK, gin.H{"success": true, "icons": []sharedIconItem{}})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list icons"})
		return
	}

	items := make([]sharedIconItem, 0, len(entries))
	for _, entry := range entries {
		if entry.IsDir() || !isSafeSharedIconName(entry.Name()) {
			continue
		}
		info, err := entry.Info()
		if err != nil {
			continue
		}
		items = append(items, sharedIconItem{
			Name:       entry.Name(),
			Path:       "/shared-icons/" + entry.Name(),
			SizeBytes:  info.Size(),
			ModifiedAt: info.ModTime().UTC().Format(time.RFC3339),
		})
	}
	sort.Slice(items, func(i, j int) bool { return items[i].Name < items[j].Name })
	c.JSON(http.StatusOK, gin.H{"success": true, "icons": items})
}

// UploadSharedIcons 上传一个或多个图标（multipart 字段 files）。
func UploadSharedIcons(c *gin.Context) {
	form, err := c.MultipartForm()
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Bad Request", "detail": err.Error()})
		return
	}
	files := form.File["files"]
	if len(files) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No files uploaded"})
		return
	}

	// 先全部校验再写盘，避免部分成功。
	for _, file := range files {
		if file.Size > maxSharedIconSize {
			c.JSON(http.StatusRequestEntityTooLarge, gin.H{"error": "文件不能超过 5MB: " + file.Filename})
			return
		}
		content, err := file.Open()
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Cannot read " + file.Filename})
			return
		}
		buf, readErr := io.ReadAll(io.LimitReader(content, maxSharedIconSize+1))
		_ = content.Close()
		if readErr != nil || len(buf) > maxSharedIconSize {
			c.JSON(http.StatusRequestEntityTooLarge, gin.H{"error": "文件不能超过 5MB: " + file.Filename})
			return
		}
		if ext := resolveImageExtension(file.Header.Get("Content-Type"), buf); ext == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "不支持的图片格式: " + file.Filename})
			return
		}
		if strings.EqualFold(filepath.Ext(bufName(file.Filename)), ".svg") && validateSafeSVG(buf) != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "SVG 含不安全内容: " + file.Filename})
			return
		}
	}

	uploaded := make([]sharedIconItem, 0, len(files))
	for _, file := range files {
		content, err := file.Open()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Cannot read " + file.Filename})
			return
		}
		buf, err := io.ReadAll(io.LimitReader(content, maxSharedIconSize+1))
		_ = content.Close()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Cannot read " + file.Filename})
			return
		}

		ext := resolveImageExtension(file.Header.Get("Content-Type"), buf)
		// 内容寻址命名：相同内容复用同一文件，天然去重，且避免中文/特殊字符文件名。
		sum := sha256.Sum256(buf)
		name := fmt.Sprintf("%x%s", sum[:8], ext)
		target := filepath.Join(config.SharedIconsDir, name)
		if err := os.WriteFile(target, buf, defaultIconFileMode); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save " + name})
			return
		}
		info, _ := os.Stat(target)
		modifiedAt := time.Now().UTC().Format(time.RFC3339)
		if info != nil {
			modifiedAt = info.ModTime().UTC().Format(time.RFC3339)
		}
		uploaded = append(uploaded, sharedIconItem{
			Name:       name,
			Path:       "/shared-icons/" + name,
			SizeBytes:  int64(len(buf)),
			ModifiedAt: modifiedAt,
		})
	}
	c.JSON(http.StatusOK, gin.H{"success": true, "icons": uploaded})
}

func bufName(filename string) string {
	return strings.ToLower(filename)
}

// DeleteSharedIcon 删除单个共享图标。
func DeleteSharedIcon(c *gin.Context) {
	name := c.Param("name")
	if !isSafeSharedIconName(name) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid name"})
		return
	}
	target := filepath.Join(config.SharedIconsDir, name)
	absTarget, err := filepath.Abs(target)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid path"})
		return
	}
	absDir, err := filepath.Abs(config.SharedIconsDir)
	if err != nil || !strings.HasPrefix(absTarget, absDir+string(os.PathSeparator)) {
		c.JSON(http.StatusForbidden, gin.H{"error": "Permission denied"})
		return
	}
	if _, err := os.Stat(absTarget); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, gin.H{"error": "Icon not found"})
		return
	}
	if err := os.Remove(absTarget); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete icon"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"success": true})
}
