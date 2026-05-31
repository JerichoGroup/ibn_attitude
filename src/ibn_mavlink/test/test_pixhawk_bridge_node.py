"""Tests for PixhawkTelemetry node logic."""

from unittest.mock import MagicMock, patch

from ibn_mavlink.pixhawk_bridge.node import PixhawkTelemetry
from ibn_mavlink.test.conftest import valid_pixhawk_config


class TestPixhawkBridgeNode:
    """Behavior tests for PixhawkTelemetry."""

    @patch("ibn_mavlink.pixhawk_bridge.node.setup_logger")
    @patch("ibn_mavlink.pixhawk_bridge.node.MAVLinkClient")
    def test_manual_cleanup_stops_client(
        self,
        mock_client_class,
        mock_logger,
        valid_pixhawk_config,
    ):
        mock_logger.return_value = MagicMock()
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        with patch.object(PixhawkTelemetry, "create_publisher"), \
             patch.object(PixhawkTelemetry, "create_timer"), \
             patch("rclpy.node.Node.destroy_node"):

            node = PixhawkTelemetry(valid_pixhawk_config)
            node._client = mock_client

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
        valid_pixhawk_config,
    ):
        mock_logger.return_value = MagicMock()

        mock_client = MagicMock()
        mock_client.get_latest.return_value = None
        mock_client_class.return_value = mock_client

        with patch("rclpy.logging._logger.RclpyLogger"), \
             patch.object(PixhawkTelemetry, "create_publisher",
                        side_effect=[MagicMock(), MagicMock(), MagicMock()]), \
             patch.object(PixhawkTelemetry, "create_timer"):

            node = PixhawkTelemetry(valid_pixhawk_config)
            node._tick()

        mock_translator.to_global_position.assert_not_called()
        mock_translator.to_attitude.assert_not_called()


    @patch("ibn_mavlink.pixhawk_bridge.node.setup_logger")
    @patch("ibn_mavlink.pixhawk_bridge.node.MavlinkTranslator")
    @patch("ibn_mavlink.pixhawk_bridge.node.MAVLinkClient")
    def test_tick_global_position_flow(
        self,
        mock_client_class,
        mock_translator,
        mock_logger,
        valid_pixhawk_config,
        sample_global_position_msg,
    ):
        mock_logger.return_value = MagicMock()

        mock_client = MagicMock()
        mock_client.get_latest.side_effect = (
            lambda t: sample_global_position_msg if t == "GLOBAL_POSITION_INT" else None
        )
        mock_client_class.return_value = mock_client

        mock_ros_msg = MagicMock()
        mock_translator.to_global_position.return_value = mock_ros_msg

        mock_pub = MagicMock()

        with patch("rclpy.logging._logger.RclpyLogger"), \
             patch.object(PixhawkTelemetry, "create_publisher",
                        side_effect=[mock_pub, MagicMock(), MagicMock()]), \
             patch.object(PixhawkTelemetry, "create_timer"):

            node = PixhawkTelemetry(valid_pixhawk_config)
            node._tick()

        mock_translator.to_global_position.assert_called_once()
        mock_pub.publish.assert_called_once_with(mock_ros_msg)


    @patch("ibn_mavlink.pixhawk_bridge.node.setup_logger")
    @patch("ibn_mavlink.pixhawk_bridge.node.MavlinkTranslator")
    @patch("ibn_mavlink.pixhawk_bridge.node.MAVLinkClient")
    def test_tick_attitude_flow(
        self,
        mock_client_class,
        mock_translator,
        mock_logger,
        valid_pixhawk_config,
        sample_attitude_msg,
    ):
        mock_logger.return_value = MagicMock()

        mock_client = MagicMock()
        mock_client.get_latest.side_effect = (
            lambda t: sample_attitude_msg if t == "ATTITUDE" else None
        )
        mock_client_class.return_value = mock_client

        mock_ros_msg = MagicMock()
        mock_translator.to_attitude.return_value = mock_ros_msg

        mock_pub = MagicMock()

        with patch("rclpy.logging._logger.RclpyLogger"), \
             patch.object(PixhawkTelemetry, "create_publisher",
                        side_effect=[MagicMock(), mock_pub, MagicMock()]), \
             patch.object(PixhawkTelemetry, "create_timer"):

            node = PixhawkTelemetry(valid_pixhawk_config)
            node._tick()

        mock_translator.to_attitude.assert_called_once()
        mock_pub.publish.assert_called_once_with(mock_ros_msg)


    @patch("ibn_mavlink.pixhawk_bridge.node.setup_logger")
    @patch("ibn_mavlink.pixhawk_bridge.node.MAVLinkClient")
    def test_publish_init_position(
        self,
        mock_client_class,
        mock_logger,
        valid_pixhawk_config,
    ):
        mock_logger.return_value = MagicMock()
        mock_client_class.return_value = MagicMock()

        mock_pub = MagicMock()

        with patch("rclpy.logging._logger.RclpyLogger"), \
             patch.object(PixhawkTelemetry, "create_publisher",
                        side_effect=[MagicMock(), MagicMock(), mock_pub]), \
             patch.object(PixhawkTelemetry, "create_timer"):

            node = PixhawkTelemetry(valid_pixhawk_config)

            node._init_position = MagicMock()
            node._publish_init_position()

        mock_pub.publish.assert_called_once()
