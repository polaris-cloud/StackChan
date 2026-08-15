## Context

官方固件的网络入口是 `Hal::startNetwork()`。它通过 XiaoZhi `Board::GetInstance().StartNetwork()` 启动 Wi-Fi，等待首次 `NetworkEvent::Connected`，随后移除该单一 Board 回调并异步启动 SNTP。现有 `WifiManager`、HTTP/WebSocket、OTA 和 App Center 都依赖这条官方网络路径，因此 MicroLink 不能替换 `WifiBoard`、修改默认网络所有权或长期占用 Board 回调。

MicroLink 提供 Tailscale 控制面、DERP、STUN/DISCO、WireGuard-lwIP netif 以及绑定 VPN 源地址的 TCP/UDP API。其 WireGuard netif 使用 `100.64.0.0/10`，peer 以 `/32` AllowedIP 加入，解密后的 inner packet 通过 `tcpip_input` 进入 lwIP。它是非官方 Tailscale 实现，需要按不受信任的第三方网络依赖管理。

截至 2026-08-08 复核时已核验：

- `CamM2325/microlink` `main` 为 `216da3300f0493b0860247d43f7af5ce29df63a5`，仓库包含 MIT `LICENSE`。
- `Csontikka/microlink` `main` 为 `87b868429a3cc7afb6160f8c52657907e7d71833`，相对 CamM `main` ahead 43、behind 0，同样保留 MIT `LICENSE`。相对先前基线 `aad403af0df6c08500c4236cb09c9ebc5bc00416` 新增 4 个提交，覆盖 control stream liveness、DERP liveness、authoritative peer sweep、跨读取的 HTTP/2 frame 重组和按原因统计的重连诊断。
- CamM PR #21 的 head 为 `da55beb7e8c13be2deaeacdc166c54d135d86235`；该修复仍未包含在上述 Csontikka commit 中，当前 `add_peer()` 仍会把 MapResponse 的首个 endpoint 预装进 WireGuard peer。该修复阻止未验证 endpoint 被当作直连路径。
- Csontikka commit 的 `microlink_pin_wg_output_netif()` 可将 WireGuard output、coord 和 DERP 自发 socket 绑定 STA underlay。`CONFIG_ML_ENABLE_CONFIG_HTTPD` 已由上游提供且默认关闭，关闭时不会初始化或启动 HTTP server；但组件 CMake 仍无条件编译 `ml_config_httpd.c` 并依赖 `esp_http_server`，需要本地最小补丁裁掉未使用的源码和依赖。

首期硬件是带 PSRAM 的 M5Stack CoreS3，underlay 是 2.4 GHz 家庭 Wi-Fi 或 iPhone 热点，目标是只通过 Mac 的 Tailnet IPv4 和受 ACL 限制的 TCP 端口访问 Codex 网关。

## Goals / Non-Goals

**Goals:**

- 让 StackChan 成为拥有持久身份的独立 Tailnet 节点。
- 在官方 Wi-Fi 和可用系统时间就绪后异步启动，在断网、换网和地址变化后有界恢复。
- 只将 Tailnet IPv4 peer 流量交给 WireGuard，所有普通公网和 overlay 外层流量继续使用 STA。
- 在 direct UDP 不可用时保持 DERP 双向可用，并仅在 DISCO 验证后升级直连。
- 以可复现依赖、最小功能集、脱敏诊断和真机资源水位控制移植风险。
- 关闭功能时恢复到与官方固件等价的网络行为。

**Non-Goals:**

- 不实现或公开 Codex 网关，也不改变 Mac 侧 Codex 服务协议。
- 不替换 XiaoZhi `WifiBoard`、Wi-Fi 配网、DHCP、DNS、SNTP 或官方重连机制。
- 不支持 IPv6 Tailnet、exit node、subnet router、accept-routes、Funnel 或公网入站。
- 不支持 cellular、MicroLink net switch、zero-copy、高吞吐视频或 MicroLink Web 配置页。
- 不在首期制作面向普通用户的 Tailnet 设置 UI；仅提供受控的本地开发/设备 provisioning。
- 不承诺兼容任意规模 Tailnet；64 KB 控制面缓冲所支持的规模必须通过目标 Tailnet 实测。

## Decisions

### 1. 以 Csontikka 固定提交加仓库补丁作为移植基线

