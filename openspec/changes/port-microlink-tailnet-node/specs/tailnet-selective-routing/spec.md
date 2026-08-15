## ADDED Requirements

### Requirement: Tailnet 路由不得替换 Wi-Fi 默认路由
系统 MUST 保持 STA Wi-Fi 为 lwIP 默认 underlay，不得启用 exit node 或把 `0.0.0.0/0` 指向 WireGuard netif。只有 Tailnet IPv4 `100.64.0.0/10` 中、且由已知 peer `/32` AllowedIP 匹配的流量才可进入 MicroLink WireGuard netif。

#### Scenario: 同时访问公网与 Tailnet
- **GIVEN** StackChan 已连接 Tailnet
- **WHEN** 固件同时访问公网 API 和 `100.64.0.0/10` 内的 Mac 地址
- **THEN** 公网连接经 STA Wi-Fi 默认路由发送，Mac 连接经 WireGuard netif 发送

#### Scenario: 未知 Tailnet 目的地址
- **GIVEN** 目的地址属于 `100.64.0.0/10`，但没有匹配的已授权 peer
- **WHEN** 应用尝试发送数据
- **THEN** 发送失败且不会把明文数据回退到 STA 默认路由

### Requirement: Overlay 外层流量必须固定在 underlay
系统 MUST 将 WireGuard 外层 UDP 显式 pin 到当前 STA lwIP netif，并 MUST 保证控制面、DERP、STUN、DNS 和 TLS socket 使用物理 Wi-Fi 路径。重连后 MUST 更新 pin 所指向的有效 STA netif，防止 overlay 递归。

#### Scenario: Tailnet 路由已经生效
- **GIVEN** WireGuard netif 已加入 lwIP 路由表
- **WHEN** MicroLink 向 DERP、STUN 或 peer 公网 endpoint 发送外层包
- **THEN** 包从 STA netif 发出，不再次进入 WireGuard netif

#### Scenario: STA 地址变化
- **GIVEN** 设备从家庭 Wi-Fi 切换到 iPhone 热点
- **WHEN** 新 STA IPv4 地址生效并触发 Tailnet 恢复
- **THEN** 外层 socket 与 WireGuard output 重新绑定新 underlay，旧地址不再被使用

### Requirement: Tunnel 内必须支持双向 TCP 和 UDP
MicroLink MUST 把解密后的 inner IPv4 包通过 `tcpip_input` 交给 lwIP，并 MUST 允许应用使用绑定 Tailnet 源地址的 TCP/UDP API 与 peer 通信。TCP 重传、排序、连接状态与 WebSocket 承载由 inner TCP/lwIP 处理，外层路径可为 direct UDP 或 DERP。

#### Scenario: 连接 Mac Codex 网关
- **GIVEN** Mac Codex 网关只监听其 Tailnet IPv4 和指定 TCP 端口
- **WHEN** StackChan 通过 MicroLink TCP API 建立 HTTP 或 WebSocket 连接
- **THEN** TCP 三次握手与双向应用数据在 WireGuard 隧道内完成，网关无需暴露公网端口

#### Scenario: Tunnel 内 UDP
- **GIVEN** 目标 peer 已在 WireGuard peer 表中
- **WHEN** StackChan 通过 MicroLink UDP API 发送数据报
- **THEN** inner UDP 数据报被 WireGuard 加密，并经当前可用的 DERP 或 direct underlay 路径发送

### Requirement: DERP 与 direct 路径切换不得改变应用语义
当 NAT、CGNAT 或热点隔离阻止 direct UDP 时，系统 MUST 保持 DERP 双向传输；当 DISCO 验证出 direct 路径时 MAY 无感升级。路径切换 MUST 不改变应用使用的 Tailnet IP 和目标端口。

#### Scenario: iPhone 热点经 DERP
- **GIVEN** iPhone 热点的 NAT 条件无法建立 peer-to-peer UDP
- **WHEN** StackChan 访问 Mac Codex 网关
- **THEN** 连接通过 Tailnet DERP 中继保持双向可用，应用仍连接同一 Tailnet IP 和端口

#### Scenario: 从 DERP 升级为 direct
- **GIVEN** 现有应用连接使用 DERP 且随后出现通过 DISCO 验证的直连路径
- **WHEN** MicroLink 更新 peer endpoint
- **THEN** 后续加密包可使用 direct UDP，不要求应用改写目标地址或切换公网路由

### Requirement: Overlay 故障必须与官方公网功能隔离
Tailnet 的注册、DERP、WireGuard、路由或 peer 故障 MUST 只使 Tailnet 能力进入 degraded/error 状态，不得删除 STA 默认路由、停止官方 Wi-Fi 重连、阻塞 SNTP、XiaoZhi、OTA、App Center 或普通公网 API。

#### Scenario: Tailscale 控制面不可达
- **GIVEN** Wi-Fi 公网可用但 Tailscale 控制面被阻断
- **WHEN** Tailnet 服务连接超时并进入退避
- **THEN** 公网 DNS、HTTPS、XiaoZhi 和 OTA 的路由与连接仍保持可用

#### Scenario: 停用 Tailnet 功能
- **GIVEN** 固件通过构建或运行配置关闭 Tailnet
- **WHEN** 系统启动
- **THEN** 不创建 MicroLink 任务或 WireGuard netif，网络行为与移植前官方固件一致

### Requirement: Codex 网关访问必须遵守最小暴露面
StackChan MUST 仅主动连接配置的 Mac Tailnet 地址与 Codex 网关端口，首期固件 MUST 不开启 MicroLink HTTP 配置服务器或其他公网监听服务。验收环境 MUST 由 Tailnet ACL 仅授权该 StackChan 节点访问所需网关端口。

#### Scenario: 从 Tailnet 访问网关
- **GIVEN** Mac 网关只监听 Tailnet 地址，ACL 允许 StackChan 节点访问指定端口
- **WHEN** StackChan 发起连接
- **THEN** 连接成功，Mac 的 LAN 地址和公网地址均无需监听该服务

#### Scenario: 非授权端口
- **GIVEN** ACL 未授权 StackChan 访问 Mac 的其他端口
- **WHEN** StackChan 尝试连接非授权端口
- **THEN** Tailnet 策略拒绝连接，设备不尝试绕过到 Mac 的公网或 LAN 地址
