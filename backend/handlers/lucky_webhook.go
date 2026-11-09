package handlers

import (
	"encoding/json"
	"net/http"
	"sync"
	"time"

	"github.com/gin-gonic/gin"

	"flatnasgo-backend/ws"
)

// luckyStunSnapshot 与前端 types.ts 里的 LuckyStunData 对齐。
// 面板读的是 data.stun / data.ip / data.port，时间戳单独放在 ts。
type luckyStunSnapshot struct {
	TS   int64                  `json:"ts"`
	Data map[string]interface{} `json:"data"`
}

var (
	luckyStunMu   sync.RWMutex
	luckyStunLast *luckyStunSnapshot
)

// LuckyStunWebhook 接收 Lucky 的 STUN 穿透状态回调。
//
// 这条路由必须匿名可访问：Lucky 在 STUN 规则里配置的全局 Webhook 只会按
// 「Content-Type: application/json」POST JSON，不会带 FlatNas 的 JWT。
// 请求体形如 {"stun":"success","ip":"1.2.3.4","port":12345}，按原样透传，
// 多余字段保留，方便 Lucky 后续版本加字段时不用改这里。
func LuckyStunWebhook(c *gin.Context) {
	body := map[string]interface{}{}
	if err := json.NewDecoder(c.Request.Body).Decode(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid json body"})
		return
	}
	if body == nil {
		body = map[string]interface{}{}
	}

	snap := &luckyStunSnapshot{
		TS:   time.Now().UnixMilli(),
		Data: body,
	}

	luckyStunMu.Lock()
	luckyStunLast = snap
	luckyStunMu.Unlock()

	if b := ws.GetBroadcaster(); b != nil {
		b.BroadcastLuckyStun(snap)
	}

	c.JSON(http.StatusOK, gin.H{"ok": true, "ts": snap.TS})
}

// GetLuckyStun 返回最近一次 webhook 快照，供设置面板的「刷新数据」按钮拉取。
// 从未收到过回调时 data 为 null，前端据此显示"暂无 Webhook 数据"。
func GetLuckyStun(c *gin.Context) {
	luckyStunMu.RLock()
	snap := luckyStunLast
	luckyStunMu.RUnlock()

	if snap == nil {
		c.JSON(http.StatusOK, gin.H{"ts": 0, "data": nil})
		return
	}
	c.JSON(http.StatusOK, snap)
}
