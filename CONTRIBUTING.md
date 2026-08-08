# Contributing To StackChan

这是一个包含两套 ESP-IDF 固件、Flutter App 和 Go 后端的 monorepo。开始前先运行：

```bash
./scripts/repo-harness doctor
```

开发知识入口在 [docs/README.md](docs/README.md)，编码 Agent 规则从
[AGENTS.md](AGENTS.md) 开始，并按目标目录继续读取局部 `AGENTS.md`。

## Development Loop

1. 检查 `git status --short --branch`，确认没有覆盖现有改动。
2. 选择一个主模块，读取该模块 README、manifest 和局部 `AGENTS.md`。
3. 行为变化先更新对应 OpenSpec；局部修复直接保持最小范围。
4. 实现并增加与风险匹配的测试。
5. 运行 `./scripts/repo-harness validate changed`，再补充必要的全量或真机验证。
6. 提交说明写清验证结果、未验证项和剩余风险。

## Repository Hygiene

- 不提交 build output、下载的 firmware components、IDE 本机状态或私有配置。
- 不提交密码、私钥、签名材料、生产地址、token 或 Tailscale auth key。
- 不直接编辑生成代码或 lock file；通过对应工具更新并审查完整 diff。
- 不在无关任务中更新依赖、格式化整个模块或重写历史。
- 硬件刷写、NVS 擦除、数据库变更和部署需要明确目标与授权。

统一命令和完成标准见 [docs/validation.md](docs/validation.md) 与
[docs/workflows.md](docs/workflows.md)。
