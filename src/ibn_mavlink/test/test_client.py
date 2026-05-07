"""Tests for MAVLinkClient."""

import threading
import time
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from ibn_mavlink.mavlink.client import GPSInputParams, MAVLinkClient

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestGPSInputParams:
    """Tests for GPSInputParams dataclass."""

    def test_default_values(self) -> None:
        """Test default parameter values."""

        expected_lat = 37.7749
        expected_lon = -122.4194
        expected_alt = 100.0
        expected_satellites = 10

        params = GPSInputParams(lat=expected_lat, lon=expected_lon, alt=expected_alt)

        assert params.lat == expected_lat
        assert params.lon == expected_lon
        assert params.alt == expected_alt
        assert params.vn == 0.0
        assert params.ve == 0.0
        assert params.vd == 0.0
        assert params.satellites == expected_satellites
        assert params.hdop == 1.0

    def test_custom_values(self) -> None:
        """Test custom parameter values."""

        expected_vn = 1.0
        expected_ve = 2.0
        expected_vd = 3.0
        expected_satellites = 15
        expected_hdop = 2.5

        params = GPSInputParams(
            lat=40.7128,
            lon=-74.0060,
            alt=50.0,
            vn=expected_vn,
            ve=expected_ve,
            vd=expected_vd,
            satellites=expected_satellites,
            hdop=expected_hdop,
        )

        assert params.vn == expected_vn
        assert params.ve == expected_ve
        assert params.vd == expected_vd
        assert params.satellites == expected_satellites
        assert params.hdop == expected_hdop


class TestMAVLinkClientCoordinateConversion:
    """Tests for coordinate conversion in send_gps_input."""

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_coordinate_conversion_positive(self, mock_mavutil: "MagicMock") -> None:
        """Test positive coordinate conversion (North/East)."""

        expected_lat = 37.7749
        expected_lon = -122.4194
        expected_alt = 100.0
        expected_lat_int = 377749000
        expected_lon_int = -1224194000
        expected_alt_cm = 10000

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        params = GPSInputParams(lat=expected_lat, lon=expected_lon, alt=expected_alt)
        client.send_gps_input(params)

        mock_master.mav.gps_input_send.assert_called_once()
        call_args = mock_master.mav.gps_input_send.call_args

        lat_int = call_args[0][2]
        lon_int = call_args[0][3]
        alt_cm = call_args[0][4]

        assert lat_int == expected_lat_int
        assert lon_int == expected_lon_int
        assert alt_cm == expected_alt_cm

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_coordinate_conversion_negative(self, mock_mavutil: "MagicMock") -> None:
        """Test negative coordinate conversion (South/West)."""

        expected_lat = -33.8688
        expected_lon = 151.2093
        expected_alt = 50.0
        expected_lat_int = -338688000
        expected_lon_int = 1512093000

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        params = GPSInputParams(lat=expected_lat, lon=expected_lon, alt=expected_alt)
        client.send_gps_input(params)

        mock_master.mav.gps_input_send.assert_called_once()
        call_args = mock_master.mav.gps_input_send.call_args

        lat_int = call_args[0][2]
        lon_int = call_args[0][3]

        assert lat_int == expected_lat_int
        assert lon_int == expected_lon_int

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_coordinate_conversion_extreme_values(self, mock_mavutil: "MagicMock") -> None:
        """Test extreme coordinate values."""

        expected_lat = 89.9999999
        expected_lon = 179.9999999
        expected_alt = 8848.0
        expected_lat_int = 899999999
        expected_lon_int = 1799999999
        expected_alt_cm = 884800

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        params = GPSInputParams(lat=expected_lat, lon=expected_lon, alt=expected_alt)
        client.send_gps_input(params)

        mock_master.mav.gps_input_send.assert_called_once()
        call_args = mock_master.mav.gps_input_send.call_args

        lat_int = call_args[0][2]
        lon_int = call_args[0][3]
        alt_cm = call_args[0][4]

        assert lat_int == expected_lat_int
        assert lon_int == expected_lon_int
        assert alt_cm == expected_alt_cm

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_velocity_conversion(self, mock_mavutil: "MagicMock") -> None:
        """Test velocity conversion to cm/s."""

        expected_vn = 10.5
        expected_ve = 20.7
        expected_vd = -5.3
        expected_vn_cm = 1050
        expected_ve_cm = 2070
        expected_vd_cm = -530

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        params = GPSInputParams(lat=37.7749, lon=-122.4194, alt=100.0, vn=expected_vn, ve=expected_ve, vd=expected_vd)
        client.send_gps_input(params)

        mock_master.mav.gps_input_send.assert_called_once()
        call_args = mock_master.mav.gps_input_send.call_args

        vn_cm = call_args[0][5]
        ve_cm = call_args[0][6]
        vd_cm = call_args[0][7]

        assert vn_cm == expected_vn_cm
        assert ve_cm == expected_ve_cm
        assert vd_cm == expected_vd_cm

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_hdop_to_accuracy_conversion(self, mock_mavutil: "MagicMock") -> None:
        """Test HDOP to accuracy conversion."""

        hdop = 2.0
        expected_horiz_accuracy = 200
        expected_vert_accuracy = 300

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        params = GPSInputParams(lat=37.7749, lon=-122.4194, alt=100.0, hdop=hdop)
        client.send_gps_input(params)

        mock_master.mav.gps_input_send.assert_called_once()
        call_args = mock_master.mav.gps_input_send.call_args

        horiz_accuracy = call_args[0][8]
        vert_accuracy = call_args[0][9]

        assert horiz_accuracy == expected_horiz_accuracy
        assert vert_accuracy == expected_vert_accuracy

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_satellite_count(self, mock_mavutil: "MagicMock") -> None:
        """Test satellite count handling."""

        satellites = 20

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        params = GPSInputParams(lat=37.7749, lon=-122.4194, alt=100.0, satellites=satellites)
        client.send_gps_input(params)

        mock_master.mav.gps_input_send.assert_called_once()
        call_args = mock_master.mav.gps_input_send.call_args

        satellites_result = call_args[0][10]

        assert satellites_result == satellites


