"""Data models and converters for GPS injection."""

from dataclasses import dataclass
from typing import Optional, Tuple

from interfaces.msg import IBNResult

GPS_POSITION_LENGTH = 3


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


class IBNToGPSConverter:
    """Converts IBNResult messages to GPSInputPayload."""

    @staticmethod
    def extract_position(msg: IBNResult) -> Optional[Tuple[float, float, float]]:
        """Extract position tuple from message."""

        if not msg.position_valid:
            return None

        if len(msg.position) != GPS_POSITION_LENGTH:
            return None
        return msg.position[0], msg.position[1], msg.position[2]

    @staticmethod
    def convert(msg: IBNResult) -> Optional[GPSInputPayload]:
        """Convert IBNResult to GPS payload."""

        pos = IBNToGPSConverter.extract_position(msg)
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
