# ibn_attitude

Python ROS 2 package that connects to a Pixhawk running ArduCopter, reads live telemetry, and publishes data over ROS 2 topics.

---

## Repository Structure

```
ibn_attitude/
├── docker/
│   ├── Dockerfile          # PC (x86_64) build
│   ├── Dockerfile.arm      # Jetson (ARM64) build
│   └── entrypoint.sh       # Container startup script
├── docker-compose.yml      # Docker Compose configuration
├── github_token.txt        # Your GitHub token (create this file)
├── docs/
│   └── system_diagram.puml # PlantUML system diagram
├── src/
│   └── ibn_attitude/       # ROS 2 package
│       ├── config/         # Node configurations
│       ├── launch/         # Launch files
│       ├── nodes/          # Node implementations
│       │   ├── gps_injection/
│       │   └── pixhawk_bridge/
│       ├── package.xml
│       └── setup.py
└── README.md
```

---

## System Architecture

![System Architecture](docs/system_diagram.svg)

---

## Prerequisites

### GitHub Token Setup

Before building the Docker image, you need a GitHub personal access token:

1. Go to [GitHub Settings > Personal access tokens](https://github.com/settings/tokens)
2. Generate a new token with `repo` scope
3. Create a file named `github_token.txt` in the project root:
   ```bash
   echo "ghp_your_token_here" > github_token.txt
   ```

---

## Building the Docker Image

### Build on PC (x86_64)

```bash
DOCKER_BUILDKIT=1 docker build \
  -f docker/Dockerfile \
  --secret id=gh_token,src=github_token.txt \
  -t pixhawk_bridge:ibn .
```

### Build on Jetson (ARM64)

```bash
DOCKER_BUILDKIT=1 docker build \
  -f docker/Dockerfile.arm \
  --secret id=gh_token,src=github_token.txt \
  -t pixhawk_bridge:jetson .
```

---

## Running the Container

### Using Docker Compose

```bash
docker-compose up --build
```

### Using Docker Directly (PC)

```bash
docker run -it --rm \
  --device /dev/ttyACM0:/dev/ttyACM0 \
  --device /dev/ttyACM1:/dev/ttyACM1 \
  --network host \
  pixhawk_bridge:ibn
```

### Using Docker Directly (Jetson)

```bash
docker run -it --rm \
  --device /dev/ttyACM0:/dev/ttyACM0 \
  --device /dev/ttyACM1:/dev/ttyACM1 \
  --network host \
  pixhawk_bridge:jetson
```

---

## Configuration

The config files in `src/ibn_attitude/config/` allow changing topic names and polling frequency:

| Parameter | Default Value |
|-----------|---------------|
| `attitude_topic_name` | `/mavlink/attitude` |
| `altitude_topic_name` | `/mavlink/altitude` |
| `hz` | `50` |

---

## ROS 2 Topics

### Attitude Topic

```bash
ros2 topic echo /mavlink/attitude
```

**Message Type:**
```bash
Metadata metadata
std_msgs/Header header
uint32 time_boot_ms
float64 roll
float64 pitch
float64 yaw
float64 rollspeed
float64 pitchspeed
float64 yawspeed
```

### Altitude Topic

```bash
ros2 topic echo /mavlink/altitude
```

**Message Type:**
```bash
std_msgs/Header header
Metadata metadata
float64 alt
```

---

## Running the Nodes

Inside the container:

```bash
# Build the workspace
cd /root/dev/src && colcon build

# Source the workspace
source install/setup.bash

# Run individual nodes
ros2 run ibn_attitude pixhawk_bridge
ros2 run ibn_attitude gps_injection

# Or use the launch file
ros2 launch ibn_attitude pixhawk_bridge.launch.py
```

---

## Dependencies

### System Packages
- ROS 2 Galactic
- Python 3
- colcon
- rosdep

### Python Packages
- `pymavlink==2.4.40`
- `pyserial`
- `pyyaml`

---

## External Packages

This package depends on the [interfaces](https://github.com/JerichoGroup/interfaces) package for custom message definitions.
