"""Data models and converters for GPS injection."""
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from your_msgs.msg import IbnResult


@dataclass
class GPSInputPayload:
    """GPS payload for injection."""
    lat: float
    lon: float
    alt: float
    horiz_accuracy: float
    vert_accuracy: float
    fix_type: int = 3
    satellites_visible: int = 10

    def to_json(self) -> Dict:
        """Convert to JSON-compatible dict."""
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


class IbnToGPSConverter:
    """Converts IbnResult messages to GPSInputPayload."""

    @staticmethod
    def extract_position(msg: IbnResult) -> Optional[Tuple[float, float, float]]:
        """Extract position tuple from message."""
        if not msg.position_valid:
            return None
        if len(msg.position) != 3:
            return None
        return msg.position[0], msg.position[1], msg.position[2]

    @staticmethod
    def convert(msg: IbnResult) -> Optional[GPSInputPayload]:
        """Convert IbnResult to GPS payload."""
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