在 `firmware/repos.json` 增加 `Csontikka/microlink`，路径为 `components/microlink`，ref 固定为 2026-08-08 复核时的最新完整 commit `87b868429a3cc7afb6160f8c52657907e7d71833`。这里的“最新”只用于选择本次受审基线，构建仍不得跟随浮动 `main`。`firmware/patches/microlink.patch` 至少包含：

1. PR #21 等价的 DERP-first endpoint 验证修复。
2. 复用上游默认关闭的 `CONFIG_ML_ENABLE_CONFIG_HTTPD` 运行门控，并在关闭时从 CMake 源码和依赖中移除 HTTP server，使固件不链接 `esp_http_server`。
3. ESP-IDF 5.5.4/CoreS3 编译所需且经过审查的最小兼容补丁。

`fetch_repos.py` 增加“必要补丁”语义：MicroLink commit 不匹配或 patch check 失败时立即非零退出。补丁文件记录上游 URL、基线 SHA 和对应 PR，便于以后判断可否删除本地补丁。

选择 Csontikka 而不是 CamM 当前 main，是因为本项目需要其较新的 rebind、netcheck、Headscale 兼容修复和 underlay pin API。没有直接采用 `0xdilo/tailscale-esp32`，因为本阶段需要可供 lwIP TCP/UDP 使用的完整 inner-IP 路径和 DERP/DISCO 恢复能力。只移植裸 WireGuard 也不能完成节点注册、netmap、DERP 和 NAT 穿透。

### 2. 新增 StackChan 自有的 Tailnet 生命周期服务

新增边界：

- `firmware/main/hal/network/tailnet_service.h`
- `firmware/main/hal/network/tailnet_service.cpp`
- `firmware/main/hal/network/tailnet_credentials.h/.cpp`
- 可选的纯逻辑 `tailnet_state_machine.h/.cpp`，用于 host test

`TailnetService` 独占 `microlink_t*`、生命周期任务、事件队列、当前 STA netif/IP 和脱敏状态快照。`Hal::startNetwork()` 在 `startSntp()` 后只调用一次 `TailnetService::StartSupervisor()`，该调用不得等待 Tailnet 上线。

服务通过独立的 ESP-IDF `WIFI_EVENT`/`IP_EVENT` handler 接收 disconnect、lost-IP 和 got-IP 事件，并以低频轮询 `WifiManager::IsConnected()` 与 STA IP 作为漏事件保护。ESP-IDF event handler 允许多个订阅者，因此无需长期占用 `Board::SetNetworkEventCallback()`。事件回调只投递小消息；所有 `microlink_init/start/rebind/stop/destroy` 都在单一 supervisor task 串行执行。

状态机为：

```text
Disabled
  -> WaitWifi
  -> WaitTime
  -> Starting
  -> Registering/Connected
  -> Rebinding
  -> Backoff
  -> Degraded
  -> Stopping
```

系统时间以 SNTP callback 通知加最小 epoch 校验共同判定。Wi-Fi 短暂恢复且 STA netif 未变化时先 soft `microlink_rebind()`；netif/IP 变化、MicroLink error 或 soft 恢复超时则 stop/start。每次状态迁移带 generation id，丢弃旧网络世代的延迟事件。快速重试次数有限，之后采用带上限的指数退避。

### 3. 保持 STA 默认路由，并显式固定 overlay underlay

移植不调用 `netif_set_default(wg_netif)`，`exit_node_ip` 为 `0`，`advertise_routes` 为空，也不安装 `0.0.0.0/0` 或其他 subnet route hook。MicroLink 创建的 `/10` netif 只负责 Tailnet 地址，实际 peer 仍由 `/32` AllowedIP 选择。

MicroLink connected 后，服务从 `WIFI_STA_DEF` 获得底层 lwIP STA netif，并调用 `microlink_pin_wg_output_netif()`。每次 got-IP 或 netif generation 改变时重新 pin 后再 rebind。控制面、DNS、DERP 和 STUN 的公网目的地址继续命中 STA 默认路由；WireGuard 外层 UDP 由 pin 强制走 STA，避免未来路由变化引入递归。

应用访问 Codex 网关时使用 MicroLink TCP API或等价的“socket 绑定本机 Tailnet IP”包装，不直接把普通 XiaoZhi `Network` 全局替换为 VPN transport。这样 inner TCP 由 lwIP 处理，outer transport 可以在 DERP 和 direct UDP 之间切换。

### 4. 采用 DERP-first 的 endpoint 信任模型

