# OpenSpec Agent Guide

本文件适用于 `openspec/`。同时继承仓库根 `AGENTS.md`。

## Meaning

- `changes/` 描述提议或实施中的目标状态，不证明该能力已经存在。
- 归档后的规范表示已接受的需求基线，但当前行为仍需由代码、配置和测试核验。
- 一个行为变化只保留一个 OpenSpec change 作为规划事实源，避免平行任务重复定义。

## Authoring

- 遵循 `config.yaml` 中的仓库上下文和 artifact 规则。
- 文档使用中文，协议名、代码符号和规范关键词保留英文。
- proposal 说明目标、非目标、影响面和兼容性。
- spec 使用 MUST/SHOULD/MAY 与 Given/When/Then 场景，验收标准必须可测试。
- design 明确边界、所有权、失败模式、安全、回滚和未决问题。
- tasks 区分 host、构建和真机验证，并按依赖顺序排列。
- 把已核验事实、推断和待真机验证内容明确分开；不得把猜测写成仓库事实。

## Validation

```bash
../scripts/repo-harness validate openspec
```

实现完成前核对 task 勾选与真实验证记录；归档前再次运行 strict validation。
