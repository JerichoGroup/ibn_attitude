"""MAVLink client for Pixhawk communication."""

from dataclasses import dataclass
import logging
import threading
import time
from typing import Any, Dict, Optional

from pymavlink import mavutil

IGNORE_VEL_XY = 1 << 3
IGNORE_VEL_Z = 1 << 4


@dataclass
class GPSInputParams:
    """Parameters for a MAVLink GPS_INPUT message."""

    lat: float
    lon: float
    alt: float
    vn: float = 0.0
    ve: float = 0.0
    vd: float = 0.0
    satellites: int = 10
    hdop: float = 1.0


class MAVLinkClient:
    """MAVLink client for Pixhawk communication."""

    def __init__(  # noqa: PLR0913 - all connection parameters are required at construction
        self,
        conn_str: str,
        baud: int,
        rate: int = 0,
        read_enabled: bool = True,
        logger: Optional[logging.Logger] = None,
        recv_timeout: float = 0.05,
    ) -> None:
        """Open a MAVLink connection and, if reading is enabled, start the read thread."""

        self._logger = logger or logging.getLogger("MAVLinkClient")

        self._conn_str = conn_str
        self._baud = baud
        self._rate = rate
        self._recv_timeout = recv_timeout

        self._latest: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._conn_lock = threading.Lock()
        self._reconnect_lock = threading.Lock()

        self._running = True
        self._read_enabled = read_enabled

        self._master: Optional[mavutil.mavlink_connection] = None

        self._connect()

        self._thread = None
        if self._read_enabled:
            self._thread = threading.Thread(
                target=self._read_loop,
                daemon=True,
            )
            self._thread.start()

    def _connect(self) -> None:
        """Establish MAVLink connection."""

        self._logger.info(f"Connecting to {self._conn_str}")

        master = mavutil.mavlink_connection(
            self._conn_str,
            baud=self._baud,
        )

        self._logger.info("Waiting for heartbeat...")

        hb = master.wait_heartbeat(timeout=10)

        if not hb:
            try:
                master.close()
            except Exception:
                pass
            raise RuntimeError("No heartbeat received")

        self._master = master

        self._logger.info("Connected to Pixhawk")

        self._request_streams()

    def _request_streams(self) -> None:
        """Request MAVLink data streams at specified rate."""

        if self._rate <= 0:
            return

        with self._conn_lock:
            if self._master is None:
                return

            master = self._master

            master.mav.request_data_stream_send(
                master.target_system,
                master.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                self._rate,
                1,
            )

    def _read_loop(self) -> None:
        """Continuously read MAVLink messages."""

        while self._running and self._read_enabled:
            try:
                with self._conn_lock:
                    master = self._master

                if master is None:
                    time.sleep(0.1)
                    continue

                msg = master.recv_match(blocking=False)

                if msg is None:
                    time.sleep(self._recv_timeout)
                    continue

                with self._lock:
                    self._latest[msg.get_type()] = msg

            except Exception as e:
                self._logger.error(f"MAVLink read error: {e}")
                self._reconnect()
                time.sleep(0.5)

    def _disconnect(self) -> None:
        """Close existing MAVLink connection safely."""

        with self._conn_lock:
            old = self._master
            self._master = None

        if old:
            try:
                old.close()
            except Exception:
                pass

    def _attempt_connect(self) -> bool:
        """Try a single reconnect attempt."""

        try:
            self._connect()
            return True

        except Exception as e:
            self._logger.error(f"Reconnect attempt failed: {e}")
            return False

    def _reconnect(self) -> None:
        """Reconnect loop with backoff."""

        if not self._reconnect_lock.acquire(blocking=False):
            return

        try:
            while self._running:
                self._logger.warning("MAVLink reconnecting...")

                self._disconnect()
                time.sleep(1.0)

                if self._attempt_connect():
                    self._logger.info("Reconnect successful")
                    return

                time.sleep(2.0)
        finally:
            self._reconnect_lock.release()

    def get_latest(self, msg_type: str) -> Optional[Any]:  # noqa: ANN401 - pymavlink messages are dynamically typed and unstubbed
        """Get latest message of specified type."""

        with self._lock:
            return self._latest.get(msg_type)

    def stop(self) -> None:
        """Stop the client and clean up resources."""

        self._running = False

        self._disconnect()

        if self._thread is not None:
            self._thread.join(timeout=2)

    def send_gps_input(self, params: GPSInputParams) -> None:
        """Send GPS_INPUT message to Pixhawk."""

        lat_int = int(params.lat * 1e7)
        lon_int = int(params.lon * 1e7)

        time_us = int(time.time() * 1e6)

        # velocity intentionally unused because EKF ignores it
        ignore_flags = IGNORE_VEL_XY | IGNORE_VEL_Z

        with self._conn_lock:
            master = self._master

            if master is None:
                self._logger.warning("GPS send skipped (no connection)")
                return

            master.mav.gps_input_send(
                time_us,
                0,  # gps_id
                ignore_flags,  # ignore flags - we only provide position
                0,  # time_week_ms
                0,  # time_week
                3,  # fix_type (3D)
                lat_int,
                lon_int,
                params.alt,  # meters
                params.hdop,  # hdop
                params.hdop,  # vdop
                params.vn,  # m/s
                params.ve,
                params.vd,
                0.1,  # speed_accuracy
                params.hdop,  # horiz_accuracy
                params.hdop,  # vert_accuracy
                params.satellites,
                0,  # yaw unavailable
            )
