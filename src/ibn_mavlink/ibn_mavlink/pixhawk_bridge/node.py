"""ROS2 node for Pixhawk telemetry bridge."""
import logging
from logging import StreamHandler
from pathlib import Path

import rclpy
import yaml
from ament_index_python import get_package_share_directory
from rclpy.node import Node

from interfaces.msg import GlobalPositionInt, Attitude

from ibn_mavlink.pixhawk_bridge.client import MAVLinkClient
from ibn_mavlink.pixhawk_bridge.translator import MavlinkTranslator


_logger = logging.getLogger("PixhawkTelemetry")
_logger.setLevel(logging.INFO)

if not _logger.handlers:
    _handler = StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    _logger.addHandler(_handler)


def load_config(path: Path) -> dict:
    """Load config from YAML file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


class PixhawkTelemetry(Node):
    """Bridge between Pixhawk MAVLink and ROS2."""

    def __init__(self, config: dict):
        """Initialize node."""
        super().__init__("pixhawk_bridge_node")

        mav = config["mavlink"]
        ros = config["ros"]

        self._pub_global = self.create_publisher(GlobalPositionInt, ros["global_position_topic"], 10)
        self._pub_attitude = self.create_publisher(Attitude, ros["attitude_topic"], 10)
        self._pub_init = self.create_publisher(GlobalPositionInt, ros["init_position_topic"], 10)

        self._client = MAVLinkClient(
            mav["connection_string"],
            mav["baud_rate"],
            mav["stream_rate_hz"]
        )

        self._init_position = None

        publish_hz = ros["publish_rate_hz"]
        self.create_timer(1.0 / publish_hz, self._tick)

    def _tick(self):
        """Publish telemetry on timer."""
        gp = self._client.get_latest("GLOBAL_POSITION_INT")
        at = self._client.get_latest("ATTITUDE")

        if gp:
            self._handle_global_position(gp)

        if at:
            ros_msg = MavlinkTranslator.to_attitude(self, at)
            self._pub_attitude.publish(ros_msg)

        self._publish_init_position()

    def _handle_global_position(self, msg):
        """Handle global position message."""
        ros_msg = MavlinkTranslator.to_global_position(self, msg)

        if self._init_position is None:
            self._init_position = ros_msg

        self._pub_global.publish(ros_msg)

    def _publish_init_position(self):
        """Publish initial position once."""
        if self._init_position:
            self._pub_init.publish(self._init_position)


def main(args=None):
    """Entry point."""
    rclpy.init(args=args)

    config_dir = get_package_share_directory('ibn_mavlink')
    config_path = Path(config_dir) / 'config' / 'pixhawk_bridge.yaml'
    config = load_config(config_path)

    node = PixhawkTelemetry(config)

    try:
        rclpy.spin(node)
    finally:
        node._client.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()