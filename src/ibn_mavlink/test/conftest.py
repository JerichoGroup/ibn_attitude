"""Shared test fixtures (ROS2-safe + MAVLink-safe)."""

import sys
from unittest.mock import MagicMock

import pytest


# -----------------------------
# SAFE ROS / INTERFACES MOCK
# -----------------------------

mock_interfaces = MagicMock()
mock_interfaces.msg = MagicMock()

sys.modules["interfaces"] = mock_interfaces
sys.modules["interfaces.msg"] = mock_interfaces.msg


# -----------------------------
# MAVLINK FIXTURE
# -----------------------------


@pytest.fixture
def mock_mavlink_connection():
    """Mock pymavlink master connection."""

    mock_master = MagicMock()
    mock_master.target_system = 1
    mock_master.target_component = 1

    mock_master.wait_heartbeat.return_value = True
    mock_master.recv_match.return_value = None

    return mock_master


@pytest.fixture
def mock_pymavlink(monkeypatch, mock_mavlink_connection):
    """Mock pymavlink module."""

    mock_mavutil = MagicMock()
    mock_mavutil.mavlink_connection.return_value = mock_mavlink_connection
    mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

    sys.modules["pymavlink"] = mock_mavutil
    sys.modules["pymavlink.mavutil"] = mock_mavutil

    return mock_mavutil


# -----------------------------
# IBN RESULT MESSAGE FIXTURE
# -----------------------------


@pytest.fixture
def sample_ibn_result():
    """Valid IBNResult mock message."""

    msg = MagicMock()
    msg.position_valid = True
    msg.position = [37.7749, -122.4194, 100.0]
    msg.position_accuracy = 1.5
    return msg


# -----------------------------
# MAVLINK MESSAGES
# -----------------------------


@pytest.fixture
def sample_global_position_msg():
    """GLOBAL_POSITION_INT message."""

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
    """ATTITUDE message."""

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


# -----------------------------
# CONFIGS
# -----------------------------


@pytest.fixture
def valid_pixhawk_config():
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
        "log": {
            "file_path": "/tmp/test.log",
        },
    }


@pytest.fixture
def valid_gps_injection_config():
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
        "log": {
            "file_path": "/tmp/test.log",
        },
    }
