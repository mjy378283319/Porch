package handlers

import (
	"bytes"
	"encoding/json"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"flatnasgo-backend/config"

	"github.com/gin-gonic/gin"
)

// 最小合法 1x1 PNG
var tinyPNG = []byte{
	0x89, 'P', 'N', 'G', 0x0d, 0x0a, 0x1a, 0x0a,
	0x00, 0x00, 0x00, 0x0d, 'I', 'H', 'D', 'R',
	0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
	0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4,
	0x89, 0x00, 0x00, 0x00, 0x0d, 'I', 'D', 'A', 'T',
	0x08, 0xd7, 0x63, 0xf8, 0xcf, 0xc0, 0xf0, 0x1f,
	0x00, 0x05, 0x00, 0x01, 0xff, 0x9a, 0x18, 0x8b,
	0x00, 0x00, 0x00, 0x00, 'I', 'E', 'N', 'D', 0xae,
	0x42, 0x60, 0x82,
}

func TestSharedIconsUploadListDelete(t *testing.T) {
	gin.SetMode(gin.TestMode)
	tempDir := t.TempDir()
	oldDir := config.SharedIconsDir
	config.SharedIconsDir = filepath.Join(tempDir, "shared-icons")
	if err := os.MkdirAll(config.SharedIconsDir, 0755); err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { config.SharedIconsDir = oldDir })

	router := gin.New()
	router.GET("/api/shared-icons", ListSharedIcons)
	router.POST("/api/shared-icons/upload", UploadSharedIcons)
	router.DELETE("/api/shared-icons/:name", DeleteSharedIcon)

	var body bytes.Buffer
	writer := multipart.NewWriter(&body)
	part, err := writer.CreateFormFile("files", "test.png")
	if err != nil {
		t.Fatal(err)
	}
	if _, err := part.Write(tinyPNG); err != nil {
		t.Fatal(err)
	}
	_ = writer.Close()
	req := httptest.NewRequest(http.MethodPost, "/api/shared-icons/upload", &body)
	req.Header.Set("Content-Type", writer.FormDataContentType())
	rec := httptest.NewRecorder()
	router.ServeHTTP(rec, req)
	if rec.Code != http.StatusOK {
		t.Fatalf("upload status=%d body=%s", rec.Code, rec.Body.String())
	}
	var uploaded struct {
		Success bool             `json:"success"`
		Icons   []sharedIconItem `json:"icons"`
	}
	if err := json.Unmarshal(rec.Body.Bytes(), &uploaded); err != nil {
		t.Fatal(err)
	}
	if !uploaded.Success || len(uploaded.Icons) != 1 {
		t.Fatalf("unexpected upload result: %s", rec.Body.String())
	}
	name := uploaded.Icons[0].Name
	if !strings.HasSuffix(name, ".png") {
		t.Fatalf("bad name: %s", name)
	}

	rec = httptest.NewRecorder()
	router.ServeHTTP(rec, httptest.NewRequest(http.MethodGet, "/api/shared-icons", nil))
	if rec.Code != http.StatusOK || !strings.Contains(rec.Body.String(), name) {
		t.Fatalf("list failed: %d %s", rec.Code, rec.Body.String())
	}

	rec = httptest.NewRecorder()
	router.ServeHTTP(rec, httptest.NewRequest(http.MethodDelete, "/api/shared-icons/..%2Fsecret.png", nil))
	if rec.Code != http.StatusBadRequest && rec.Code != http.StatusNotFound {
		t.Fatalf("traversal not rejected: %d %s", rec.Code, rec.Body.String())
	}

	rec = httptest.NewRecorder()
	router.ServeHTTP(rec, httptest.NewRequest(http.MethodDelete, "/api/shared-icons/"+name, nil))
	if rec.Code != http.StatusOK {
		t.Fatalf("delete failed: %d %s", rec.Code, rec.Body.String())
	}
	if _, err := os.Stat(filepath.Join(config.SharedIconsDir, name)); !os.IsNotExist(err) {
		t.Fatalf("file still exists after delete")
	}
}

func TestIsSafeSharedIconName(t *testing.T) {
	cases := map[string]bool{
		"abc.png":  true,
		"a b.svg":  true,
		"../x.png": false,
		"sub/x.png": false,
		"x.exe":    false,
		"x.PNG":    true,
		"a..b.png": false,
		`a\b.png`:  false,
	}
	for name, want := range cases {
		if got := isSafeSharedIconName(name); got != want {
			t.Errorf("isSafeSharedIconName(%q)=%v want %v", name, got, want)
		}
	}
}
