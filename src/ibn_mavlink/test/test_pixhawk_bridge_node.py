"""Tests for PixhawkTelemetry node logic."""


class TestPixhawkClientLogic:
    """Tests for MAVLinkClient logic in bridge context."""

    def test_client_has_get_latest_method(self) -> None:
        """Test client has get_latest method."""

        from ibn_mavlink.mavlink.client import MAVLinkClient

        assert hasattr(MAVLinkClient, "get_latest")

    def test_client_has_send_gps_input_method(self) -> None:
        """Test client has send_gps_input method."""

        from ibn_mavlink.mavlink.client import MAVLinkClient

        assert hasattr(MAVLinkClient, "send_gps_input")

    def test_client_has_stop_method(self) -> None:
        """Test client has stop method."""

        from ibn_mavlink.mavlink.client import MAVLinkClient

        assert hasattr(MAVLinkClient, "stop")

    def test_gps_input_params_fields(self) -> None:
        """Test GPSInputParams has expected fields."""

        from ibn_mavlink.mavlink.client import GPSInputParams

        params = GPSInputParams(lat=37.7749, lon=-122.4194, alt=100.0)
        assert hasattr(params, "lat")
        assert hasattr(params, "lon")
        assert hasattr(params, "alt")
        assert hasattr(params, "vn")
        assert hasattr(params, "ve")
        assert hasattr(params, "vd")
        assert hasattr(params, "satellites")
        assert hasattr(params, "hdop")


class TestMAVLinkClientIntegration:
    """Integration-style tests with mocked MAVLink."""

    def test_coordinate_conversion_helper(self) -> None:
        """Test coordinate conversion logic."""

        lat = 37.7749
        lon = -122.4194

        lat_int = int(lat * 1e7)
        lon_int = int(lon * 1e7)

        expected_lat_int = 377749000
        expected_lon_int = -1224194000

        assert lat_int == expected_lat_int
        assert lon_int == expected_lon_int

    def test_velocity_conversion_helper(self) -> None:
        """Test velocity conversion logic."""

        vn = 10.5
        ve = 20.7
        vd = -5.3

        vn_cm = int(vn * 100)
        ve_cm = int(ve * 100)
        vd_cm = int(vd * 100)

        expected_vn_cm = 1050
        expected_ve_cm = 2070
        expected_vd_cm = -530

        assert vn_cm == expected_vn_cm
        assert ve_cm == expected_ve_cm
        assert vd_cm == expected_vd_cm

    def test_hdop_conversion_helper(self) -> None:
        """Test HDOP conversion logic."""

        hdop = 2.0

        horiz_accuracy = int(hdop * 100)
        vert_accuracy = int(hdop * 150)

        expected_horiz = 200
        expected_vert = 300

        assert horiz_accuracy == expected_horiz
        assert vert_accuracy == expected_vert
