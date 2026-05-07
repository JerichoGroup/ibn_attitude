"""Shared test fixtures."""

import sys
from unittest.mock import MagicMock

import pytest

sys.modules["interfaces"] = MagicMock()
sys.modules["interfaces.msg"] = MagicMock()


@pytest.fixture
def mock_mavlink_connection():
    """Create mock pymavlink connection with master and heartbeat message."""

    mock_master = MagicMock()
    mock_master.target_system = 1
    mock_master.target_component = 1

    mock_heartbeat_msg = MagicMock()
    mock_heartbeat_msg.get_type.return_value = "HEARTBEAT"

    mock_master.wait_heartbeat.return_value = True

    return mock_master, mock_heartbeat_msg


@pytest.fixture
def mock_pymavlink(monkeypatch, mock_mavlink_connection):
    """Create mock pymavlink module for testing."""

    mock_master, mock_heartbeat_msg = mock_mavlink_connection

    mock_mavutil = MagicMock()
    mock_mavutil.mavlink_connection.return_value = mock_master
    mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

    mock_mavutil.mavlink_connection.return_value.wait_heartbeat.return_value = True

    import sys

    sys.modules["pymavlink"] = mock_mavutil
    sys.modules["pymavlink.mavutil"] = mock_mavutil

    return mock_mavutil, mock_master


@pytest.fixture
def mock_interfaces_msg():
    """Create mock interfaces module for testing."""

    mock_module = MagicMock()

    mock_ibn_result = MagicMock()
    mock_ibn_result.position_valid = True
    mock_ibn_result.position = [37.7749, -122.4194, 100.0]
    mock_ibn_result.position_accuracy = 1.5

    mock_module.IBNResult = mock_ibn_result

    return mock_module


@pytest.fixture
def sample_ibn_result():
    """Create sample IBNResult message for testing."""

    msg = MagicMock()
    msg.position_valid = True
    msg.position = [37.7749, -122.4194, 100.0]
    msg.position_accuracy = 1.5
    return msg


@pytest.fixture
def sample_global_position_msg():
    """Create sample GLOBAL_POSITION_INT MAVLink message for testing."""

    msg = MagicMock()
    msg.get_type.return_value = "GLOBAL_POSITION_INT"
    msg.time_boot_ms = 12345
    msg.lat = 377749000
    msg.lon = -1224194000
    msg.alt = 100000
    msg.relative_alt = 50000
    msg.vx = 100.5
    msg.vy = 200.7
    msg.vz = -10.3
    msg.hdg = 180.9
    return msg


@pytest.fixture
def sample_attitude_msg():
    """Create sample ATTITUDE MAVLink message for testing."""

    msg = MagicMock()
    msg.get_type.return_value = "ATTITUDE"
    msg.time_boot_ms = 12345
    msg.roll = 0.1
    msg.pitch = 0.2
    msg.yaw = 0.3
    msg.rollspeed = 0.01
    msg.pitchspeed = 0.02
    msg.yawspeed = 0.03
    return msg


@pytest.fixture
def valid_config():
    """Create valid config dict for testing."""

    return {
        "mavlink": {
            "connection_string": "/dev/ttyACM0",
            "baud_rate": 115200,
            "stream_rate_hz": 50,
        },
        "ros": {
            "global_position_topic": "/pixhawk/global_position",
            "attitude_topic": "/pixhawk/attitude",
            "init_position_topic": "/pixhawk/init_position",
            "publish_rate_hz": 10,
        },
    }


@pytest.fixture
def valid_gps_injection_config():
    """Create valid GPS injection config dict for testing."""

    return {
        "mavlink": {
            "connection_string": "/dev/ttyACM0",
            "baud_rate": 115200,
            "stream_rate_hz": 0,
        },
        "ros": {
            "ibn_result_topic": "/IBN/result",
            "inject_rate_hz": 10,
        },
    }
