"""MAVLink client for Pixhawk communication."""

from dataclasses import dataclass
import logging
import threading
import time
from typing import Any, Dict, Optional

from pymavlink import mavutil

_logger = logging.getLogger("MAVLinkClient")
_logger.setLevel(logging.INFO)

if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    _logger.addHandler(_handler)


@dataclass
class GPSInputParams:
    """Parameters for GPS injection."""

    lat: float
    lon: float
    alt: float
    vn: float = 0.0
    ve: float = 0.0
    vd: float = 0.0
    satellites: int = 10
    hdop: float = 1.0


class MAVLinkClient:
    """
    Connects to Pixhawk and streams MAVLink messages.
    Stores only the latest message of each type.
    """

    def __init__(self, conn_str: str, baud: int, rate: int = 0, read_enabled: bool = True) -> None:
        """
        Initialize MAVLink connection. 
        """

        self._init_connection(conn_str, baud, rate, read_enabled)

    def _init_connection(self, conn_str: str, baud: int, rate: int, read_enabled: bool) -> None:
        """
        Initialize the MAVLink connection.

        Args:
            conn_str: MAVLink connection string (e.g., /dev/ttyACM0)
            baud: Serial baud rate
            rate: Data stream rate (0 to disable)
            read_enabled: Whether to start read loop (disable for write-only connections)

        """

        self._master = mavutil.mavlink_connection(conn_str, baud=baud)

        _logger.info("Waiting for heartbeat...")
        if not self._master.wait_heartbeat(timeout=10):
            raise RuntimeError("No heartbeat received")

        _logger.info("Connected to Pixhawk")

        if rate > 0:
            self._master.mav.request_data_stream_send(
                self._master.target_system,
                self._master.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                rate,
                1,
            )

        self._latest: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._running = read_enabled

        if read_enabled:
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()


    def _read_loop(self) -> None:
        """Read messages in background thread."""

        while self._running:
            msg = self._master.recv_match(blocking=True, timeout=1)
            if msg is None:
                continue

            msg_type = msg.get_type()

            with self._lock:
                self._latest[msg_type] = msg


    def get_latest(self, msg_type: str) -> Optional[object]:
        """Get latest message of given type."""

        with self._lock:
            return self._latest.get(msg_type)


    def stop(self) -> None:
        """Stop the client."""

        self._running = False
        if hasattr(self, "_thread"):
            self._thread.join(timeout=2)


    def send_gps_input(self, params: GPSInputParams) -> None:
        """Send GPS_INPUT message to Pixhawk."""

        lat_int = int(params.lat * 1e7)
        lon_int = int(params.lon * 1e7)

        time_us = int(time.time() * 1e6)

        self._master.mav.gps_input_send(
            time_us,
            0,                      # gps_id
            0,                      # ignore_flags
            0,                      # time_week_ms
            0,                      # time_week
            3,                      # fix_type (3D)
            lat_int,
            lon_int,
            params.alt,             # meters
            params.hdop,            # hdop
            params.hdop,            # vdop
            params.vn,              # m/s
            params.ve,
            params.vd,
            0.1,                    # speed_accuracy
            params.hdop,            # horiz_accuracy
            params.hdop,            # vert_accuracy
            params.satellites,
            0,                      # yaw unavailable
        )
    