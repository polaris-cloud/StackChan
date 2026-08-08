# Firmware Agent Guide

本文件适用于 `firmware/`。同时继承仓库根 `AGENTS.md`。

## Read First

- 构建和依赖入口：`README.md`、`CMakeLists.txt`、`repos.json`、
  `dependencies.lock`
- 固件配置事实源：`sdkconfig.defaults` 和 `main/Kconfig.projbuild`
- 源码注册边界：`main/CMakeLists.txt`
- 变更需求：目标任务对应的 `../openspec/changes/<change>/`

`sdkconfig`、`build/`、`components/`、`managed_components/` 和
`xiaozhi-esp32/` 是生成或拉取内容，不是直接维护的事实源。

## Structure

- `main/hal/`：硬件、板级和网络集成边界
- `main/stackchan/`：机器人动作、表情和领域逻辑
- `main/apps/`：设备应用和 UI 功能
- `tests/`：可脱离 ESP-IDF 运行的 host tests
- `patches/`：对固定第三方版本的可追溯补丁
- `fetch_repos.py` / `repos.json`：外部源码获取与版本身份

## Conventions

- 目标为 `esp32s3`，主工具链为 ESP-IDF v5.5.4。
- C/C++ 格式遵循 `.clang-format`：Google 派生、4 空格、120 列、禁止 tab。
- 配置默认值写入 `sdkconfig.defaults`；本机覆盖使用被忽略的
  `sdkconfig.defaults.local`。
- 保持官方 Wi-Fi、OTA、XiaoZhi 和 App Center 的所有权边界。网络改造必须先读取
  对应 OpenSpec，且不得凭设计文档推断代码已经实现。
- ESP-IDF event callback 中只做有界、非阻塞工作；长生命周期操作放入拥有明确所有权
  的 task/service。
- 检查所有 allocation、task 和网络资源创建结果；失败应可降级，不应让非核心功能
  触发整机 abort。
- 不记录认证材料、私钥、完整控制面响应或可复用凭据。

## Validation

```bash
../scripts/repo-harness validate firmware-host
../scripts/repo-harness validate firmware
```

涉及硬件、Wi-Fi、BLE、音频、舵机、NVS、OTA 或网络恢复时，构建通过不等于验收通过。
必须记录板型、串口、配置、场景和真机结果；未经明确请求不得刷写设备。