从控制面得到的 endpoint 只作为 DISCO 探测候选，不直接写入 WireGuard peer。新 peer 的 endpoint 初始为空，数据经 DERP。只有从候选地址收到且通过目标 peer DISCO key 验证的 pong，才能调用 `wireguardif_update_endpoint()` 安装 direct path。

这个选择牺牲了首次连接的少量延迟和 DERP 带宽，但避免在 iPhone 热点、CGNAT、hairpin NAT 或过期 endpoint 下形成“一边经 DERP 收包、另一边向不可达 UDP 地址发包”的单向故障。

### 5. Tailnet 身份与 bootstrap 凭据分离

MicroLink 的 machine、WireGuard、DISCO key 和 peer cache 保持在其 NVS namespace。StackChan 新增 `stack_tailnet` namespace，只保存节点名、启用状态和一次性 bootstrap auth key。正常运行复用持久节点身份，不长期保存 auth key。

首期 provisioning 使用物理 USB 串口的本地命令/工具：

- 仅允许 set、clear 和 status，不允许读取 key。
- secret 输入不回显，日志只显示写入结果。
- 推荐 one-off 或短有效期、带目标 tag 的 auth key。
- 首次进入 `ML_STATE_CONNECTED` 后擦除 NVS bootstrap key，并清零服务持有的可擦除缓冲。
- 发布构建和 CI 不注入 key；发布产物增加 `tskey-auth-` 字符串扫描。

Tailnet factory reset 只调用 MicroLink identity reset 并清理 `stack_tailnet`，不得擦除整个默认 NVS 分区。首期不调整 partition table，先测量当前 16 KB NVS 的空闲 entries；`ML_NVS_MAX_PEERS` 初值取 `16`。若容量不足，必须先形成独立的分区迁移设计，不能在本变更中静默扩大或格式化 NVS。

### 6. 以 Kconfig 关闭高风险和非必要能力

新增 `CONFIG_STACKCHAN_TAILNET` 总开关，默认关闭。CoreS3 bring-up 配置：

```text
CONFIG_ML_H2_BUFFER_SIZE_KB=64
CONFIG_ML_JSON_BUFFER_SIZE_KB=64
CONFIG_ML_MAX_PEERS=8
CONFIG_ML_NVS_MAX_PEERS=16
CONFIG_ML_ZERO_COPY_WG=n
CONFIG_ML_ENABLE_CELLULAR=n
CONFIG_ML_ENABLE_CONFIG_HTTPD=n
```

运行时 config 同时设置 `exit_node_ip=0`、空 `advertise_routes`，并不启动 `ml_net_switch`。所有 allocation/task 创建结果必须检查；失败时销毁部分实例并进入 Tailnet degraded，不能触发全固件 abort。启动、连接和停止前后记录 internal heap、largest block、PSRAM 和 NVS 水位，用真机数据决定是否继续保持 64 KB 配置。

### 7. 诊断只暴露最小状态

内部状态快照包含：supervisor 状态、MicroLink 状态、最近错误枚举、重试次数、Tailnet IPv4、peer 数量、目标 peer 的 DERP region/direct 标记、STA generation 和资源水位。日志不得打印 auth key、私钥、完整 public/disco key、完整控制面响应或 NVS blob。

首期不增加常驻 UI。串口日志用于 bring-up，其他模块以后可只读状态快照。Codex transport 只消费“connected/target reachable”和 TCP 连接接口，不直接持有 `microlink_t*`。

### 8. 验证分为 host、固件构建和真机三层

Host test 覆盖纯状态机：启动门控、事件去重、generation、soft/full recovery、退避和 disabled 路径。依赖测试检查固定 SHA、必要补丁和禁止 secret。ESP-IDF 构建分别验证 Tailnet off/on，off 构建不得链接或启动 MicroLink。

CoreS3 真机矩阵至少包括：

| 场景 | 必要结果 |
| --- | --- |
| 家庭 Wi-Fi冷启动 | SNTP 后注册/连接，公网与 Tailnet 同时可用 |
| iPhone 热点/CGNAT | DERP 下 Mac 到设备和设备到 Mac 均可达，TCP/WebSocket 双向传输 |
| 可直连网络 | 初始 DERP 可用，DISCO 验证后升级 direct |
| 热点关闭再开启 | 无 watchdog/泄漏，重绑或有界重启后恢复 |
| 家庭 Wi-Fi与热点切换 | STA pin 更新，旧地址不再发送 |
| Mac 睡眠再唤醒 | peer 恢复后 TCP 可重新建立 |
| Tailscale 控制面阻断 | Tailnet 退避，XiaoZhi、OTA 和公网 API 不受影响 |
| 内存/NVS 压力 | Tailnet 可降级，官方功能不崩溃 |

