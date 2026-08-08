# App Agent Guide

本文件适用于 `app/`。同时继承仓库根 `AGENTS.md`。

## Read First

- 依赖和 Dart 版本事实源：`pubspec.yaml`
- 静态分析规则：`analysis_options.yaml`
- 应用入口与全局状态：`lib/main.dart`、`lib/app_state.dart`
- 网络边界：`lib/network/`
- 平台权限和发布配置：`android/`、`ios/`

README 中的版本描述可能滞后；冲突时以 manifest、平台配置和实际工具输出为准。

## Conventions

- 遵循 `flutter_lints`，不要通过全局关闭规则来隐藏新告警。
- UI、网络、设备状态和数据模型保持现有目录边界；不要把凭据或服务器环境差异写死在
  widget 中。
- 后端地址、公钥和非敏感开发默认值应与生产凭据分离。不得提交私钥、签名密码、
  keystore 或真实 token。
- `build/`、`.dart_tool/`、Pods 和平台生成文件不作为手工维护目标。
- 修改 BLE、摄像头、麦克风、定位或局域网能力时，同时检查 Android/iOS 权限声明和
  失败状态。

## Validation

```bash
../scripts/repo-harness validate app
```

验证至少包含 `flutter analyze`；存在 `test/` 时还会运行 `flutter test`。涉及原生平台、
权限或发布配置时，再构建受影响的平台并在真机或模拟器验证。
