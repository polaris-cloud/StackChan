# GitHub Automation Agent Guide

本文件适用于 `.github/`。同时继承仓库根 `AGENTS.md`。

- 工作流调用仓库内 `scripts/repo-harness`，不要在 YAML 中维护另一套验证命令。
- `permissions` 使用最小权限；默认只需要 `contents: read`。
- 第三方 Action 固定到完整 commit SHA，并在行尾注释对应 release。
- 不在 `pull_request_target` 上执行不受信任的 PR 代码。
- 不把 secrets 传给 fork PR，不输出环境变量或凭据。
- 新增 CI 检查时同步更新 `docs/validation.md`，明确本地与 CI 的覆盖差异。
