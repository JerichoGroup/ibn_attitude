"""Tests for GPSInjectionNode."""

from unittest.mock import MagicMock, patch

from ibn_mavlink.gps_injection.converter import GPSInputPayload
from ibn_mavlink.gps_injection.node import GPSInjectionNode


class TestGPSInjectionNode:
    """Behavior tests for GPSInjectionNode logic."""

    @patch("ibn_mavlink.gps_injection.node.MAVLinkClient")
    def test_callback_stores_payload(self, mock_client, valid_gps_injection_config):
        """Test that callback properly converts and stores latest GPSInputPayload."""
        
        node = GPSInjectionNode(valid_gps_injection_config)

        payload = GPSInputPayload(
            lat=37.7749,
            lon=-122.4194,
            alt=100.0,
            horiz_accuracy=1.5,
            vert_accuracy=1.5,
        )

        msg = MagicMock()

        with patch(
            "ibn_mavlink.gps_injection.node.IBNToGPSConverter.convert",
            return_value=payload,
        ):
            node._callback(msg)

        assert node._latest_payload == payload


    @patch("ibn_mavlink.gps_injection.node.MAVLinkClient")
    def test_callback_invalid_ignored(self, mock_client, valid_gps_injection_config):
        """Test that callback sets _latest_payload to None when converter returns None."""

        node = GPSInjectionNode(valid_gps_injection_config)

        msg = MagicMock()

        with patch(
            "ibn_mavlink.gps_injection.node.IBNToGPSConverter.convert",
            return_value=None,
        ):
            node._callback(msg)

        assert node._latest_payload is None


    @patch("ibn_mavlink.gps_injection.node.MAVLinkClient")
    def test_inject_loop_no_payload(self, mock_client, valid_gps_injection_config):
        """Test that _inject_loop does nothing when no valid payload is available."""

        node = GPSInjectionNode(valid_gps_injection_config)

        node._inject_loop()

        node._client.send_gps_input.assert_not_called()


    @patch("ibn_mavlink.gps_injection.node.MAVLinkClient")
    def test_inject_loop_sends_gps(self, mock_client, valid_gps_injection_config):
        """Test that _inject_loop sends GPSInputParams with correct values."""

        node = GPSInjectionNode(valid_gps_injection_config)

        node._latest_payload = GPSInputPayload(
            lat=37.7749,
            lon=-122.4194,
            alt=100.0,
            horiz_accuracy=1.5,
            vert_accuracy=1.5,
        )

        node._inject_loop()

        node._client.send_gps_input.assert_called_once()

        sent = node._client.send_gps_input.call_args[0][0]

        assert sent.lat == 37.7749
        assert sent.lon == -122.4194
        assert sent.alt == 100.0
        assert sent.hdop == 1.5
        assert sent.satellites == 10


    @patch("ibn_mavlink.gps_injection.node.MAVLinkClient")
    def test_destroy_node_stops_client(self, mock_client, valid_gps_injection_config):
        """Test that destroy_node properly stops the MAVLink client."""

        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance

        node = GPSInjectionNode(valid_gps_injection_config)

        node.destroy_node()

        mock_client_instance.stop.assert_called_once()