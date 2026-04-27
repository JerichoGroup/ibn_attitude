# ============ Imports ============ #
import logging
from pathlib import Path
import yaml

import rclpy
from rclpy.node import Node

from interfaces.msg import GlobalPositionInt, Attitude

from mavlink.client import MAVLinkClient
from mavlink.translator import MavlinkTranslator



# ========= Config Loader ========= #
def load_config(path: Path) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ========= Logger Setup ========== #
logger = logging.getLogger("PixhawkTelemetry")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# ============= ROS Node ============= #
class PixhawkTelemetry(Node):
    """
    ROS2 node that reads telemetry from Pixhawk via MAVLink and publishes it as ROS messages.
    Publishes both the current global position and attitude, as well as the initial position at startup.
    """

    def __init__(self, config: dict):
        super().__init__("pixhawk_telemetry_node")

        mav = config["mavlink"]
        ros = config["ros"]
        topics = ros["topics"]

        self._pub_global = self.create_publisher(
            GlobalPositionInt, topics["global_position"], 10
        )
        self._pub_attitude = self.create_publisher(
            Attitude, topics["attitude"], 10
        )
        self._pub_init = self.create_publisher(
            GlobalPositionInt, topics["init_position"], 10
        )

        self._client = MAVLinkClient(
            mav["connection_string"],
            mav["baud_rate"],
            mav["stream_rate_hz"]
        )

        self._init_position = None

        publish_hz = ros["publish_rate_hz"]
        self.create_timer(1.0 / publish_hz, self._tick)


    def _tick(self):
        gp = self._client.get_latest("GLOBAL_POSITION_INT")
        at = self._client.get_latest("ATTITUDE")

        if gp:
            self._handle_global_position(gp)

        if at:
            ros_msg = MavlinkTranslator.to_attitude(self, at)
            self._pub_attitude.publish(ros_msg)

        self._publish_init_position()


    def _handle_global_position(self, msg):
        ros_msg = MavlinkTranslator.to_global_position(self, msg)

        if self._init_position is None:
            self._init_position = ros_msg

        self._pub_global.publish(ros_msg)


    def _publish_init_position(self):
        if self._init_position:
            self._pub_init.publish(self._init_position)


# ============ main ============== #
def main(args=None):
    rclpy.init(args=args)

    config = load_config(
        Path(__file__).resolve().parent.parent / "config.yml"
    )

    node = PixhawkTelemetry(config)

    try:
        rclpy.spin(node)
    finally:
        node._client.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()