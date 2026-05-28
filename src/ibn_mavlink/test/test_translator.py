"""Tests for MavlinkTranslator."""

from unittest.mock import MagicMock
from builtin_interfaces.msg import Time

from ibn_mavlink.pixhawk_bridge.translator import MavlinkTranslator


class TestMavlinkTranslator:
    """Tests for MAVLink to ROS translation."""

    def test_to_global_position(self) -> None:
        """Test GLOBAL_POSITION_INT translation."""

        node = MagicMock()

        stamp = Time(sec=123, nanosec=456)
        clock = MagicMock()
        now = MagicMock()

        node.get_clock.return_value = clock
        clock.now.return_value = now
        now.to_msg.return_value = stamp

        msg = MagicMock()
        msg.time_boot_ms = 1000
        msg.lat = 377749000
        msg.lon = -1224194000
        msg.alt = 100000
        msg.relative_alt = 50000
        msg.vx = 10.7
        msg.vy = 20.2
        msg.vz = -5.9
        msg.hdg = 180.9

        ros_msg = MavlinkTranslator.to_global_position(node, msg)

        assert ros_msg.header.stamp == stamp
        assert ros_msg.time_boot_ms == 1000
        assert ros_msg.lat == 377749000
        assert ros_msg.lon == -1224194000

        assert ros_msg.msl_altitude == 100000
        assert ros_msg.relative_altitude == 50000

        assert ros_msg.vx == 10
        assert ros_msg.vy == 20
        assert ros_msg.vz == -5

        assert ros_msg.vehicle_heading_angle == 180


    def test_to_attitude(self) -> None:
        """Test ATTITUDE translation."""

        node = MagicMock()

        stamp = Time(sec=111, nanosec=222)

        clock = MagicMock()
        now = MagicMock()

        node.get_clock.return_value = clock
        clock.now.return_value = now
        now.to_msg.return_value = stamp

        msg = MagicMock()
        msg.time_boot_ms = 2000
        msg.roll = 0.1
        msg.pitch = 0.2
        msg.yaw = 0.3
        msg.rollspeed = 0.01
        msg.pitchspeed = 0.02
        msg.yawspeed = 0.03

        ros_msg = MavlinkTranslator.to_attitude(node, msg)

        assert ros_msg.header.stamp == stamp
        assert ros_msg.time_boot_ms == 2000

        assert abs(ros_msg.roll - 0.1) < 1e-6
        assert abs(ros_msg.pitch - 0.2) < 1e-6
        assert abs(ros_msg.yaw - 0.3) < 1e-6

        assert abs(ros_msg.rollspeed - 0.01) < 1e-6
        assert abs(ros_msg.pitchspeed - 0.02) < 1e-6
        assert abs(ros_msg.yawspeed - 0.03) < 1e-6
