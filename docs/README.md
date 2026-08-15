# StackChan Developer Knowledge

这里是人和编码 Agent 共用的开发知识入口。它负责导航，不复制模块 README 或源码中的
细节。

## Route By Question

| 你要回答的问题 | 首先读取 | 然后读取 |
| --- | --- | --- |
| 仓库有哪些产品、由谁负责 | 根 `AGENTS.md` | 目标模块的 `AGENTS.md` |
| 某个事实到底以什么为准 | [知识源路由](knowledge-sources.md) | 对应 manifest、配置、代码和测试 |
| 新功能或行为变化怎么推进 | [开发工作流](workflows.md) | `openspec/config.yaml` 和目标 change |
| 修改后该跑哪些检查 | [验证矩阵](validation.md) | 目标模块的 `AGENTS.md` |
| 产品如何安装或使用 | 根/模块 README | 官方产品和平台文档 |

## Module Map

| 模块 | 主要入口 | 关键事实源 |
| --- | --- | --- |
| 主固件 | `firmware/main/main.cpp` | `firmware/sdkconfig.defaults`、`firmware/repos.json` |
| 移动端 | `app/lib/main.dart` | `app/pubspec.yaml`、`app/analysis_options.yaml` |
| 后端 | `server/main.go` | `server/go.mod`、`server/manifest/config/config.yaml` |
| 遥控器 | `remote/code/main/StackChan-RemoteControl-ESPNow.cpp` | `remote/code/dependencies.lock`、`remote/code/sdkconfig` |
| 变更规格 | `openspec/changes/` | `openspec/config.yaml`、目标 change artifacts |

## Keep This Layer Healthy

- 只记录稳定的路由、边界和决策，不把源码细节复制到这里。
- 新增模块时，同时增加局部 `AGENTS.md`、知识源条目和验证入口。
- 文档与实现冲突时，先修正事实源，再更新导航。
- Agent 本地 memory、聊天摘要和 IDE 索引可以提高效率，但不得成为仓库唯一知识源。
