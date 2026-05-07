"""Translates MAVLink messages to ROS2 messages."""

from __future__ import annotations

from typing import Protocol

from interfaces.msg import Attitude, GlobalPositionInt
from rclpy.node import Node
from std_msgs.msg import Header


class GlobalPositionMessage(Protocol):
    """Protocol for GLOBAL_POSITION_INT MAVLink message."""

    time_boot_ms: int
    lat: int
    lon: int
    alt: int
    relative_alt: int
    vx: float
    vy: float
    vz: float
    hdg: float


class AttitudeMessage(Protocol):
    """Protocol for ATTITUDE MAVLink message."""

    time_boot_ms: int
    roll: float
    pitch: float
    yaw: float
    rollspeed: float
    pitchspeed: float
    yawspeed: float


class MavlinkTranslator:
    """Translates MAVLink messages to ROS2 messages."""

    @staticmethod
    def _header(node: Node) -> Header:
        """Create header with timestamp."""

        h = Header()
        h.stamp = node.get_clock().now().to_msg()
        return h

    @staticmethod
    def to_global_position(node: Node, msg: GlobalPositionMessage) -> GlobalPositionInt:
        """Translate GLOBAL_POSITION_INT to ROS."""

        ros_msg = GlobalPositionInt()
        ros_msg.header = MavlinkTranslator._header(node)

        ros_msg.time_boot_ms = msg.time_boot_ms
        ros_msg.lat = msg.lat
        ros_msg.lon = msg.lon
        ros_msg.msl_altitude = msg.alt
        ros_msg.relative_altitude = msg.relative_alt

        ros_msg.vx = int(msg.vx)
        ros_msg.vy = int(msg.vy)
        ros_msg.vz = int(msg.vz)
        ros_msg.vehicle_heading_angle = int(msg.hdg)

        return ros_msg

    @staticmethod
    def to_attitude(node: Node, msg: AttitudeMessage) -> Attitude:
        """Translate ATTITUDE to ROS."""

        ros_msg = Attitude()
        ros_msg.header = MavlinkTranslator._header(node)

        ros_msg.time_boot_ms = msg.time_boot_ms
        ros_msg.roll = msg.roll
        ros_msg.pitch = msg.pitch
        ros_msg.yaw = msg.yaw

        ros_msg.rollspeed = msg.rollspeed
        ros_msg.pitchspeed = msg.pitchspeed
        ros_msg.yawspeed = msg.yawspeed

        return ros_msg
