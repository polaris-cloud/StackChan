# Development Workflow

## 1. Orient

1. 检查分支和 dirty 状态。
2. 选择主模块并读取最近的 `AGENTS.md`。
3. 从知识源地图找到当前事实和目标事实。
4. 运行 `./scripts/repo-harness doctor` 确认本任务所需工具可用。

## 2. Choose A Change Path

局部修复、文档或纯重构：

- 直接在最小所有权边界内修改。
- 保持接口兼容，补充与风险匹配的测试。

新能力、跨模块契约、协议、安全或持久化变化：

- 在 `openspec/changes/` 新建或更新唯一 change。
- 先确认 proposal/spec/design/tasks 一致并通过 strict validation。
- 按 tasks 实施；每一项只在实现和验证都完成后勾选。

依赖更新：

- 固定版本或完整 commit。
- 核验来源、许可证、变更内容和供应链风险。
- 更新 lock/patch/provenance，并验证离线或失败行为。

硬件和部署：

- 先确认目标设备/环境、配置、凭据边界、可观测性和回滚路径。
- 构建、刷写、真机验收分开记录；构建成功不代表设备行为正确。

## 3. Implement

- 只修改当前任务需要的模块和契约。
- 先更新测试或验收 probe，再实现高风险行为。
- 生成文件通过正式生成器更新，并单独审查生成 diff。
- 遇到不相关改动时保护现场，不重置、不覆盖、不顺手清理。

## 4. Validate

先运行：

```bash
./scripts/repo-harness validate changed
```

再根据 [验证矩阵](validation.md) 补齐全量构建、集成、真机或平台验证。失败必须修正或在
交付说明中明确记录，不能通过跳过检查获得“通过”。

## 5. Handoff

交付说明至少包含：

- 结论和行为变化
- 修改的所有权模块
- 实际运行的验证及结果
- 未运行检查、硬件/环境缺口和剩余风险
- 对应 OpenSpec change 与 task 状态（如适用）
