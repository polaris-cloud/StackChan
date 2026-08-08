## 1. Dependency Provenance And Patch Gate

- [ ] 1.1 Record the reviewed MicroLink source URL, MIT license, baseline `aad403af0df6c08500c4236cb09c9ebc5bc00416`, CamM common base, and PR #21 source in the firmware third-party dependency documentation.
- [ ] 1.2 Add `Csontikka/microlink` to `firmware/repos.json` at `components/microlink` using the full pinned commit and a required `firmware/patches/microlink.patch`.
- [ ] 1.3 Extend `firmware/fetch_repos.py` to verify the fetched `HEAD`, distinguish an already-applied patch from a mismatched patch, and fail nonzero when a required patch cannot be applied.
- [ ] 1.4 Add and review the PR #21-equivalent DERP-first endpoint patch; include a focused test or source assertion proving an advertised endpoint is blank until a valid DISCO pong installs it.
- [ ] 1.5 Add a default-off `CONFIG_ML_CONFIG_HTTPD` patch that prevents the HTTP configuration server from starting and removes its server dependency/source when disabled.
- [ ] 1.6 Fetch MicroLink twice in a clean dependency checkout and verify both runs are deterministic, preserve the pinned commit, and report the required patch as applied or already present.

## 2. Build Configuration And State Machine

- [ ] 2.1 Add `CONFIG_STACKCHAN_TAILNET` and the minimal CoreS3 MicroLink settings: 64 KB H2, 64 KB JSON, 8 active peers, 16 cached peers, with cellular, zero-copy and config HTTP server disabled.
- [ ] 2.2 Wire the `microlink` component into `firmware/main/CMakeLists.txt` only for Tailnet-enabled builds, without changing remote, app, server or XiaoZhi source ownership.
- [ ] 2.3 Implement a pure `TailnetStateMachine` for disabled, wait-Wi-Fi, wait-time, starting, connected, rebinding, backoff, degraded and stopping states, including network generation and bounded retry data.
- [ ] 2.4 Add host tests for startup gates, duplicate events, stale generation rejection, soft-rebind escalation, exponential backoff and the disabled path.

## 3. Credential And Identity Handling

- [ ] 3.1 Implement `TailnetCredentialStore` in the `stack_tailnet` NVS namespace with set, consume, clear and status operations that never expose the stored auth key.
- [ ] 3.2 Implement and document a physical USB serial provisioning command/tool that accepts a one-off or short-lived auth key without echoing it and never writes it into tracked files.
- [ ] 3.3 Clear the bootstrap key and its in-memory buffer after the first successful registration while preserving MicroLink machine, WireGuard and DISCO identities for reboot.
- [ ] 3.4 Implement a Tailnet-only factory reset that removes `stack_tailnet`, MicroLink identity and peer cache without erasing official Wi-Fi or product NVS data.
- [ ] 3.5 Add repository and release-image checks for `tskey-auth-`, private key material and accidental credential logging; make release verification fail on a match.

## 4. Tailnet Lifecycle Service

- [ ] 4.1 Add `TailnetService` under `firmware/main/hal/network/` with sole ownership of the MicroLink handle, supervisor task, event queue and sanitized status snapshot.
- [ ] 4.2 Register independent ESP-IDF Wi-Fi/IP handlers plus low-frequency `WifiManager` polling, and notify the supervisor when SNTP time passes the accepted epoch.
- [ ] 4.3 Implement idempotent `microlink_init/start/rebind/stop/destroy` transitions, using rebind first for same-netif recovery and full restart for address/netif changes, timeout or error.
- [ ] 4.4 Resolve `WIFI_STA_DEF` to the active lwIP STA netif and call `microlink_pin_wg_output_netif()` after connect and after every underlay generation change.
- [ ] 4.5 Start the nonblocking supervisor once from `Hal::startNetwork()` after SNTP initialization, without retaining or replacing `Board::SetNetworkEventCallback()`.
- [ ] 4.6 Handle allocation, task and API failures by releasing partial resources and entering degraded/backoff while keeping official Wi-Fi, SNTP, XiaoZhi, OTA and App Center alive.
- [ ] 4.7 Log state transitions, reason codes, Tailnet IP, DERP/direct path and heap/PSRAM/NVS watermarks without logging auth keys or complete cryptographic keys.

