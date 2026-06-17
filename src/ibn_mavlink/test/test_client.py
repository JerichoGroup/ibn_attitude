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

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True

        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        params = GPSInputParams(
            lat=expected_lat,
            lon=expected_lon,
            alt=expected_alt,
        )

        client.send_gps_input(params)

        mock_master.mav.gps_input_send.assert_called_once()

        call_args = mock_master.mav.gps_input_send.call_args[0]

        lat_int = call_args[6]
        lon_int = call_args[7]
        alt = call_args[8]

        assert lat_int == expected_lat_int
        assert lon_int == expected_lon_int
        assert alt == expected_alt

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

        params = GPSInputParams(
            lat=expected_lat,
            lon=expected_lon,
            alt=expected_alt,
        )

        client.send_gps_input(params)

        mock_master.mav.gps_input_send.assert_called_once()

        call_args = mock_master.mav.gps_input_send.call_args[0]

        lat_int = call_args[6]
        lon_int = call_args[7]

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

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True

        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        params = GPSInputParams(
            lat=expected_lat,
            lon=expected_lon,
            alt=expected_alt,
        )

        client.send_gps_input(params)

        mock_master.mav.gps_input_send.assert_called_once()

        call_args = mock_master.mav.gps_input_send.call_args[0]

        lat_int = call_args[6]
        lon_int = call_args[7]
        alt = call_args[8]

        assert lat_int == expected_lat_int
        assert lon_int == expected_lon_int
        assert alt == expected_alt

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_velocity_conversion(self, mock_mavutil: "MagicMock") -> None:
        """Test velocity values passed correctly."""

        expected_vn = 10.5
        expected_ve = 20.7
        expected_vd = -5.3

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True

        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        params = GPSInputParams(
            lat=37.7749,
            lon=-122.4194,
            alt=100.0,
            vn=expected_vn,
            ve=expected_ve,
            vd=expected_vd,
        )

        client.send_gps_input(params)

        mock_master.mav.gps_input_send.assert_called_once()

        call_args = mock_master.mav.gps_input_send.call_args[0]

        vn = call_args[11]
        ve = call_args[12]
        vd = call_args[13]

        assert vn == expected_vn
        assert ve == expected_ve
        assert vd == expected_vd

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_dop_and_accuracy_passed_independently(self, mock_mavutil: "MagicMock") -> None:
        """Test that DOP (unitless) and accuracy (meters) are sent in separate fields."""

        hdop = 1.2
        horiz_accuracy = 2.0
        vert_accuracy = 3.0

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True

        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        params = GPSInputParams(
            lat=37.7749,
            lon=-122.4194,
            alt=100.0,
            hdop=hdop,
            horiz_accuracy=horiz_accuracy,
            vert_accuracy=vert_accuracy,
        )

        client.send_gps_input(params)

        mock_master.mav.gps_input_send.assert_called_once()

        call_args = mock_master.mav.gps_input_send.call_args[0]

        hdop_result = call_args[9]
        vdop_result = call_args[10]
        horiz_accuracy_result = call_args[15]
        vert_accuracy_result = call_args[16]

        assert hdop_result == hdop
        assert vdop_result == hdop
        assert horiz_accuracy_result == horiz_accuracy
        assert vert_accuracy_result == vert_accuracy

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

        params = GPSInputParams(
            lat=37.7749,
            lon=-122.4194,
            alt=100.0,
            satellites=satellites,
        )

        client.send_gps_input(params)

        mock_master.mav.gps_input_send.assert_called_once()

        call_args = mock_master.mav.gps_input_send.call_args[0]

        satellites_result = call_args[17]

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
        mock_master.recv_match.return_value = None
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
        mock_master.recv_match.return_value = None
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
        mock_master.recv_match.return_value = None
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=True)

        client.stop()

        assert client._thread is not None
        assert not client._thread.is_alive()

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_stop_no_thread_when_read_disabled(self, mock_mavutil: "MagicMock") -> None:
        """Test no thread started when read_enabled=False."""

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        client = MAVLinkClient("/dev/ttyACM0", 115200, rate=0, read_enabled=False)

        assert client._thread is None

    @patch("ibn_mavlink.mavlink.client.mavutil")
    def test_reconnect_called_on_recv_exception(self, mock_mavutil: "MagicMock") -> None:
        """Test reconnect triggered on MAVLink read failure."""

        mock_master = MagicMock()
        mock_master.target_system = 1
        mock_master.target_component = 1
        mock_master.wait_heartbeat.return_value = True
        mock_master.recv_match.side_effect = Exception("Connection lost")
        mock_mavutil.mavlink_connection.return_value = mock_master
        mock_mavutil.mavlink.MAV_DATA_STREAM_ALL = 0

        with patch.object(MAVLinkClient, "_reconnect") as mock_reconnect:
            client = MAVLinkClient(
                "/dev/ttyACM0",
                115200,
                rate=0,
                read_enabled=True,
            )

            time.sleep(0.05)

            mock_reconnect.assert_called_once()

            client.stop()
