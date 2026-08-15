# Knowledge Source Routing

目标是让同一个问题只有一个可识别的事实源，并让 Agent 按需读取最小上下文。

## Precedence

发生冲突时，按问题类型选择来源，而不是机械地相信某一类文档：

1. 当前行为：可执行代码、运行时配置和实际测试结果。
2. 构建与依赖：manifest、lock file、CMake 和工具链输出。
3. 预期行为：已接受的规范、测试和对应 OpenSpec artifact。
4. 工作方式：根与局部 `AGENTS.md`、本目录开发文档。
5. 说明性材料：README、注释、外部文章和历史记录。
6. 临时上下文：Agent memory、聊天摘要、搜索结果和未验证推断。

OpenSpec 中“应该存在”的能力不能覆盖代码中“尚未存在”的事实；README 中的版本号也
不能覆盖 manifest。

## Repository Sources

| 问题 | 事实源 | 不应作为唯一依据 |
| --- | --- | --- |
| 主固件工具链与目标 | `firmware/README.md`、`sdkconfig.defaults`、构建输出 | 本机 `sdkconfig` |
| 固件第三方源码版本 | `firmware/repos.json`、`dependencies.lock`、`patches/` | 已下载的 `components/` |
| 固件源码是否参与构建 | `firmware/main/CMakeLists.txt` | 仅凭文件存在 |
| Flutter/Dart 版本与包 | `app/pubspec.yaml`；若提交 `pubspec.lock`，以 lock 的解析结果为准 | README 徽章或旧说明 |
| App 静态规则 | `app/analysis_options.yaml` | IDE 个人设置 |
| Server Go 版本与依赖 | `server/go.mod`、`go.sum` | 本机 Go 版本 |
| Server API 当前行为 | route/controller/logic 代码与测试 | README API 摘要 |
| 遥控器工具链与配置 | `remote/code/README.md`、`sdkconfig`、`dependencies.lock` | 主固件配置 |
| 变更目标和验收标准 | `openspec/changes/<change>/` | 聊天记录 |
| 当前是否已实现变更 | 代码、配置、测试和 task 验证记录 | proposal/design 单独存在 |

## External Sources

- M5Stack 产品和 BSP：优先官方 StackChan 文档、StackChan-BSP 仓库和官方发布信息。
- ESP-IDF：使用与模块固定版本匹配的 Espressif 官方文档；主固件为 5.5.4，遥控器为
  5.4.2。
- Flutter/Dart、Go/GoFrame：优先官方版本化文档和项目 manifest。
- 第三方网络库：固定 commit 后同时保存仓库 URL、许可证、patch 来源和兼容性验证。
- Tailscale 协议行为：优先 Tailscale 官方文档/源码；非官方 ESP32 实现只证明自身
  行为，不代表官方兼容承诺。

查阅网络资料时记录访问日期。会变化的版本、API、安全建议和 release 状态必须重新
核验，不能依赖旧会话记忆。

## Harness Building Blocks

选型核验日期：2026-07-28。

| 开源项目 | 在本仓库中的角色 | 决策 |
| --- | --- | --- |
| [AGENTS.md](https://github.com/agentsmd/agents.md) | 分层 Agent 指令约定 | 已采用根路由 + 模块局部文件 |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | 行为变化的规格与任务闭环 | 已采用，并固定 CI CLI 版本 |
| [Serena](https://github.com/oraios/serena) | 本机语义检索、重构和临时 memory | 可选工具；memory 不是仓库事实源 |
| [Microsoft Skills / Deep Wiki](https://github.com/microsoft/skills) | AGENTS/wiki 生成模式参考 | 参考其局部发现和不覆盖原则，不引入生成站点 |
| [GitHub Spec Kit](https://github.com/github/spec-kit) | 完整 SDD 的另一种实现 | 不与 OpenSpec 并用，避免双重规格源 |
| [pre-commit](https://github.com/pre-commit/pre-commit) | 多语言提交前 hook 管理 | 后续按团队需要接入，不作为基础依赖 |
| [Gitleaks](https://github.com/gitleaks/gitleaks) | 新增凭据泄露门禁 | 建立审查过的 baseline 后再启用 |
| [Lychee](https://github.com/lycheeverse/lychee) | 外部链接检查 | 当前只检查本地链接；可在联网 CI 中增量接入 |

根命令入口使用仓库自带 shell/Python 和 Make，当前不要求额外安装 `just` 或 Taskfile。
若任务数量继续增长，可评估 [just](https://github.com/casey/just)，但它不应复制
`scripts/repo-harness` 的业务逻辑。
