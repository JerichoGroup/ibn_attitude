# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A ROS 2 Galactic Python package that bridges a Pixhawk (running ArduCopter) and ROS 2. The git repo is named `ibn_attitude`, but the actual ROS package is **`ibn_mavlink`** (under `src/ibn_mavlink/`) — the README and Dockerfile clone paths still use the old `ibn_attitude` name in places, so don't trust those paths over the on-disk layout.

It runs two ROS nodes (entry points in `setup.py`):
- **`pixhawk_bridge`** — reads MAVLink telemetry (`ATTITUDE`, `GLOBAL_POSITION_INT`) and publishes it as ROS messages.
- **`gps_injection`** — subscribes to `IBNResult` and injects the position back into the Pixhawk as a MAVLink `GPS_INPUT` message.

## Architecture

Three layers, deliberately separated so the data-mapping logic is testable without ROS or hardware:

1. **Transport — `ibn_mavlink/mavlink/client.py` (`MAVLinkClient`).** Owns the pymavlink connection. Runs a daemon read thread that caches the *latest* message per type in a dict (`get_latest(msg_type)`); there is no queue, consumers always get the most recent frame. Handles heartbeat wait, stream-rate requests, and an automatic reconnect-with-backoff loop guarded by locks. Reconnect triggers on two conditions: a `recv` exception, or a **liveness timeout** (`heartbeat_timeout`, default 5 s) when no message has arrived — the latter matters because a dropped UDP link returns `None` rather than raising, so it would otherwise never reconnect. `read_enabled=False` is used by the injection node (it only sends, never reads). `send_gps_input()` intentionally sends velocity flagged-ignored (EKF ignores it), sends a fixed unitless `hdop`/`vdop` (a DOP, *not* meters), and sends `horiz_accuracy`/`vert_accuracy` separately in meters — these are distinct `GPSInputParams` fields, do not conflate them.
2. **Translation — pure static methods, no I/O:**
   - `pixhawk_bridge/translator.py` (`MavlinkTranslator`): MAVLink message → ROS message. Values are passed through in MAVLink-native scaling (lat/lon as deg×1e7, alt in mm, etc.) — **no unit/frame conversion**. See README "MAVLink ↔ ROS GPS Conventions" for the field table.
   - `gps_injection/converter.py` (`IBNToGPSConverter`): `IBNResult` → `GPSInputPayload`, returning `None` for invalid positions (which callers treat as "skip").
3. **Nodes — `*/node.py` (`PixhawkTelemetry`, `GPSInjectionNode`).** rclpy `Node`s that wire the above together on a timer. Both load config the same way: `get_package_share_directory("ibn_mavlink") / "config" / <file>.yaml`, so **config must be reinstalled (rebuilt) to take effect** — editing the source YAML alone does nothing at runtime. Both override `destroy_node()` to stop the MAVLink client before ROS teardown.
   - **Logger gotcha:** rclpy's `Node` stores its own logger in `self._logger` (returned by `get_logger()`), so the app's file/stdout logger is held in **`self._app_logger`** instead — do not reassign `self._logger` or you clobber rclpy's.
   - **`GPSInjectionNode` injection is decoupled from arrival:** `_callback` stores the latest payload + a `time.monotonic()` stamp whenever an `IBNResult` arrives; a separate timer (`inject_rate_hz`) sends it. If the payload goes older than `inject_max_age_s` (default 1 s) the loop stops injecting and clears it, so a frozen/last-known position is never re-injected as a fresh GPS lock. Injection resumes automatically when a fresh message arrives.

**External dependency:** the custom messages (`Attitude`, `GlobalPositionInt`, `IBNResult`) live in a separate private repo, [`JerichoGroup/interfaces`](https://github.com/JerichoGroup/interfaces), cloned alongside this package in the Docker build. It is not vendored here.

## Build & run

This targets ROS 2 Galactic on a Jetson (ARM64); there is no x86 Dockerfile despite the README mentioning one. Building the image requires a `github_token.txt` (a GitHub PAT with `repo` scope) in the repo root — it's used to clone the private `ibn_attitude` + `interfaces` repos.

```bash
# Build + run the full stack (pixhawk_bridge + a mavproxy that fans the serial link out to UDP)
docker-compose -f docker-compose-arm.yml up --build

# Inside a container / workspace, build with colcon from the workspace root (/root/dev)
colcon build --packages-select ibn_mavlink

# Run (after sourcing /opt/ros/galactic/install/setup.bash and install/setup.bash)
ros2 run ibn_mavlink pixhawk_bridge
ros2 run ibn_mavlink gps_injection
ros2 launch ibn_mavlink pixhawk_bridge_launch.py   # launches both nodes
```

`mavproxy` splits `/dev/ttyACM0` to UDP `127.0.0.1:14550` (injection) and `:14551` (bridge) — matching the two `connection_string` values in the config YAMLs. All containers run on `ROS_DOMAIN_ID=42` and host networking.

## Tests

```bash
cd src/ibn_mavlink && python3 -m pytest test -v        # all tests
python3 -m pytest test/test_client.py -v               # one file
python3 -m pytest test/test_client.py::<name> -v       # one test
colcon test --packages-select ibn_mavlink              # via colcon
```

Tests run **without ROS or hardware**: `test/conftest.py` injects `MagicMock`s for the `interfaces` and `pymavlink` modules into `sys.modules` and provides sample-message / config fixtures. When adding tests that touch new `interfaces` messages or pymavlink calls, extend those mocks rather than importing the real packages.

Note: `rclpy.create_subscription()` runs a type-support check that **rejects the mocked `interfaces` messages**, so `GPSInjectionNode` tests patch `create_subscription` (autouse fixture in `test_gps_injection_node.py`). `create_publisher` does not do this check, so the bridge tests don't need it.

## Linting & commit conventions

`pre-commit` runs ruff, ruff-format (double quotes), and mypy (`--ignore-missing-imports`). Config is in `pyproject.toml` (ruff, py310, line-length 120 but `E501` is ignored; `test/` and `conftest.py` are fully ignore-listed). Beyond the standard tools, three **custom local hooks** in `g_tools/hooks/` are enforced and will rewrite/fail your files — match these conventions when writing Python:
- **Every private method (`def _foo`) must have a docstring.**
- **A blank line is required immediately after every function docstring.**
- **Section-header comments are auto-reformatted** to `# ==================== Title ====================` (20 `=` each side, title capitalized).

Commit messages are linted by gitlint (`.gitlint`): titles must not contain `wip`, `todo`, or `fixme`.
