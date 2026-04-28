"""Logs GPS payload to file."""
import json
from pathlib import Path
from typing import Dict


class GPSLogger:
    """Logs GPS payload to file."""

    def __init__(self, file_path: str = "/tmp/gps_injection.log") -> None:
        """Initialize logger."""
        self._file_path = Path(file_path)
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, payload: Dict) -> None:
        """Log payload to file."""
        with open(self._file_path, "a") as f:
            f.write(json.dumps(payload) + "\n")


GPSSender = GPSLogger