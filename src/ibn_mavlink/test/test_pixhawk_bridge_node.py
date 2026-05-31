"""Tests for PixhawkTelemetry node logic."""

from unittest.mock import MagicMock, patch

patch("rclpy.node.Node._create_rosout_publisher", return_value=None).start()

from ibn_mavlink.pixhawk_bridge.node import PixhawkTelemetry


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

        with patch.object(PixhawkTelemetry, "create_publisher",
                          return_value=MagicMock()), \
             patch.object(PixhawkTelemetry, "create_timer"), \
             patch("rclpy.node.Node.destroy_node"):

            node = PixhawkTelemetry(valid_pixhawk_config)
            node.destroy_node()

        mock_client.stop.assert_called_once()


    @patch("ibn_mavlink.pixhawk_bridge.node.setup_logger")
    @patch("ibn_mavlink.pixhawk_bridge.node.MAVLinkClient")
    def test_tick_skips_when_no_messages(
        self,
        mock_client_class,
        mock_logger,
        valid_pixhawk_config,
    ):
        mock_logger.return_value = MagicMock()

        mock_client = MagicMock()
        mock_client.get_latest.return_value = None
        mock_client_class.return_value = mock_client

        with patch.object(PixhawkTelemetry, "create_publisher",
                          return_value=MagicMock()), \
             patch.object(PixhawkTelemetry, "create_timer"), \
             patch.object(PixhawkTelemetry, "_handle_global_position") as mock_handle, \
             patch.object(PixhawkTelemetry, "_publish_init_position") as mock_publish_init:

            node = PixhawkTelemetry(valid_pixhawk_config)
            node._tick()

        mock_handle.assert_not_called()
        mock_publish_init.assert_not_called()


    @patch("ibn_mavlink.pixhawk_bridge.node.setup_logger")
    @patch("ibn_mavlink.pixhawk_bridge.node.MAVLinkClient")
    @patch("ibn_mavlink.pixhawk_bridge.node.MavlinkTranslator.to_global_position")
    def test_tick_global_position_flow(
        self,
        mock_translate,
        mock_client_class,
        mock_logger,
        valid_pixhawk_config,
        sample_global_position_msg,
    ):
        mock_logger.return_value = MagicMock()

        mock_client = MagicMock()
        mock_client.get_latest.side_effect = (
            lambda t: sample_global_position_msg
            if t == "GLOBAL_POSITION_INT"
            else None
        )
        mock_client_class.return_value = mock_client

        ros_msg = MagicMock()
        mock_translate.return_value = ros_msg

        global_pub = MagicMock()
        attitude_pub = MagicMock()
        init_pub = MagicMock()

        with patch.object(
            PixhawkTelemetry,
            "create_publisher",
            side_effect=[global_pub, attitude_pub, init_pub],
        ), patch.object(PixhawkTelemetry, "create_timer"):

            node = PixhawkTelemetry(valid_pixhawk_config)
            node._tick()

        mock_translate.assert_called_once()
        global_pub.publish.assert_called_once_with(ros_msg)
        init_pub.publish.assert_called_once_with(ros_msg)


    @patch("ibn_mavlink.pixhawk_bridge.node.setup_logger")
    @patch("ibn_mavlink.pixhawk_bridge.node.MAVLinkClient")
    @patch("ibn_mavlink.pixhawk_bridge.node.MavlinkTranslator.to_attitude")
    def test_tick_attitude_flow(
        self,
        mock_translate,
        mock_client_class,
        mock_logger,
        valid_pixhawk_config,
        sample_attitude_msg,
    ):
        mock_logger.return_value = MagicMock()

        mock_client = MagicMock()
        mock_client.get_latest.side_effect = (
            lambda t: sample_attitude_msg
            if t == "ATTITUDE"
            else None
        )
        mock_client_class.return_value = mock_client

        ros_msg = MagicMock()
        mock_translate.return_value = ros_msg

        global_pub = MagicMock()
        attitude_pub = MagicMock()
        init_pub = MagicMock()

        with patch.object(
            PixhawkTelemetry,
            "create_publisher",
            side_effect=[global_pub, attitude_pub, init_pub],
        ), patch.object(PixhawkTelemetry, "create_timer"):

            node = PixhawkTelemetry(valid_pixhawk_config)
            node._tick()

        mock_translate.assert_called_once_with(node, sample_attitude_msg)
        attitude_pub.publish.assert_called_once_with(ros_msg)


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

        global_pub = MagicMock()
        attitude_pub = MagicMock()
        init_pub = MagicMock()

        with patch.object(
            PixhawkTelemetry,
            "create_publisher",
            side_effect=[global_pub, attitude_pub, init_pub],
        ), patch.object(PixhawkTelemetry, "create_timer"):

            node = PixhawkTelemetry(valid_pixhawk_config)

            node._init_position = MagicMock()
            node._publish_init_position()

        init_pub.publish.assert_called_once_with(node._init_position)
        assert node._init_published is True
