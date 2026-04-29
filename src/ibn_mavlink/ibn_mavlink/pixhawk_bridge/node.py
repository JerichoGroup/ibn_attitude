"""ROS2 node for Pixhawk telemetry bridge."""

import logging
from logging import StreamHandler
from pathlib import Path
from typing import Any, Dict

from ament_index_python import get_package_share_directory
from interfaces.msg import Attitude, GlobalPositionInt
import rclpy
from rclpy.node import Node
import yaml

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

    with path.open("r") as f:
        return yaml.safe_load(f)


class PixhawkTelemetry(Node):
    """Bridge between Pixhawk MAVLink and ROS2."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize node."""

        super().__init__("pixhawk_bridge_node")

        mavlink_config = config["mavlink"]
        ros_config = config["ros"]

        self._pub_global = self.create_publisher(GlobalPositionInt, ros_config["global_position_topic"], 10)
        self._pub_attitude = self.create_publisher(Attitude, ros_config["attitude_topic"], 10)
        self._pub_init = self.create_publisher(GlobalPositionInt, ros_config["init_position_topic"], 10)

        self._client = MAVLinkClient(
            mavlink_config["connection_string"], mavlink_config["baud_rate"], mavlink_config["stream_rate_hz"]
        )

        self._init_position = None

        publish_hz = ros_config["publish_rate_hz"]
        self.create_timer(1.0 / publish_hz, self._tick)

    def _tick(self) -> None:
        """Publish telemetry on timer."""

        global_position_msg = self._client.get_latest("GLOBAL_POSITION_INT")
        attitude_msg = self._client.get_latest("ATTITUDE")

        if global_position_msg:
            self._handle_global_position(global_position_msg)

        if attitude_msg:
            ros_msg = MavlinkTranslator.to_attitude(self, attitude_msg)
            self._pub_attitude.publish(ros_msg)

        self._publish_init_position()

    def _handle_global_position(self, msg: Any) -> None:
        """Handle global position message."""

        ros_msg = MavlinkTranslator.to_global_position(self, msg)

        if self._init_position is None:
            self._init_position = ros_msg

        self._pub_global.publish(ros_msg)

    def _publish_init_position(self) -> None:
        """Publish initial position once."""

        if self._init_position:
            self._pub_init.publish(self._init_position)


def main() -> None:
    """Entry point."""

    rclpy.init(args=None)

    config_dir = get_package_share_directory("ibn_mavlink")
    config_path = Path(config_dir) / "config" / "pixhawk_bridge.yaml"
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
