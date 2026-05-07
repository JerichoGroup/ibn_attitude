"""Tests for GPSInjectionNode logic."""

from unittest.mock import MagicMock

from ibn_mavlink.gps_injection.converter import GPSInputPayload, IBNToGPSConverter


class TestGPSInjectionNodeLogic:
    """Tests for node logic without ROS2 initialization."""

    def test_payload_attributes(self) -> None:
        """Test GPSInputPayload attributes."""

        test_lat = 37.7749
        test_lon = -122.4194
        test_alt = 100.0
        test_accuracy = 1.5
        expected_satellites = 10

        payload = GPSInputPayload(
            lat=test_lat, lon=test_lon, alt=test_alt, horiz_accuracy=test_accuracy, vert_accuracy=test_accuracy
        )

        assert payload.lat == test_lat
        assert payload.lon == test_lon
        assert payload.alt == test_alt
        assert payload.horiz_accuracy == test_accuracy
        assert payload.vert_accuracy == test_accuracy
        assert payload.satellites_visible == expected_satellites

    def test_convert_returns_none_for_invalid_position_valid_false(self) -> None:
        """Test IBNToGPSConverter returns None for position_valid=False."""

        test_lat = 37.7749
        test_lon = -122.4194
        test_alt = 100.0

        msg = MagicMock()
        msg.position_valid = False
        msg.position = [test_lat, test_lon, test_alt]
        msg.position_accuracy = 1.5

        result = IBNToGPSConverter.convert(msg)

        assert result is None

    def test_convert_returns_none_for_invalid_position_length(self) -> None:
        """Test IBNToGPSConverter returns None for wrong position length."""

        msg = MagicMock()
        msg.position_valid = True
        msg.position = [37.7749]
        msg.position_accuracy = 1.5

        result = IBNToGPSConverter.convert(msg)

        assert result is None

    def test_convert_returns_payload_for_valid(self) -> None:
        """Test IBNToGPSConverter returns payload for valid input."""

        test_lat = 37.7749
        test_lon = -122.4194
        test_alt = 100.0

        msg = MagicMock()
        msg.position_valid = True
        msg.position = [test_lat, test_lon, test_alt]
        msg.position_accuracy = 1.5

        result = IBNToGPSConverter.convert(msg)

        assert result is not None
        assert result.lat == test_lat
        assert result.lon == test_lon
        assert result.alt == test_alt

    def test_extract_position_with_valid_position_returns_position_tuple(self) -> None:
        """Test extract_position returns tuple when position is valid."""

        test_lat = 37.7749
        test_lon = -122.4194
        test_alt = 100.0

        msg = MagicMock()
        msg.position_valid = True
        msg.position = [test_lat, test_lon, test_alt]

        result = IBNToGPSConverter.extract_position(msg)

        expected = (test_lat, test_lon, test_alt)
        assert result == expected

    def test_extract_position_with_invalid_position_returns_none(self) -> None:
        """Test extract_position returns None when position is invalid."""

        msg = MagicMock()
        msg.position_valid = False
        msg.position = [37.7749, -122.4194, 100.0]

        result = IBNToGPSConverter.extract_position(msg)

        assert result is None