## 5. Selective Routing And Transport

- [ ] 5.1 Configure MicroLink with `exit_node_ip=0`, empty advertised routes and no route hook that can replace the STA default route.
- [ ] 5.2 Add a StackChan-owned TCP/UDP transport wrapper that requires a Tailnet destination, binds the Tailnet source through MicroLink, and does not expose `microlink_t*` to Codex business code.
- [ ] 5.3 Add a diagnostic ping/TCP/WebSocket probe for a configured Mac Tailnet IP and port; keep the probe disabled outside bring-up builds.
- [ ] 5.4 Add tests or runtime assertions that public destinations use STA, known Tailnet peers use WireGuard, and unknown `100.64.0.0/10` destinations never fall back to plaintext STA routing.
- [ ] 5.5 Verify stop and disabled flows remove the WireGuard netif and leave the original STA default route, DNS and ordinary BSD sockets operational.

## 6. Host And Firmware Verification

- [ ] 6.1 Run `cmake -S firmware/tests -B firmware/build-host-tests`, build it, and run `ctest --test-dir firmware/build-host-tests --output-on-failure`.
- [ ] 6.2 Build the CoreS3 firmware with Tailnet disabled and verify no MicroLink task, WireGuard netif or HTTP config listener is present at runtime.
- [ ] 6.3 Build the CoreS3 firmware with Tailnet enabled under ESP-IDF 5.5.4 and record image size, static RAM, PSRAM allocation and component dependency changes.
- [ ] 6.4 Exercise forced MicroLink allocation/task failures and confirm Tailnet degrades without abort, watchdog reset or regression in official public-network operations.
- [ ] 6.5 Scan the enabled firmware for listening sockets and credential strings, confirming the MicroLink HTTP config server and reusable auth key material are absent.

## 7. CoreS3 Hardware Acceptance

- [ ] 7.1 Provision a tagged one-off auth key over physical USB, register once, clear the bootstrap key, reboot without it and confirm the same Tailnet node identity reconnects.
- [ ] 7.2 On home Wi-Fi, verify SNTP-gated startup, public HTTPS/XiaoZhi/OTA availability, Tailnet ping, TCP and WebSocket traffic to the Mac gateway.
- [ ] 7.3 On an iPhone hotspot/CGNAT path, force or observe DERP and verify bidirectional Mac-to-StackChan and StackChan-to-Mac ping plus sustained TCP/WebSocket exchange.
- [ ] 7.4 On a network that permits peer-to-peer UDP, verify DERP works first, only a validated DISCO pong installs the endpoint, and traffic then upgrades to direct.
- [ ] 7.5 Switch between home Wi-Fi and the iPhone hotspot and verify generation changes, underlay re-pin, no use of the stale address and bounded recovery without reboot.
- [ ] 7.6 Sleep and wake the Mac, interrupt and restore the hotspot, and block the Tailscale control plane; verify recovery/退避 behavior and isolation from official public services.
- [ ] 7.7 Run at least a 30-minute audio/animation/XiaoZhi plus Tailnet soak test and record minimum internal heap, largest block, PSRAM, task stack high-water marks, NVS free entries, reconnect count and watchdog status.
- [ ] 7.8 Verify the Mac gateway listens only on its Tailnet address and the Tailnet ACL allows this StackChan identity only on the required Codex gateway port.

## 8. Documentation, Rollback And Final Gate

- [ ] 8.1 Document dependency refresh, secret-free provisioning, Tailnet factory reset, expected DERP/direct diagnostics and troubleshooting under `firmware/`.
- [ ] 8.2 Record the exact CoreS3 firmware SHA, MicroLink SHA/patch hash, Tailnet test matrix and resource measurements used for acceptance.
- [ ] 8.3 Verify rollback by disabling `CONFIG_STACKCHAN_TAILNET` and confirming behavior matches the official baseline without changing the partition table or erasing Wi-Fi settings.
- [ ] 8.4 Run the strict OpenSpec validator, inspect the final Git diff for unrelated changes or secrets, and leave every hardware-only item explicitly unchecked until measured on the target devices.
