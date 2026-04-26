# ============ Imports ============ #
import logging

import rclpy
from rclpy.node import Node
from std_msgs.msg import Header

from pymavlink import mavutil
from interfaces.msg import GlobalPositionInt, Attitude


# ========= Logger Setup ========== #
logger = logging.getLogger("PixhawkTelemetry")
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


# ========= MAVLink Client ========= #
class MAVLinkClient:
    """Handles connection + receiving MAVLink messages"""

    def __init__(self, connection_str: str):
        self._master = mavutil.mavlink_connection(
            connection_str,
            baud=115200
        )

        logger.info("Waiting for heartbeat...")
        hb = self._master.wait_heartbeat(timeout=10)
        if not hb:
            raise RuntimeError("No heartbeat received")

        logger.info("Connected to Pixhawk")

        self._request_streams()

    def _request_streams(self):
        try:
            self._master.mav.request_data_stream_send(
                self._master.target_system,
                self._master.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                50,
                1
            )
        except Exception as e:
            logger.warning(f"Stream request failed: {e}")

    def receive_all(self):
        while True:
            msg = self._master.recv_match(blocking=False)
            if msg is None:
                break
            yield msg


# ======== Translator Layer ======== #
class MavlinkTranslator:
    """Converts MAVLink → ROS messages"""

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
    """Orchestrates MAVLink → ROS publishing"""

    def __init__(self):
        super().__init__("pixhawk_telemetry_node")

        self._pub_global = self.create_publisher(
            GlobalPositionInt, "/pixhawk/global_position", 10
        )
        self._pub_attitude = self.create_publisher(
            Attitude, "/pixhawk/attitude", 10
        )

        self._client = MAVLinkClient("/dev/ttyACM0")

        self.create_timer(0.01, self._tick)

    def _tick(self):
        for msg in self._client.receive_all():
            mtype = msg.get_type()

            if mtype == "GLOBAL_POSITION_INT":
                ros_msg = MavlinkTranslator.to_global_position(self, msg)
                self._pub_global.publish(ros_msg)

            elif mtype == "ATTITUDE":
                ros_msg = MavlinkTranslator.to_attitude(self, msg)
                self._pub_attitude.publish(ros_msg)


# ============ main ============== #
def main(args=None):
    rclpy.init(args=args)

    node = PixhawkTelemetry()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()