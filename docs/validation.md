# Validation Matrix

所有本地和 CI 检查都通过 `scripts/repo-harness` 暴露，避免 README、IDE task 和 CI 各自
维护不同命令。

## Commands

| 命令 | 内容 | 典型耗时/前提 |
| --- | --- | --- |
| `validate quick` | harness 结构、局部链接、Action pin、OpenSpec strict | 快；Python、Node/OpenSpec |
| `validate changed` | quick + 按当前改动选择模块验证 | 取决于改动 |
| `validate firmware-host` | CMake/CTest motion host tests | 快；CMake/C++ |
| `validate firmware` | ESP-IDF 主固件完整构建 | 慢；ESP-IDF 5.5.4、已获取依赖 |
| `validate app` | `flutter analyze`，存在测试时运行 `flutter test` | Flutter SDK、已获取包 |
| `validate server` | `go test ./...` + `go build ./...` | Go 1.26.3、可用 module cache |
| `validate remote` | 遥控器 ESP-IDF 构建 | ESP-IDF 5.4.2、对应依赖 |
| `validate openspec` | `openspec validate --all --strict` | OpenSpec CLI |
| `validate all` | 所有上述作用域 | 完整工具链和较长时间 |

`doctor` 只报告工具可用性，不替代验证。

## Change To Check Mapping

| 改动 | 最小检查 | 交付前附加检查 |
| --- | --- | --- |
| 根规则、docs、harness、CI | `quick` | 在 CI 配置变更时核对实际 workflow run |
| OpenSpec | `openspec` | artifact 一致性与 task/实现核对 |
| 固件纯 motion 逻辑 | `firmware-host` + `firmware` | 受影响动作真机验证 |
| 固件网络/硬件/NVS/OTA | `firmware` | CoreS3 真机矩阵、资源和恢复测试 |
| Flutter Dart | `app` | 受影响平台 build/模拟器/真机 |
| Server Go | `server` | 数据库、WebSocket 或外部服务集成测试 |
| 遥控器 | `remote` | 遥控器与 StackChan 配对真机验证 |
| 跨模块协议 | 所有相关模块 | 端到端兼容性测试 |

## CI Coverage

`.github/workflows/repo-harness.yml` 默认执行：

- 仓库结构、文档链接和 OpenSpec strict validation
- firmware host tests
- server tests and build

Flutter、完整主固件、遥控器和硬件验收需要专用 SDK/设备，当前保留为本地或后续
self-hosted runner 检查。新增 CI 能力时必须复用 harness 子命令并更新本页。

## Security Validation

仓库已有历史内容会使宽泛正则扫描产生较多误报。引入 Gitleaks 等工具时应先审查现有
finding、建立可解释 baseline，再把“只阻止新增泄露”设为门禁；不要用大范围 allowlist
隐藏真实凭据。任何疑似真实凭据都应先轮换，再处理历史记录。
