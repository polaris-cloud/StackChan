# Remote Firmware Agent Guide

本文件适用于 `remote/code/`。同时继承仓库根 `AGENTS.md`。

## Read First

- 构建前提和硬件说明：`README.md`
- 依赖锁定：`dependencies.lock`、`main/idf_component.yml`
- 源码清单：`main/CMakeLists.txt`
- 项目配置：`sdkconfig`

## Boundaries

- 这是独立的 ESP-IDF 工程，目标为 `esp32`，工具链为 ESP-IDF v5.4.2；不要套用主固件
  的 v5.5.4/esp32s3 配置。
- `main/esp_now/`、`main/joystick/` 和 `main/ui/` 保持各自职责。
- 仓库当前跟踪了 `sdkconfig` 和预编译固件。除非任务明确要求发布或配置变更，不要
  顺手重生成或覆盖它们。
- 修改 ESP-NOW 协议或配对信息时，必须检查与主固件
  `firmware/main/apps/app_espnow_ctrl/` 的兼容性。
- 未经明确请求不得刷写遥控器或替换仓库中的二进制产物。

## Validation

```bash
../../scripts/repo-harness validate remote
```

构建通过后，涉及摇杆、UI、ESP-NOW 或 IMU 的变更仍需在对应硬件上验证。
