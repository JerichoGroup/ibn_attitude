# Test Plan

## Overview

This document describes the test strategy for ibn_attitude ROS 2 package.

## Test Structure

```
src/ibn_mavlink/
└── test/
    ├── __init__.py
    ├── test_client.py           # MAVLinkClient tests
    ├── test_converter.py        # IBNToGPSConverter tests
    ├── test_translator.py       # MavlinkTranslator tests
    ├── test_gps_injection_node.py
    ├── test_pixhawk_bridge_node.py
    ├── conftest.py              # Shared fixtures
    └── resources/
        ├── valid_config.yaml
        └── invalid_config.yaml
```

## Modules to Test

| Module | File | Priority |
|--------|------|----------|
| MAVLink Client | `ibn_mavlink/mavlink/client.py` | High |
| GPS Converter | `ibn_mavlink/gps_injection/converter.py` | High |
| Mavlink Translator | `ibn_mavlink/pixhawk_bridge/translator.py` | High |
| Pixhawk Bridge Node | `ibn_mavlink/pixhawk_bridge/node.py` | Medium |
| GPS Injection Node | `ibn_mavlink/gps_injection/node.py` | Medium |

## Test Types

### Unit Tests
- **GPSInputParams** - Coordinate conversion to integer formats
- **IBNToGPSConverter** - All conversion paths including edge cases
- **MavlinkTranslator** - Message field mapping and type conversions

### Integration Tests
- **MAVLinkClient** with mocked pymavlink connection
- **PixhawkTelemetry** node with mocked MAVLinkClient and ROS 2 publishers
- **GPSInjectionNode** with mocked MAVLinkClient and ROS 2 subscription

## Key Test Cases

### MAVLinkClient
- Coordinate conversion (lat/lon/alt to integers)
- Satellite count handling
- HDOP to accuracy conversion
- Thread-safe message retrieval via `get_latest()`
- Background thread stop behavior

### IBNToGPSConverter
- Valid position extraction (position_valid=True, length=3)
- Invalid position handling (position_valid=False, wrong length)
- Full conversion flow with payload creation

### MavlinkTranslator
- GlobalPositionInt field mapping and velocity int casting
- Attitude field mapping
- Header timestamp creation

### GPSInjectionNode
- Valid/invalid IBNResult handling
- GPS injection when payload cached
- Error handling in injection loop

### PixhawkTelemetry
- Global position and attitude publishing
- Initial position caching

## Edge Cases

1. **Coordinate conversion**: Negative lat/lon (South/West), extreme values
2. **Empty messages**: `get_latest()` returns None on first call
3. **Invalid IBNResult**: position_valid=False, wrong position array length
4. **Thread safety**: Concurrent `get_latest()` while `_read_loop` writes
5. **Injection without data**: `_inject_loop` called before first IBNResult
6. **Config errors**: Missing file, malformed YAML

## Running Tests

```bash
# Inside container
cd /root/dev/src
python3 -m pytest src/ibn_mavlink/test/ -v

# Or via colcon
colcon test --packages-select ibn_mavlink
```

## Framework

- **pytest** - Already in package.xml dependencies
- **unittest.mock** - For mocking external dependencies (pymavlink, ROS 2)
