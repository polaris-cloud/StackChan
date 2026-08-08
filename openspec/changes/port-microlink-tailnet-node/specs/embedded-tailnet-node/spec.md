## ADDED Requirements

### Requirement: MicroLink 依赖必须可复现且经过安全核验
固件 MUST 从固定的完整 Git commit 获取 MicroLink，并 MUST 在编译前核验来源、MIT 许可证、ESP-IDF 5.5.x 兼容性和本地安全补丁。依赖获取流程 MUST 在 commit 不匹配或必要补丁无法干净应用时失败，不得静默跳过。

#### Scenario: 固定依赖成功
- **GIVEN** `repos.json` 中记录了已审查的 MicroLink 完整 commit 和必要补丁
- **WHEN** 开发者在干净目录执行依赖获取
- **THEN** 获取结果的 `HEAD` 等于指定 commit，必要补丁全部通过检查并应用

#### Scenario: 必要补丁失配
- **GIVEN** 上游内容与安全补丁的上下文不再匹配
- **WHEN** 依赖获取脚本检查补丁
- **THEN** 脚本 MUST 以非零状态终止，并明确指出 MicroLink 补丁未应用

### Requirement: 节点只能在 underlay 就绪后启动
Tailnet 服务 MUST 在官方 Wi-Fi 已获得有效 IPv4 地址且系统时间可用于 TLS 证书校验后才调用 `microlink_start()`。初始化与启动 MUST 幂等，且不得重复创建 MicroLink 任务、队列或 netif。

#### Scenario: Wi-Fi 已连接但时间未同步
- **GIVEN** `WifiManager` 已连接且 STA 获得 IPv4 地址
- **WHEN** SNTP 尚未提供可接受的系统时间
- **THEN** Tailnet 服务保持等待状态，不发起控制面 TLS 连接

#### Scenario: 启动条件满足
- **GIVEN** Wi-Fi IPv4 与有效系统时间均已就绪
- **WHEN** 生命周期任务再次评估启动条件
- **THEN** 系统只创建一个 MicroLink 实例并异步启动连接

### Requirement: StackChan 必须使用独立且持久的节点身份
StackChan MUST 以独立节点名称注册到 Tailnet，并 MUST 将 MicroLink 生成的 machine、WireGuard 和 DISCO 身份保存在 NVS，以便正常重启后复用同一节点身份。恢复出厂设置 MUST 能显式删除这些身份与 peer 缓存。

#### Scenario: 注册后重启
- **GIVEN** 设备已成功注册并将节点身份写入 NVS
- **WHEN** 设备在没有 bootstrap auth key 的情况下重启
- **THEN** 设备使用原身份重新连接，不创建第二个 Tailnet 节点

#### Scenario: Tailnet 恢复出厂
- **GIVEN** NVS 中存在节点身份和 peer 缓存
- **WHEN** 用户通过受控的本地操作执行 Tailnet factory reset
- **THEN** 系统删除 MicroLink 身份和缓存，但不删除官方 Wi-Fi 配置或其他 StackChan 数据

### Requirement: Bootstrap 凭据必须受控
系统 MUST 仅通过本地、明确的 provisioning 流程接收一次性或短有效期 Tailscale auth key。auth key MUST 不进入 Git、发布固件、日志、崩溃信息或状态接口；成功注册后 MUST 从临时存储和可擦除内存中删除。

#### Scenario: 本地写入 bootstrap key
- **GIVEN** 用户持有一次性或短有效期 auth key，并对设备具有物理访问
- **WHEN** 用户执行本地 provisioning
- **THEN** key 被写入受限的临时存储，命令输出和普通日志不回显 key

#### Scenario: 注册完成
- **GIVEN** MicroLink 已使用 bootstrap key 成功注册并持久化节点身份
- **WHEN** 状态首次进入 `ML_STATE_CONNECTED`
- **THEN** 系统清除 bootstrap key，后续重启不再依赖该 key

### Requirement: 连接生命周期必须可恢复
Tailnet 服务 MUST 观察官方 Wi-Fi 连接状态而不接管 `WifiBoard`。Wi-Fi 断开时 MUST 停止发送 Tailnet 流量；同一 STA 恢复时 MUST 先尝试 `microlink_rebind()`，底层 netif 或地址改变、软恢复超时或实例错误时 MUST 执行有界的 stop/start 恢复。重试 MUST 使用退避且不得阻塞官方网络任务。

#### Scenario: iPhone 热点短暂中断后恢复
- **GIVEN** Tailnet 已连接且 iPhone 热点暂时断开
- **WHEN** STA 重新获得 IPv4 地址
- **THEN** Tailnet 服务触发一次幂等恢复，并最终回到 connected 或带原因的 degraded 状态

#### Scenario: 连续恢复失败
- **GIVEN** 控制面、DERP 或 DNS 持续不可达
- **WHEN** 恢复尝试超过配置的快速重试次数
- **THEN** 系统进入退避，不发生忙循环、任务泄漏或看门狗复位，官方公网功能仍可运行

### Requirement: 未验证的 peer endpoint 不得承载数据
MicroLink 集成 MUST 包含与 CamM2325/microlink PR #21 等价或更严格的端点验证规则：MapResponse 中广告的 endpoint 在收到对应 DISCO 验证前 MUST 不被安装为 WireGuard 直连 endpoint；在此之前数据 MUST 经 DERP，验证成功后才 MAY 升级为 direct UDP。

#### Scenario: CGNAT peer 广告不可达 endpoint
- **GIVEN** Mac peer 的广告 endpoint 从 StackChan 所在网络不可达
- **WHEN** 双方只能通过 DERP 交换数据
- **THEN** StackChan 与 Mac 的 ping 和 TCP 流量保持双向可用，不出现仅单向收包

#### Scenario: 可用直连路径通过验证
- **GIVEN** StackChan 收到来自候选地址且通过 peer DISCO key 校验的 pong
- **WHEN** MicroLink 更新该 peer 的最佳 endpoint
- **THEN** 后续 WireGuard 流量可切换到 direct UDP，并在路径失效后回退 DERP

### Requirement: 运行时必须受资源上限约束并可观测
首期 CoreS3 配置 MUST 将 `ML_H2_BUFFER_SIZE_KB` 和 `ML_JSON_BUFFER_SIZE_KB` 设为 `64`，`ML_MAX_PEERS` 不得超过 `8`，`ML_NVS_MAX_PEERS` 设为经 NVS 容量核验的最小值，并禁用 cellular、net switch、exit node、subnet advertising、zero-copy 和 MicroLink HTTP 配置服务器。分配或任务创建失败 MUST 使 Tailnet 降级而不是使固件崩溃。

#### Scenario: MicroLink 初始化内存不足
- **GIVEN** 某个必要缓冲区或任务栈无法分配
- **WHEN** Tailnet 服务初始化 MicroLink
- **THEN** 服务记录脱敏错误与 heap 水位，释放已分配资源并保持官方 Wi-Fi/XiaoZhi 可用

#### Scenario: 状态诊断
- **GIVEN** Tailnet 服务正在等待、注册、连接、重绑、退避或降级
- **WHEN** 开发者读取串口日志或内部状态快照
- **THEN** 输出包含状态、原因、Tailnet IP、DERP/direct 模式和资源水位，但不包含私钥、auth key 或完整 peer 密钥
