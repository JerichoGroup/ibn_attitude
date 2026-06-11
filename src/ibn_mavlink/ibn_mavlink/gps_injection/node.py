"""ROS2 node for GPS injection back to Pixhawk."""

from pathlib import Path
from typing import Any, Dict, Optional

from ament_index_python import get_package_share_directory
from interfaces.msg import IBNResult
import rclpy
from rclpy.node import Node
import yaml  # type: ignore[import-untyped]

from ibn_mavlink.gps_injection.converter import GPSInputPayload, IBNToGPSConverter
from ibn_mavlink.mavlink.client import GPSInputParams, MAVLinkClient
from ibn_mavlink.utils.logger_setup import setup_logger


def load_config(path: Path) -> dict:
    """Load and parse a YAML config file."""

    with path.open("r") as config_file:
        return yaml.safe_load(config_file)


def ensure_ros_initialized() -> None:
    """Initialize rclpy if it has not been initialized yet."""

    if not rclpy.ok():
        rclpy.init()


class GPSInjectionNode(Node):
    """Injects computed GPS position back to Pixhawk."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Set up the MAVLink client, IBNResult subscription, and injection timer."""

        ensure_ros_initialized()

        super().__init__("gps_injection_node")

        mavlink_config = config["mavlink"]
        ros = config["ros"]

        self.log_file = config["log"]["file_path"]
        self._logger = setup_logger("GPSInjection", self.log_file)

        self._client: Optional[MAVLinkClient] = MAVLinkClient(
            mavlink_config["connection_string"],
            mavlink_config["baud_rate"],
            mavlink_config["stream_rate_hz"],
            read_enabled=False,
            logger=self._logger,
        )

        try:
            self._subscription = self.create_subscription(
                IBNResult,
                ros["ibn_result_topic"],
                self._callback,
                10,
            )
        except Exception:
            self._subscription = None

        self._inject_rate_hz = ros.get("inject_rate_hz", 10)
        self._inject_timer = self.create_timer(1.0 / self._inject_rate_hz, self._inject_loop)

        self._latest_payload: Optional[GPSInputPayload] = None

        self._logger.info("GPS Injection Node initialized")
        self._logger.info(f"Connecting to {mavlink_config['connection_string']} at {mavlink_config['baud_rate']} baud")

    def _callback(self, msg: IBNResult) -> None:
        """Store latest IBNResult for injection."""

        gps_payload = IBNToGPSConverter.convert(msg)

        if gps_payload is None:
            self._latest_payload = None
            self._logger.warning("Invalid position, skipping")
            return

        self._latest_payload = gps_payload
        self._logger.info(
            f"Received GPS lat={gps_payload.lat:.7f}, " f"lon={gps_payload.lon:.7f}, alt={gps_payload.alt:.2f}"
        )

    def _inject_loop(self) -> None:
        """Send GPS to Pixhawk on timer."""

        if self._latest_payload is None or self._client is None:
            return

        payload = self._latest_payload

        try:
            params = GPSInputParams(
                lat=payload.lat,
                lon=payload.lon,
                alt=payload.alt,
                vn=0.0,
                ve=0.0,
                vd=0.0,
                satellites=payload.satellites_visible,
                hdop=payload.horiz_accuracy,
            )
            self._client.send_gps_input(params)

        except Exception as e:
            self._logger.error(f"Failed to inject GPS: {e}")

    def destroy_node(self) -> None:
        """
        Shut down external resources owned by the node.

        Ensures the MAVLink client is stopped before the ROS2 node is destroyed.
        """

        if self._client is not None:
            self._client.stop()
            self._client = None

        super().destroy_node()


def main(args: Optional[list] = None) -> None:
    """Entry point."""

    ensure_ros_initialized()

    config_dir = get_package_share_directory("ibn_mavlink")
    config_path = Path(config_dir) / "config" / "gps_injection.yaml"
    config = load_config(config_path)

    node = GPSInjectionNode(config)
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
