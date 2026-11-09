SHELL := /bin/bash
VERSION ?= 1.2.6
REGISTRY ?= ghcr.io
OWNER ?= your-name
IMAGE := $(REGISTRY)/$(OWNER)/flatnas
PLATFORMS ?= linux/amd64,linux/arm64
REVISION := $(shell git rev-parse --short HEAD 2>/dev/null || echo dev)

.PHONY: help build run push multiarch up down logs test-frontend clean

help:
	@echo "make build        本地构建单架构镜像 $(IMAGE):$(VERSION)"
	@echo "make run          本地起容器（23000 端口，./data 等目录挂载）"
	@echo "make multiarch    buildx 多架构构建并推送（需先 docker login $(REGISTRY)）"
	@echo "make up/down      用 docker-compose.yml 启停"
	@echo "make test-frontend 前端依赖安装 + 生产构建验证"

build:
	docker build --build-arg VERSION=$(VERSION) --build-arg REVISION=$(REVISION) \
		-t $(IMAGE):$(VERSION) -t $(IMAGE):latest .

run:
	docker run -d --name flatnas -p 23000:3000 \
		-v $(PWD)/data:/app/server/data \
		-v $(PWD)/music:/app/server/music \
		-v $(PWD)/PC:/app/server/PC \
		-v $(PWD)/APP:/app/server/APP \
		-v $(PWD)/doc:/app/server/doc \
		$(IMAGE):$(VERSION)

multiarch:
	docker buildx build --platform $(PLATFORMS) \
		--build-arg VERSION=$(VERSION) --build-arg REVISION=$(REVISION) \
		-t $(IMAGE):$(VERSION) -t $(IMAGE):latest --push .

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

test-frontend:
	cd frontend && npm ci && npm run build-only

clean:
	rm -rf frontend/dist frontend/node_modules
