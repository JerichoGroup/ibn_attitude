"""Tests for PixhawkTelemetry node logic."""

from unittest.mock import MagicMock, patch

from ibn_mavlink.pixhawk_bridge.node import PixhawkTelemetry


TEST_CONFIG = {
    "mavlink": {
        "connection_string": "/dev/ttyACM0",
        "baud_rate": 115200,
        "stream_rate_hz": 10,
    },
    "ros": {
        "global_position_topic": "/global_position",
        "attitude_topic": "/attitude",
        "init_position_topic": "/init_position",
        "publish_rate_hz": 10,
    },
    "log": {
        "file_path": "/tmp/test.log",
    },
}


class TestPixhawkBridgeNode:
    """Behavior tests for PixhawkTelemetry."""

    @patch("ibn_mavlink.pixhawk_bridge.node.setup_logger")
    @patch("ibn_mavlink.pixhawk_bridge.node.MAVLinkClient")
    def test_destroy_node_stops_client(
        self,
        mock_client_class,
        mock_logger,
    ):
        """Test destroy_node stops MAVLink client."""

        mock_logger.return_value = MagicMock()

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        with patch.object(PixhawkTelemetry, "create_publisher"), \
             patch.object(PixhawkTelemetry, "create_timer"), \
             patch("rclpy.node.Node.destroy_node"):

            node = PixhawkTelemetry(TEST_CONFIG)
            node.destroy_node()

        mock_client.stop.assert_called_once()


    @patch("ibn_mavlink.pixhawk_bridge.node.setup_logger")
    @patch("ibn_mavlink.pixhawk_bridge.node.MavlinkTranslator")
    @patch("ibn_mavlink.pixhawk_bridge.node.MAVLinkClient")
    def test_tick_skips_when_no_messages(
        self,
        mock_client_class,
        mock_translator,
        mock_logger,
    ):
        """Test tick does nothing when no MAVLink messages."""

        mock_logger.return_value = MagicMock()

        mock_client = MagicMock()
        mock_client.get_latest.return_value = None
        mock_client_class.return_value = mock_client

        mock_global_pub = MagicMock()
        mock_att_pub = MagicMock()
        mock_init_pub = MagicMock()

        with patch.object(
            PixhawkTelemetry,
            "create_publisher",
            side_effect=[
                mock_global_pub,
                mock_att_pub,
                mock_init_pub,
            ],
        ), patch.object(PixhawkTelemetry, "create_timer"):

            node = PixhawkTelemetry(TEST_CONFIG)
            node._tick()

        mock_translator.to_global_position.assert_not_called()
        mock_translator.to_attitude.assert_not_called()

        mock_global_pub.publish.assert_not_called()
        mock_att_pub.publish.assert_not_called()
        mock_init_pub.publish.assert_not_called()


    @patch("ibn_mavlink.pixhawk_bridge.node.setup_logger")
    @patch("ibn_mavlink.pixhawk_bridge.node.MavlinkTranslator")
    @patch("ibn_mavlink.pixhawk_bridge.node.MAVLinkClient")
    def test_tick_global_position_flow(
        self,
        mock_client_class,
        mock_translator,
        mock_logger,
    ):
        """Test global position publish flow."""

        mock_logger.return_value = MagicMock()

        mock_global_msg = MagicMock()

        mock_client = MagicMock()
        mock_client.get_latest.side_effect = [
            mock_global_msg,
            None,
        ]
        mock_client_class.return_value = mock_client

        mock_ros_msg = MagicMock()
        mock_translator.to_global_position.return_value = mock_ros_msg

        mock_global_pub = MagicMock()
        mock_att_pub = MagicMock()
        mock_init_pub = MagicMock()

        with patch.object(
            PixhawkTelemetry,
            "create_publisher",
            side_effect=[
                mock_global_pub,
                mock_att_pub,
                mock_init_pub,
            ],
        ), patch.object(PixhawkTelemetry, "create_timer"):

            node = PixhawkTelemetry(TEST_CONFIG)
            node._tick()

        mock_translator.to_global_position.assert_called_once_with(
            node,
            mock_global_msg,
        )

        mock_global_pub.publish.assert_called()


    @patch("ibn_mavlink.pixhawk_bridge.node.setup_logger")
    @patch("ibn_mavlink.pixhawk_bridge.node.MavlinkTranslator")
    @patch("ibn_mavlink.pixhawk_bridge.node.MAVLinkClient")
    def test_tick_attitude_flow(
        self,
        mock_client_class,
        mock_translator,
        mock_logger,
    ):
        """Test attitude publish flow."""

        mock_logger.return_value = MagicMock()

        mock_att_msg = MagicMock()

        mock_client = MagicMock()
        mock_client.get_latest.side_effect = [
            None,
            mock_att_msg,
        ]
        mock_client_class.return_value = mock_client

        mock_ros_msg = MagicMock()
        mock_translator.to_attitude.return_value = mock_ros_msg

        mock_global_pub = MagicMock()
        mock_att_pub = MagicMock()
        mock_init_pub = MagicMock()

        with patch.object(
            PixhawkTelemetry,
            "create_publisher",
            side_effect=[
                mock_global_pub,
                mock_att_pub,
                mock_init_pub,
            ],
        ), patch.object(PixhawkTelemetry, "create_timer"):

            node = PixhawkTelemetry(TEST_CONFIG)
            node._tick()

        mock_translator.to_attitude.assert_called_once_with(
            node,
            mock_att_msg,
        )

        mock_att_pub.publish.assert_called_once_with(mock_ros_msg)


    @patch("ibn_mavlink.pixhawk_bridge.node.setup_logger")
    @patch("ibn_mavlink.pixhawk_bridge.node.MAVLinkClient")
    def test_init_position_published_once(
        self,
        mock_client_class,
        mock_logger,
    ):
        """Test init position publishing."""

        mock_logger.return_value = MagicMock()

        mock_client = MagicMock()
        mock_client.get_latest.return_value = None
        mock_client_class.return_value = mock_client

        mock_global_pub = MagicMock()
        mock_att_pub = MagicMock()
        mock_init_pub = MagicMock()

        with patch.object(
            PixhawkTelemetry,
            "create_publisher",
            side_effect=[
                mock_global_pub,
                mock_att_pub,
                mock_init_pub,
            ],
        ), patch.object(PixhawkTelemetry, "create_timer"):

            node = PixhawkTelemetry(TEST_CONFIG)

            node._init_position = MagicMock()

            node._publish_init_position()

        mock_init_pub.publish.assert_called_once_with(
            node._init_position
        )
