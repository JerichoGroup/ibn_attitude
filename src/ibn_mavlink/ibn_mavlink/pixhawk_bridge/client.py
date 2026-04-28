"""MAVLink client for Pixhawk communication."""
import logging
import threading

from pymavlink import mavutil


_logger = logging.getLogger("MAVLinkClient")
_logger.setLevel(logging.INFO)

if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    _logger.addHandler(_handler)


class MAVLinkClient:
    """Connects to Pixhawk and streams MAVLink messages."""

    def __init__(self, connection_string: str, baud_rate: int, stream_rate_hz: int):
        """Initialize MAVLink connection."""
        self._master = mavutil.mavlink_connection(connection_string, baud=baud_rate)

        _logger.info("Waiting for heartbeat...")
        if not self._master.wait_heartbeat(timeout=10):
            raise RuntimeError("No heartbeat received")

        _logger.info("Connected to Pixhawk")

        self._master.mav.request_data_stream_send(
            self._master.target_system,
            self._master.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL,
            stream_rate_hz,
            1
        )

        self._latest = {}
        self._lock = threading.Lock()
        self._running = True

        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _read_loop(self):
        """Read messages in background thread."""
        while self._running:
            msg = self._master.recv_match(blocking=True, timeout=1)
            if msg is None:
                continue

            msg_type = msg.get_type()

            with self._lock:
                self._latest[msg_type] = msg

    def get_latest(self, msg_type: str):
        """Get latest message of given type."""
        with self._lock:
            return self._latest.get(msg_type)

    def stop(self):
        """Stop the client."""
        self._running = False
        self._thread.join(timeout=2)