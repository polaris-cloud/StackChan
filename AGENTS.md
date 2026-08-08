# StackChan Agent Guide

本文件只提供仓库级路由和共同约束。处理某个目录时，还必须读取离目标文件最近的
`AGENTS.md`；局部规则在其作用域内优先。不要为了获取上下文而一次性扫描整个仓库。

## First Steps

1. 运行 `git status --short --branch`，确认分支、工作树和已有改动。
2. 根据任务确定唯一主作用域，并读取对应的局部 `AGENTS.md`。
3. 从 [知识源路由](docs/knowledge-sources.md) 找到事实源；不要把 README、聊天记录或
   OpenSpec 中尚未实现的设计当成当前行为。
4. 修改前确认最小验证集合，修改后运行
   `./scripts/repo-harness validate changed` 或更严格的作用域验证。

## Repository Router

| 作用域 | 内容 | 局部说明 |
| --- | --- | --- |
| `firmware/` | CoreS3/ESP32-S3 主固件，ESP-IDF 5.5.4 | `firmware/AGENTS.md` |
| `app/` | Flutter 移动端 | `app/AGENTS.md` |
| `server/` | GoFrame/MySQL 后端 | `server/AGENTS.md` |
| `remote/code/` | ESP-NOW 遥控器固件，ESP-IDF 5.4.2 | `remote/code/AGENTS.md` |
| `openspec/` | 需求、设计和实施任务，不等于已实现事实 | `openspec/AGENTS.md` |
| `.github/` | CI 和仓库自动化 | `.github/AGENTS.md` |

更完整的开发入口见 [开发知识索引](docs/README.md)。

## Shared Boundaries

- 保持改动位于其所有权模块内；跨模块行为先明确接口和验证范围。
- 不提交密钥、令牌、Wi-Fi 凭据、私钥、生产地址或可复用的 Tailscale auth key。
- 不覆盖用户已有改动，不清理与当前任务无关的 dirty 文件。
- 不提交构建产物、下载的第三方源码或本机 IDE/工具链状态。
- 依赖升级必须固定版本或 commit，并记录来源、许可证和兼容性验证。
- 未经明确请求，不刷写设备、不擦除 NVS、不修改数据库数据、不执行部署。
- 生成文件只通过其生成器更新；先阅读局部 `AGENTS.md` 确认来源。

## Change Workflow

- 文档、注释和局部低风险修复可以直接修改，并运行相应快速验证。
- 新能力、跨模块行为、协议/路由/安全边界变化先在 `openspec/changes/` 建立或更新
  OpenSpec，再实施和归档。
- OpenSpec 描述目标状态；代码、配置和测试描述当前仓库状态。两者不一致时必须明确
  标注“尚未实现”，不能静默选择其中一个。
- 完整流程和完成定义见 [开发工作流](docs/workflows.md)。

## Validation

统一入口：

```bash
./scripts/repo-harness doctor
./scripts/repo-harness validate quick
./scripts/repo-harness validate changed
```

`changed` 会按当前改动选择模块检查；交付前仍需依据风险补充真机、集成或发布验证。
所有命令和 CI 覆盖范围见 [验证矩阵](docs/validation.md)。
