"""ROS2 node for GPS injection."""

import logging
from logging import StreamHandler
from pathlib import Path
from typing import Any, Dict, Optional

from ament_index_python import get_package_share_directory
from interfaces.msg import IBNResult
import rclpy
from rclpy.node import Node
import yaml

from ibn_mavlink.gps_injection.converter import IbnToGPSConverter
from ibn_mavlink.gps_injection.sender import GPSLogger

_logger = logging.getLogger("GPSInjection")
_logger.setLevel(logging.INFO)

if not _logger.handlers:
    _handler = StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    _logger.addHandler(_handler)


def load_config(path: Path) -> dict:
    """Load config from YAML file."""

    with path.open("r") as f:
        return yaml.safe_load(f)


class GPSInjectionNode(Node):
    """Logs GPS position from IBN result."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize node."""

        super().__init__("gps_injection_node")

        ros = config["ros"]
        log = config["log"]

        self._logger = GPSLogger(log["file_path"])
        self._subscription = self.create_subscription(
            IBNResult,
            ros["ibn_result_topic"],
            self._callback,
            10,
        )

        _logger.info("GPS Injection Node initialized")

    def _callback(self, msg: IBNResult) -> None:
        """Handle incoming IbnResult."""

        gps_payload = IbnToGPSConverter.convert(msg)

        if gps_payload is None:
            self.get_logger().warn("Invalid position, skipping")
            return

        self._logger.log(gps_payload.to_json())

        _logger.info(f"Logged GPS lat={gps_payload.lat:.7f}, " f"lon={gps_payload.lon:.7f}, alt={gps_payload.alt:.2f}")


def main(args: Optional[list] = None) -> None:
    """Entry point."""

    rclpy.init(args=args)

    config_dir = get_package_share_directory("ibn_mavlink")
    config_path = Path(config_dir) / "config" / "gps_injection.yaml"
    config = load_config(config_path)

    node = GPSInjectionNode(config)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