Mac 侧验收要求网关只监听 Tailnet IPv4，ACL 仅允许 StackChan tag/node 访问目标端口。ACL 与网关实现不纳入固件提交，但其测试结果纳入验收记录。

## Risks / Trade-offs

- **[非官方协议实现可能随 Tailscale 服务变化失效]** -> 固定 commit、保留 DERP/direct 诊断、将依赖升级作为独立变更，不自动跟随 `main`。
- **[PR #21 仍未合入所选基线]** -> 仓库保留可追溯补丁并使 patch failure fail closed；上游合入后先做等价性审查再删除。
- **[HTTP 配置服务器虽然默认不启动，但源码和依赖仍无条件进入组件构建]** -> 复用上游 `CONFIG_ML_ENABLE_CONFIG_HTTPD=n`，以本地 CMake 补丁裁掉源码和 `esp_http_server` 依赖，并在真机扫描监听 socket。
- **[64 KB MapResponse 缓冲无法容纳较大 Tailnet]** -> 首期限制目标 Tailnet 与 peer 数量，记录解析错误和水位；需要更大缓冲时以 CoreS3 PSRAM 实测决定。
- **[默认 16 KB NVS 还承载 Wi-Fi 和其他产品数据]** -> 首期把 cached peers 降至 16 并测量 entries；空间不足时 fail degraded，不擦除或迁移现有 NVS。
- **[全局 lwIP netif 操作可能影响官方连接]** -> 不改 default netif，只加入 `/10` overlay 并在 disabled/stop 时验证完整移除；增加 off/on 路由回归。
- **[iPhone 热点的 NAT 与客户端隔离不可控]** -> DERP 是必过验收路径，direct 只作为验证后的优化。
- **[串口 provisioning 仍依赖物理访问安全]** -> 不提供读取接口、不回显 key、使用 one-off/短期 key、成功后擦除，发布构建不包含凭据。
- **[MicroLink 任务和缓冲挤压音频/动画资源]** -> 先使用最小缓冲和 peer 上限，记录 internal heap/PSRAM/stack high-water mark，并以连续运行测试决定是否准入。

## Migration Plan

1. 引入 `CONFIG_STACKCHAN_TAILNET=n` 的空壳与 host-testable 状态机，确认关闭时固件行为和镜像构建不变。
2. 固定 MicroLink commit、加入 required patch 校验和许可证清单，完成 ESP-IDF 5.5.4 component build。
3. 实现凭据存储与物理 provisioning，再接入 supervisor；先只观察连接状态，不接 Codex 业务流量。
4. 固定 STA underlay，完成 Tailnet ping、TCP 和 WebSocket probe；验证 DERP-first 与 direct upgrade。
5. 执行完整真机矩阵和 30 分钟以上资源/重连 soak，记录固件版本、Tailnet 路径和水位。
6. 验收通过后才允许目标 CoreS3 构建打开 `CONFIG_STACKCHAN_TAILNET`；官方默认仍保持关闭。

回滚时关闭 `CONFIG_STACKCHAN_TAILNET` 并重新构建即可。代码级回滚可移除 StackChan Tailnet service、`repos.json` 项和 MicroLink patch；由于没有修改默认路由或 partition table，官方 Wi-Fi 数据无需迁移。若需要清理 Tailnet 身份，使用专用 factory reset，不得执行整分区 NVS erase。

## Open Questions

- 目标 Tailnet 的实际节点数和首个 MapResponse 大小是否稳定落在 64 KB H2/JSON 缓冲内？
- 当前 16 KB 默认 NVS 在已有 Wi-Fi、账号和产品数据后还剩多少 entries，`ML_NVS_MAX_PEERS=16` 是否可接受？
- CoreS3 同时运行音频、动画、XiaoZhi 与 MicroLink 时，internal heap largest block、PSRAM 和各任务 stack high-water mark 的准入阈值应设为多少？
- 物理 USB provisioning 应复用现有 console 初始化还是使用独立的最小串口协议，哪一种不会与日志/USB 模式冲突？
- Mac Codex 网关最终使用 HTTP、WebSocket 还是二者并存；固件层只提供 TCP transport，但验收 probe 需要锁定端口和会话时长。