class TestMAVLinkClientGetLatest:
    """Tests for get_latest thread-safe message retrieval."""

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_get_latest_empty(self, mock_mavutil: "MagicMock") -> None:
        """Test get_latest returns None on first call."""

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        result = client.get_latest("GLOBAL_POSITION_INT")

        assert result is None

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_get_latest_returns_message(self, mock_mavutil: "MagicMock") -> None:
        """Test get_latest returns stored message."""

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        mock_msg = MagicMock()
        mock_msg.get_type.return_value = "GLOBAL_POSITION_INT"

        with client._lock:
            client._latest["GLOBAL_POSITION_INT"] = mock_msg

        result = client.get_latest("GLOBAL_POSITION_INT")

        assert result == mock_msg

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_get_latest_thread_safety(self, mock_mavutil: "MagicMock") -> None:
        """Test thread-safe concurrent get_latest calls."""

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=True)

        mock_msg = MagicMock()
        mock_msg.get_type.return_value = "GLOBAL_POSITION_INT"

        results = []
        errors = []

        def writer() -> None:
            for _ in range(100):
                with client._lock:
                    client._latest["GLOBAL_POSITION_INT"] = mock_msg
                time.sleep(0.001)

        def reader() -> None:
            for _ in range(100):
                try:
                    result = client.get_latest("GLOBAL_POSITION_INT")
                    results.append(result)
                except Exception as e:
                    errors.append(e)
                time.sleep(0.001)

        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)

        writer_thread.start()
        reader_thread.start()

        writer_thread.join()
        reader_thread.join()

        assert len(errors) == 0


class TestMAVLinkClientStop:
    """Tests for client stop behavior."""

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_stop_sets_running_false(self, mock_mavutil: "MagicMock") -> None:
        """Test stop sets _running to False."""

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=True)

        assert client._running is True

        client.stop()

        assert client._running is False

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_stop_joins_thread(self, mock_mavutil: "MagicMock") -> None:
        """Test stop joins background thread."""

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=True)

        client.stop()

        assert not client._thread.is_alive()

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_stop_no_thread_when_read_disabled(self, mock_mavutil: "MagicMock") -> None:
        """Test no thread created when read_enabled=False."""

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        assert not hasattr(client, "_thread")
