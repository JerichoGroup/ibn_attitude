# ============ Imports ============ #
import logging
import threading
from pathlib import Path
import yaml

import rclpy
from rclpy.node import Node
from std_msgs.msg import Header

from pymavlink import mavutil
from interfaces.msg import GlobalPositionInt, Attitude


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


# ========= MAVLink Client ========= #
class MAVLinkClient:
    """
    Continuous MAVLink reader (threaded).
    Stores ONLY latest message per type.
    """

    def __init__(self, connection_string: str, baud_rate: int, stream_rate_hz: int):
        self._master = mavutil.mavlink_connection(
            connection_string,
            baud=baud_rate
        )

        logger.info("Waiting for heartbeat...")
        if not self._master.wait_heartbeat(timeout=10):
            raise RuntimeError("No heartbeat received")

        logger.info("Connected to Pixhawk")

        self._master.mav.request_data_stream_send(
            self._master.target_system,
            self._master.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL,
            stream_rate_hz,
            1
        )

        self._latest = {}
        self._running = True

        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _read_loop(self):
        while self._running:
            msg = self._master.recv_match(blocking=True, timeout=1)
            if msg is None:
                continue

            self._latest[msg.get_type()] = msg

    def get_latest(self, msg_type: str):
        return self._latest.get(msg_type)

    def stop(self):
        self._running = False


# ======== Translator Layer ======== #
class MavlinkTranslator:

    @staticmethod
    def header(node: Node) -> Header:
        h = Header()
        h.stamp = node.get_clock().now().to_msg()
        return h

    @staticmethod
    def to_global_position(node: Node, msg) -> GlobalPositionInt:
        ros_msg = GlobalPositionInt()
        ros_msg.header = MavlinkTranslator.header(node)

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
    def to_attitude(node: Node, msg) -> Attitude:
        ros_msg = Attitude()
        ros_msg.header = MavlinkTranslator.header(node)

        ros_msg.time_boot_ms = msg.time_boot_ms
        ros_msg.roll = msg.roll
        ros_msg.pitch = msg.pitch
        ros_msg.yaw = msg.yaw

        ros_msg.rollspeed = msg.rollspeed
        ros_msg.pitchspeed = msg.pitchspeed
        ros_msg.yawspeed = msg.yawspeed

        return ros_msg


# ============= ROS Node ============= #
class PixhawkTelemetry(Node):

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