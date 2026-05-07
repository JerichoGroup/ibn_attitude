"""Tests for IBNToGPSConverter."""

from unittest.mock import MagicMock

from ibn_mavlink.gps_injection.converter import GPS_POSITION_LENGTH, GPSInputPayload, IBNToGPSConverter


class TestIBNToGPSExtractPosition:
    """Tests for extract_position method."""

    def test_extract_valid_position(self) -> None:
        """Test extraction with valid position (position_valid=True, length=3)."""

        test_lat = 37.7749
        test_lon = -122.4194
        test_alt = 100.0
        expected_length = 3

        msg = MagicMock()
        msg.position_valid = True
        msg.position = [test_lat, test_lon, test_alt]

        result = IBNToGPSConverter.extract_position(msg)

        assert result is not None
        assert len(result) == expected_length
        assert result[0] == test_lat
        assert result[1] == test_lon
        assert result[2] == test_alt

    def test_extract_invalid_position_valid_false(self) -> None:
        """Test extraction with position_valid=False."""

        test_lat = 37.7749
        test_lon = -122.4194
        test_alt = 100.0

        msg = MagicMock()
        msg.position_valid = False
        msg.position = [test_lat, test_lon, test_alt]

        result = IBNToGPSConverter.extract_position(msg)

        assert result is None

    def test_extract_invalid_position_length_zero(self) -> None:
        """Test extraction with empty position array."""

        msg = MagicMock()
        msg.position_valid = True
        msg.position = []

        result = IBNToGPSConverter.extract_position(msg)

        assert result is None

    def test_extract_invalid_position_length_one(self) -> None:
        """Test extraction with position array length=1."""

        test_lat = 37.7749

        msg = MagicMock()
        msg.position_valid = True
        msg.position = [test_lat]

        result = IBNToGPSConverter.extract_position(msg)

        assert result is None

    def test_extract_invalid_position_length_two(self) -> None:
        """Test extraction with position array length=2."""

        test_lat = 37.7749
        test_lon = -122.4194

        msg = MagicMock()
        msg.position_valid = True
        msg.position = [test_lat, test_lon]

        result = IBNToGPSConverter.extract_position(msg)

        assert result is None

    def test_extract_invalid_position_length_four(self) -> None:
        """Test extraction with position array length=4."""

        test_lat = 37.7749
        test_lon = -122.4194
        test_alt = 100.0
        test_extra = 50.0

        msg = MagicMock()
        msg.position_valid = True
        msg.position = [test_lat, test_lon, test_alt, test_extra]

        result = IBNToGPSConverter.extract_position(msg)

        assert result is None


class TestIBNToGPSConvert:
    """Tests for convert method."""

    def test_convert_valid_message(self) -> None:
        """Test full conversion flow with valid message."""

        test_lat = 37.7749
        test_lon = -122.4194
        test_alt = 100.0
        test_accuracy = 1.5

        msg = MagicMock()
        msg.position_valid = True
        msg.position = [test_lat, test_lon, test_alt]
        msg.position_accuracy = test_accuracy

        result = IBNToGPSConverter.convert(msg)

        assert result is not None
        assert isinstance(result, GPSInputPayload)
        assert result.lat == test_lat
        assert result.lon == test_lon
        assert result.alt == test_alt
        assert result.horiz_accuracy == test_accuracy
        assert result.vert_accuracy == test_accuracy

    def test_convert_invalid_position_valid(self) -> None:
        """Test conversion with position_valid=False."""

        test_lat = 37.7749
        test_lon = -122.4194
        test_alt = 100.0

        msg = MagicMock()
        msg.position_valid = False
        msg.position = [test_lat, test_lon, test_alt]
        msg.position_accuracy = 1.5

        result = IBNToGPSConverter.convert(msg)

        assert result is None

    def test_convert_invalid_position_length(self) -> None:
        """Test conversion with wrong position array length."""

        test_lat = 37.7749

        msg = MagicMock()
        msg.position_valid = True
        msg.position = [test_lat]
        msg.position_accuracy = 1.5

        result = IBNToGPSConverter.convert(msg)

        assert result is None

    def test_convert_negative_coordinates(self) -> None:
        """Test conversion with negative coordinates (South/West)."""

        test_lat = -33.8688
        test_lon = 151.2093
        test_alt = 50.0

        msg = MagicMock()
        msg.position_valid = True
        msg.position = [test_lat, test_lon, test_alt]
        msg.position_accuracy = 2.0

        result = IBNToGPSConverter.convert(msg)

        assert result is not None
        assert result.lat == test_lat
        assert result.lon == test_lon

    def test_convert_extreme_coordinates(self) -> None:
        """Test conversion with extreme coordinate values."""

        test_lat = 89.9999999
        test_lon = 179.9999999
        test_alt = 8848.0

        msg = MagicMock()
        msg.position_valid = True
        msg.position = [test_lat, test_lon, test_alt]
        msg.position_accuracy = 0.5

        result = IBNToGPSConverter.convert(msg)

        assert result is not None
        assert result.lat == test_lat
        assert result.lon == test_lon
        assert result.alt == test_alt


class TestGPSInputPayload:
    """Tests for GPSInputPayload dataclass."""

    def test_default_fix_type_and_satellite_count(self) -> None:
        """Test that default payload has correct fix type and satellite count."""

        test_lat = 37.7749
        test_lon = -122.4194
        test_alt = 100.0
        expected_fix_type = 3
        expected_satellites = 10

        payload = GPSInputPayload(lat=test_lat, lon=test_lon, alt=test_alt, horiz_accuracy=1.0, vert_accuracy=1.5)

        assert payload.fix_type == expected_fix_type
        assert payload.satellites_visible == expected_satellites

    def test_custom_fix_type_and_satellite_count(self) -> None:
        """Test that custom payload values are stored correctly."""

        expected_fix_type = 5
        expected_satellites = 15

        payload = GPSInputPayload(
            lat=37.7749,
            lon=-122.4194,
            alt=100.0,
            horiz_accuracy=2.0,
            vert_accuracy=3.0,
            fix_type=expected_fix_type,
            satellites_visible=expected_satellites,
        )

        assert payload.fix_type == expected_fix_type
        assert payload.satellites_visible == expected_satellites

    def test_to_json(self) -> None:
        """Test JSON conversion."""

        test_lat = 37.7749
        test_lon = -122.4194
        test_alt = 100.0
        expected_fix_type = 3
        expected_lat_int = 377749000
        expected_lon_int = -1224194000
        expected_satellites = 10

        payload = GPSInputPayload(lat=test_lat, lon=test_lon, alt=test_alt, horiz_accuracy=1.0, vert_accuracy=2.0)

        json_data = payload.to_json()

        assert "time_usec" in json_data
        assert json_data["gps_id"] == 0
        assert json_data["ignore_flags"] == 0
        assert json_data["fix_type"] == expected_fix_type
        assert json_data["lat"] == expected_lat_int
        assert json_data["lon"] == expected_lon_int
        assert json_data["alt"] == test_alt
        assert json_data["horiz_accuracy"] == 1.0
        expected_vert_accuracy = 2.0
        assert json_data["vert_accuracy"] == expected_vert_accuracy
        assert json_data["satellites_visible"] == expected_satellites


class TestGPSPositionLength:
    """Tests for GPS_POSITION_LENGTH constant."""

    def test_position_length_value(self) -> None:
        """Test GPS_POSITION_LENGTH is 3."""

        expected_length = 3

        assert GPS_POSITION_LENGTH == expected_length
