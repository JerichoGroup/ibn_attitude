# ibn_attitude

Python ROS 2 package that connects to a Pixhawk running ArduCopter, reads live telemetry, and publishes data over ROS 2 topics.

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
```

### Build on Jetson (ARM64)

```bash
DOCKER_BUILDKIT=1 docker build \
  -f docker/Dockerfile.arm \
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

The system uses two YAML configuration files located in:

src/ibn_mavlink/ibn_mavlink/config/

- gps_injection.yaml → controls GPS/IBN injection behavior
- pixhawk_bridge.yaml → controls MAVLink ↔ ROS2 bridge settings

---

### gps_injection.yaml

This file controls the GPS/IBN injection pipeline and ROS publishing rate.

### Example Configuration

ros:
  ibn_result_topic: "/IBN/result"
  inject_rate_hz: 10
  inject_max_age_s: 1.0

log:
  file_path: "/logs/gps_injection.log"

### Parameters

ROS:

- ibn_result_topic
  ROS2 topic where processed IBN results are published.

- inject_rate_hz
  Frequency (Hz) at which GPS/IBN injection runs.

- inject_max_age_s
  Maximum age (seconds) of the last received position before injection stops.
  Prevents a stale fix from being re-injected as a fresh GPS lock.

Log:

- file_path
  Path where injection logs are saved.

---

### pixhawk_bridge.yaml

This file configures the MAVLink connection to the Pixhawk (or SITL) and streaming behavior.

### Example Configuration

mavlink:
  connection_string: "127.0.0.1:14550"
  baud_rate: 115200
  stream_rate_hz: 0   # 0 disables MAVLink streaming requests

ros:
  publish_rate_hz: 20
  global_position_topic: "/monitor/gps_raw_int"
  attitude_topic: "/mavlink/attitude"
  init_position_topic: "/IBN/init_pos"

### Parameters

MAVLink:

- connection_string
  Endpoint for connecting to Pixhawk or SITL (UDP/TCP/serial).

- baud_rate
  Serial communication speed.

- stream_rate_hz
  MAVLink stream request rate. Set to 0 to disable automatic stream requests.

ROS:

- publish_rate_hz
  Update frequency (Hz) of the bridge publish timer.

- global_position_topic
  ROS2 topic for the raw GLOBAL_POSITION_INT telemetry.

- attitude_topic
  ROS2 topic for vehicle attitude data.

- init_position_topic
  ROS2 topic on which the first received global position is (re)published.
---

## MAVLink ↔ ROS GPS Conventions

This package bridges MAVLink telemetry and ROS 2 messages. It does not perform full unit normalization or coordinate frame conversion unless explicitly stated.

---

### Global Position (`GLOBAL_POSITION_INT`)

MAVLink fields are interpreted in their native format:

| Field | MAVLink Format | ROS Representation |
|------|---------------|-------------------|
| `lat` | degrees × 1e7 | int (raw MAVLink value) |
| `lon` | degrees × 1e7 | int (raw MAVLink value) |
| `alt` | millimeters (MSL altitude) | int (raw MAVLink value) |
| `relative_alt` | millimeters above home | int (raw MAVLink value) |
| `vx`, `vy`, `vz` | cm/s | cast to int |
| `hdg` | centidegrees | cast to int |

---

### Attitude (`ATTITUDE`)

- `roll`, `pitch`, `yaw` → radians
- `rollspeed`, `pitchspeed`, `yawspeed` → rad/s
- No unit conversion is applied before publishing

---

### GPS Injection (`GPS_INPUT`)

When injecting GPS data into Pixhawk:

#### Input (ROS → MAVLink expectation)

| Field | Meaning | Unit |
|------|--------|------|
| `lat` | Latitude | degrees |
| `lon` | Longitude | degrees |
| `alt` | Altitude above MSL | meters |
| `vn` | North velocity | m/s |
| `ve` | East velocity | m/s |
| `vd` | Down velocity | m/s |
| `hdop` | Horizontal dilution of precision | unitless |
| `satellites` | Visible satellites | count |

#### MAVLink encoding:

- `lat/lon` → `int(lat/lon × 1e7)`
- `alt` → meters (passed directly)
- timestamps → microseconds (`time.time() * 1e6`)
- `hdop`/`vdop` are unitless dilution-of-precision values (a fixed, sane default — **not** the metric accuracy)
- `horiz_accuracy`/`vert_accuracy` carry the position accuracy in **meters** (from `IBNResult.position_accuracy`)
- velocity is sent but flagged ignored (`GPS_INPUT_IGNORE_FLAG_VEL_HORIZ | VEL_VERT`) because the EKF ignores it
- `fix_type` (3D) and `satellites` are fixed assumptions, not derived from solution quality

---

### Notes

- No ENU/NED coordinate transformation is performed
- Values follow MAVLink-native scaling rules
- ROS consumers must interpret units correctly

---

## Running the Nodes on Jetson

Inside the container:

```bash
# Source the workspace
source /opt/ros/galactic/install/setup.bash
source /root/dev/install/setup.bash

# Run individual nodes
ros2 run ibn_mavlink pixhawk_bridge
ros2 run ibn_mavlink gps_injection

# Or use the launch file
ros2 launch ibn_mavlink pixhawk_bridge_launch.py
```

---

## Dependencies

### System Packages
- ROS 2 Galactic
- Python3
- colcon
- rosdep

### Python Packages
- `pymavlink==2.4.40`
- `pyserial`
- `pyyaml`

---

## External Packages

This package depends on the [interfaces](https://github.com/JerichoGroup/interfaces) package for custom message definitions.

---

## Testing

Tests are located in `src/ibn_mavlink/test/` and use pytest.

### Running Tests

```bash
# Inside container
cd /root/dev/src
python3 -m pytest ibn_attitude/src/ibn_mavlink/test -v

# Or via colcon
colcon test --packages-select ibn_mavlink
```

### Test Structure

- `test_client.py` - MAVLinkClient unit tests
- `test_converter.py` - IBNToGPSConverter tests
- `test_translator.py` - MavlinkTranslator tests
- `test_gps_injection_node.py` - GPS injection node integration tests
- `test_pixhawk_bridge_node.py` - Pixhawk bridge node integration tests
- `conftest.py` - Shared fixtures and mocks

### Test Plan

See [docs/test_plan.md](docs/test_plan.md) for detailed test cases and edge cases.
