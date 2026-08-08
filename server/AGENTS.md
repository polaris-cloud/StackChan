# Server Agent Guide

本文件适用于 `server/`。同时继承仓库根 `AGENTS.md`。

## Read First

- 依赖和 Go 版本事实源：`go.mod`、`go.sum`
- 运行与接口说明：`README.MD`
- 启动入口：`main.go`、`internal/cmd/`
- 配置：`manifest/config/config.yaml`
- 数据库定义：`check_list/create_mysql_database.sql`

## Structure And Conventions

- `api/` 定义请求/响应契约，`internal/controller/` 接入路由，
  `internal/logic/` 承载业务逻辑，`internal/service/` 提供服务边界。
- Go 代码必须通过 `gofmt`；保持现有 GoFrame 分层，不在 controller 中复制业务逻辑。
- `internal/dao/` 和 `internal/model/{do,entity}/` 可能由 GoFrame 工具生成。只有数据库
  变更明确要求时才运行 `make dao`，并审查生成 diff。
- 文档和默认配置只使用占位符。不得提交真实数据库密码、JWT secret、管理账号、
  第三方 token 或生产主机。
- 数据库迁移、数据修复、部署和外部服务调用都需要明确环境与授权；普通代码任务默认
  只做本地编译和测试。

## Validation

```bash
../scripts/repo-harness validate server
```

该入口运行 `go test ./...` 和 `go build ./...`。涉及数据库、WebSocket 或外部服务时，
还应增加针对相应边界的集成验证。
