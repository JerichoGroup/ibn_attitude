# ibn_attitude - IBN MAVLink Bridge

## Overview

ROS 2 package that connects to a Pixhawk running ArduCopter, reads telemetry via MAVLink, and publishes to ROS 2 topics. Also injects computed GPS back to Pixhawk.

---

## Repository Structure

```
/home/user/clones/ibn_attitude/
├── docker/
│   ├── Dockerfile              # PC (x86_64) build
│   ├── Dockerfile.arm        # Jetson (ARM64) build
│   └── entrypoint.sh         # Container startup script
├── docker-compose.yml         # PC (x86_64) compose
├── docker-compose-arm.yml     # Jetson (ARM64) compose
├── github_token.txt           # GitHub token (create with your token)
├── CLAUDE.md                  # This file
├── README.md
├── .gitignore
├── .gitlint                   # Git commit hooks
├── .pre-commit-config.yaml    # Pre-commit hooks
├── pyproject.toml             # Python project config (ruff, mypy)
├── g_tools/                   # Git hooks
│
├── docs/
│   ├── system_diagram.puml
│   └── system_diagram.svg
│
└── src/
    └── ibn_mavlink/           # Main ROS 2 package
        ├── setup.py
        ├── package.xml
        ├── resource/
        │   └── ibn_mavlink    # Non-empty marker file
        ├── setup.cfg
        ├── launch/
        │   ├── __init__.py
        │   └── pixhawk_bridge.launch.py
        ├── test/
        ├── ibn_mavlink/       # Python package
        │   ├── __init__.py
        │   ├── config/        # Config files (INSIDE package)
        │   │   ├── pixhawk_bridge.yaml
        │   │   └── gps_injection.yaml
        │   ├── mavlink/       # Shared MAVLink module
        │   │   ├── __init__.py
        │   │   └── client.py
        │   ├── pixhawk_bridge/
        │   │   ├── __init__.py
        │   │   ├── node.py
        │   │   └── translator.py
        │   └── gps_injection/
        │       ├── __init__.py
        │       ├── node.py
        │       ├── converter.py
        │       └── sender.py
```

---

## Architecture

```
                    ┌─────────────────────────────┐
                    │      Pixhawk (/dev/ttyACM0)  │
                    └─────────────┬───────────────┘
                                  │
            ┌─────────────────────┴─────────────────────┐
            │                                           │
            ▼                                           ▼
┌───────────────────────┐                   ┌───────────────────────┐
│   pixhawk_bridge      │                   │   gps_injection       │
│   (reads telemetry)   │                   │   (sends GPS back)    │
│                       │                   │                       │
│ MAVLinkClient         │                   │ MAVLinkClient         │
│ - read_enabled=True  │                   │ - read_enabled=False │
│ - stream_rate_hz=50 │                   │ - stream_rate_hz=0   │
└──────────┬────────────┘                   └──────────┬────────────┘
           │                                      │
           ▼                                      ▼
    /pixhawk/global_position              /IBN/result (from algorithm)
    /pixhawk/attitude
```

---

## Build & Run

### Inside Docker

```bash
# Rebuild (always clean first)
cd /root/dev/src && rm -rf build install log && colcon build

# Source workspace
source install/setup.bash

# Run nodes
ros2 run ibn_mavlink pixhawk_bridge
ros2 run ibn_mavlink gps_injection

# Or use launch file (runs both nodes)
ros2 launch ibn_mavlink pixhawk_bridge.launch.py
```

---

## Setup.py Key Points

```python
from setuptools import setup, find_packages

package_name = 'ibn_mavlink'

setup(
    packages=find_packages(include=['ibn_mavlink', 'ibn_mavlink.*']),
    zip_safe=False,                           # IMPORTANT: must be False
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config',
            ['ibn_mavlink/config/pixhawk_bridge.yaml',
             'ibn_mavlink/config/gps_injection.yaml']),
        ('share/' + package_name + '/launch',
            ['launch/pixhawk_bridge.launch.py', 'launch/__init__.py']),
    ],
    entry_points={
        'console_scripts': [
            'gps_injection = ibn_mavlink.gps_injection.node:main',
            'pixhawk_bridge = ibn_mavlink.pixhawk_bridge.node:main',
        ],
    },
)
```

Note: Launch files at `src/ibn_mavlink/launch/` must be listed in `data_files` to be installed to the share directory.

---

## Config Loading (node.py)

Uses `ament_index_python.get_package_share_directory()` for proper ROS 2 install paths:

```python
from ament_index_python import get_package_share_directory
from pathlib import Path

def main(args=None):
    config_dir = get_package_share_directory('ibn_mavlink')
    config_path = Path(config_dir) / 'config' / 'pixhawk_bridge.yaml'
    config = load_config(config_path)
```

---

## MAVProxy Setup (Optional)

For two separate connections via MAVProxy:

```bash
# Terminal 1: Start MAVProxy with two UDP outputs
mavproxy.py --device /dev/ttyACM0 --baud 115200 --out 127.0.0.1:14550 --out 127.0.0.1:14551
```

Update configs to use UDP:
- pixhawk_bridge.yaml: `connection_string: "udp://127.0.0.1:14550"`, `baud_rate: 0`
- gps_injection.yaml: `connection_string: "udp://127.0.0.1:14551"`, `baud_rate: 0`

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "No executable found" | Clean rebuild: `rm -rf build install log && colcon build` |
| "ModuleNotFoundError" | Set `zip_safe=False` in setup.py |
| "Config not found" | Use `get_package_share_directory()` |
| Empty marker file | Ensure `resource/ibn_mavlink` has content (non-empty) |
| "Launch file not found in share directory" | Add launch files to `data_files` in setup.py |
| GPS injection not working | Ensure Pixhawk already has internal GPS fix before external injection |

---

## Dependencies

- `rclpy`
- `interfaces` (external ROS package - JerichoGroup)
- `python3-yaml`
- `python3-pymavlink`
