# ibn_attitude - IBN MAVLink Bridge

## Overview

ROS 2 package that connects to a Pixhawk running ArduCopter, reads telemetry via MAVLink, and publishes to ROS 2 topics.

---

## Repository Structure

```
/home/user/clones/ibn_attitude/
├── docker/
│   ├── Dockerfile              # PC (x86_64) build
│   ├── Dockerfile.arm         # Jetson (ARM64) build
│   └── entrypoint.sh        # Container startup script
├── docker-compose.yml
├── github_token.txt         # GitHub token (create with your token)
├── CLAUDE.md             # This file
├── README.md
├── .gitignore
│
├── docs/
│   ├── system_diagram.puml
│   └── system_diagram.svg
│
└── src/
    └── ibn_mavlink/           # Main ROS 2 package
        ├── ibn_mavlink/
        │   ├── config/         # Config files (IN the package)
        │   │   ├── pixhawk_bridge.yaml
        │   │   └── gps_injection.yaml
        │   ├── launch/       # Launch files
        │   │   └── pixhawk_bridge.launch.py
        │   └── nodes/       # Node implementations
        │       ├── pixhawk_bridge/
        │       │   ├── node.py
        │       │   ├── client.py
        │       │   └── translator.py
        │       └── gps_injection/
        │           ├── node.py
        │           ├── converter.py
        │           └── sender.py
        ├── resource/
        │   └── ibn_mavlink
        ├── package.xml
        └── setup.py
```

---

## Build & Run

### Inside Docker

```bash
# Rebuild
cd /root/dev/src && colcon build

# Source workspace
source install/setup.bash

# Run nodes
ros2 run ibn_mavlink pixhawk_bridge
ros2 run ibn_mavlink gps_injection

# Or use launch file
ros2 launch ibn_mavlink pixhawk_bridge.launch.py
```

---

## Key Files

### node.py config loading
Uses `ament_index_python.get_package_share_directory()`:
```python
from ament_index_python import get_package_share_directory

config_dir = get_package_share_directory('ibn_mavlink')
config_path = Path(config_dir) / 'config' / 'pixhawk_bridge.yaml'
```

### setup.py key points
- `packages=find_packages(include=['ibn_mavlink', 'ibn_mavlink.*'])`
- `zip_safe=False` (important for module discovery)
- Config files in `data_files` under `share/ibn_mavlink/config/`
- marker file at `resource/ibn_mavlink` (non-empty)

---

## Dependencies

### package.xml
- `rclpy`
- `interfaces` (external ROS package)
- `python3-yaml`
- `python3-pymavlink`

---

## Common Issues

1. **"No executable found"** -> Rebuild with `colcon build`
2. **"ModuleNotFoundError"** -> Set `zip_safe=False` in setup.py
3. **"Config not found"** -> Use `get_package_share_directory()` for config paths
4. **Empty marker file** -> Ensure `resource/ibn_mavlink` has content (e.g. "ibn_mavlink")