"""ROS2 node for Pixhawk telemetry bridge."""

from pathlib import Path
from typing import Any, Dict, Optional

from ament_index_python import get_package_share_directory
from interfaces.msg import Attitude, GlobalPositionInt
import rclpy
from rclpy.node import Node
import yaml  # type: ignore[import-untyped]

from ibn_mavlink.mavlink.client import MAVLinkClient
from ibn_mavlink.pixhawk_bridge.translator import GlobalPositionMessage, MavlinkTranslator
from ibn_mavlink.utils.logger_setup import setup_logger


def load_config(path: Path) -> dict:
    with path.open("r") as config_file:
        return yaml.safe_load(config_file)


def ensure_ros_initialized() -> None:
    if not rclpy.ok():
        rclpy.init()


class PixhawkTelemetry(Node):
    """Bridge between Pixhawk MAVLink and ROS2."""

    def __init__(self, config: Dict[str, Any]) -> None:
        ensure_ros_initialized()

        super().__init__("pixhawk_bridge_node")

        mavlink_config = config["mavlink"]
        ros_config = config["ros"]

        self.log_file = config["log"]["file_path"]
        self._logger = setup_logger("PixhawkTelemetry", self.log_file)

        self._pub_global = self.create_publisher(
            GlobalPositionInt, ros_config["global_position_topic"], 10
        )
        self._pub_attitude = self.create_publisher(
            Attitude, ros_config["attitude_topic"], 10
        )
        self._pub_init = self.create_publisher(
            GlobalPositionInt, ros_config["init_position_topic"], 10
        )

        self._client = MAVLinkClient(
            mavlink_config["connection_string"],
            mavlink_config["baud_rate"],
            mavlink_config["stream_rate_hz"],
            read_enabled=True,
            logger=self._logger,
        )

        self._init_position: Optional[GlobalPositionInt] = None

        publish_hz = ros_config["publish_rate_hz"]
        self.create_timer(1.0 / publish_hz, self._tick)

        self._logger.info("Pixhawk Telemetry Node initialized")
        self._logger.info(
            f"Connecting to {mavlink_config['connection_string']} at {mavlink_config['baud_rate']} baud"
        )


    def _tick(self) -> None:
        """Publish telemetry on timer."""

        global_position_msg = self._client.get_latest("GLOBAL_POSITION_INT")
        attitude_msg = self._client.get_latest("ATTITUDE")

        if attitude_msg:
            ros_msg = MavlinkTranslator.to_attitude(self, attitude_msg)  # type: ignore[arg-type]
            self._pub_attitude.publish(ros_msg)

        if global_position_msg:
            self._handle_global_position(global_position_msg)  # type: ignore[arg-type]
            self._publish_init_position()


    def _handle_global_position(self, msg: GlobalPositionMessage) -> None:
        """Handle global position message."""

        ros_msg = MavlinkTranslator.to_global_position(self, msg)

        if self._init_position is None:
            self._init_position = ros_msg
            self._logger.info("First global position received (init set)")

        self._pub_global.publish(ros_msg)


    def _publish_init_position(self) -> None:
        """Publish initial position if not already published."""
        
        if self._init_position is not None:
            self._pub_init.publish(self._init_position)


    def destroy_node(self) -> None:
        """
        Cleanly shut down external resources owned by the node.
        Ensures MAVLink client is stopped before the ROS2 node is destroyed.
        """
        
        if getattr(self, "_client", None) is not None:
            self._client.stop()
            self._client = None

        super().destroy_node()


def main() -> None:
    """Entry point."""

    ensure_ros_initialized()

    config_dir = get_package_share_directory("ibn_mavlink")
    config_path = Path(config_dir) / "config" / "pixhawk_bridge.yaml"
    config = load_config(config_path)

    node = PixhawkTelemetry(config)

    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
