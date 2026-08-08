## Why

StackChan 目前只能经普通 Wi-Fi 使用公网服务，不能作为独立 Tailnet 节点安全访问仅监听于 Mac Tailnet 地址的 Codex 网关。现在需要在不替换官方 Wi-Fi/XiaoZhi 网络栈的前提下，引入 MicroLink，使 CoreS3 在家庭 Wi-Fi或 iPhone 热点下均可独立注册、恢复连接并访问该网关。

## What Changes

- 为 ESP32-S3 固件增加独立的 MicroLink Tailnet 节点生命周期：在 Wi-Fi 获得 IP 且系统时间可用后启动，在断网时停用，在重新联网或底层地址变化后重绑。
- 增加选择性 Tailnet 路由：仅将 Tailnet IPv4 `100.64.0.0/10` 交给 MicroLink，普通公网、Tailscale 控制面、DERP、STUN 和 WireGuard 外层 UDP 继续经官方 Wi-Fi。
- 为节点注册、凭据持久化、状态日志和错误恢复定义安全边界；源码与构建产物不得包含可复用认证密钥。
- 以固定提交引入 MicroLink，并在集成前核验仓库来源、许可证、ESP-IDF API 兼容性以及 PR #21 所代表的端点验证行为。
- 增加主机侧构建检查和 CoreS3 真机验收，覆盖家庭 Wi-Fi、iPhone 热点/CGNAT、DERP 中继、直连升级、重连和官方网络功能回归。

本变更不替换 `WifiBoard` 或 `Board::GetNetwork()`，不实现 Codex 网关本身，也不在首期支持 IPv6、exit node、subnet router、Funnel、蜂窝网络、MicroLink Web 配置页或 zero-copy。

## Capabilities

### New Capabilities

- `embedded-tailnet-node`: 定义 StackChan 独立 Tailnet 节点的启动条件、身份注册、凭据保护、连接状态、重连和资源约束。
- `tailnet-selective-routing`: 定义 Tailnet IPv4 的选择性路由、物理 Wi-Fi underlay 绑定、Codex 网关连通性及路由失败时的隔离行为。

### Modified Capabilities

无。仓库当前没有已有 OpenSpec capability。

## Impact

- **固件代码**：预计影响 `firmware/main/hal/hal_network.cpp`、HAL 网络接口及新增的 StackChan 自有 MicroLink 适配模块；不改变 remote、app 或 server。
- **构建与依赖**：预计影响 `firmware/repos.json`、`firmware/main/CMakeLists.txt`、ESP-IDF 配置和补丁目录；MicroLink 必须固定到已审查的精确提交。
- **运行时**：新增 Tailnet 控制面、DERP/DISCO/WireGuard 任务、PSRAM/SRAM 缓冲和 NVS 身份数据；需要定义资源水位与降级策略。
- **安全与运维**：Mac Codex 网关继续只监听 Tailnet 地址，并由 Tailnet ACL 限制 StackChan 身份；设备侧不得开放公网监听端口。
- **兼容性**：无计划中的公共 API 或存储格式破坏；对官方 Wi-Fi、XiaoZhi、OTA、App Center 和普通公网访问进行回归验证。
- **待真机验证假设**：CoreS3 的可用内存、iPhone 热点下的 DERP/直连行为、Wi-Fi 切换与 Mac 睡眠恢复仍需硬件数据确认。
