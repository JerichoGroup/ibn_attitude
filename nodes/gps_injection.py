import json
import socket
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import rclpy
from rclpy.node import Node



from your_msgs.msg import IbnResult   # e.g. from my_pkg.msg import IbnResult


# ========== Data Model ========== #

@dataclass
class GPSInputPayload:
    lat: float
    lon: float
    alt: float
    horiz_accuracy: float
    vert_accuracy: float
    fix_type: int = 3
    satellites_visible: int = 10

    def to_json(self) -> Dict:
        return {
            "time_usec": int(time.time() * 1e6),
            "gps_id": 0,
            "ignore_flags": 0,
            "time_week_ms": 0,
            "time_week": 0,
            "fix_type": self.fix_type,
            "lat": int(self.lat * 1e7),
            "lon": int(self.lon * 1e7),
            "alt": float(self.alt),
            "hdop": self.horiz_accuracy,
            "vdop": self.vert_accuracy,
            "vn": 0.0,
            "ve": 0.0,
            "vd": 0.0,
            "speed_accuracy": 0.1,
            "horiz_accuracy": self.horiz_accuracy,
            "vert_accuracy": self.vert_accuracy,
            "satellites_visible": self.satellites_visible,
        }


# ======== Converter SRP ========= #

class IbnToGPSConverter:
    @staticmethod
    def extract_position(msg: IbnResult) -> Optional[Tuple[float, float, float]]:
        if not msg.position_valid:
            return None
        if len(msg.position) != 3:
            return None
        return msg.position[0], msg.position[1], msg.position[2]

    @staticmethod
    def convert(msg: IbnResult) -> Optional[GPSInputPayload]:
        pos = IbnToGPSConverter.extract_position(msg)
        if pos is None:
            return None

        lat, lon, alt = pos

        return GPSInputPayload(
            lat=lat,
            lon=lon,
            alt=alt,
            horiz_accuracy=msg.position_accuracy,
            vert_accuracy=msg.position_accuracy,
        )


# ======== UDP Sender SRP ======== #
class GPSSender:
    def __init__(self, ip: str = "127.0.0.1", port: int = 25100) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._addr = (ip, port)

    def send(self, payload: Dict) -> None:
        data = json.dumps(payload).encode()
        self._sock.sendto(data, self._addr)


# ========= ROS2 Node SRP ========= #

class GPSInjectionNode(Node):
    def __init__(self) -> None:
        super().__init__("gps_injection_node")

        self._sender = GPSSender()
        self._subscription = self.create_subscription(
            IbnResult,
            "/IBN/result",
            self._callback,
            10,
        )

        self.get_logger().info("GPS Injection Node initialized")

    def _callback(self, msg: IbnResult) -> None:
        gps_payload = IbnToGPSConverter.convert(msg)

        if gps_payload is None:
            self.get_logger().warn("Invalid or unavailable position in ibn_result, skipping")
            return

        self._sender.send(gps_payload.to_json())

        self.get_logger().info(
            f"Injected GPS lat={gps_payload.lat:.7f}, "
            f"lon={gps_payload.lon:.7f}, alt={gps_payload.alt:.2f}, "
            f"acc={gps_payload.horiz_accuracy:.2f}"
        )


# ============ main ============== #

def main(args=None) -> None:
    rclpy.init(args=args)
    node = GPSInjectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
