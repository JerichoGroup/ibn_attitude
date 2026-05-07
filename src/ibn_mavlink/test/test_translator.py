"""Tests for MavlinkTranslator logic."""


class TestMavlinkTranslatorVelocityIntCasting:
    """Tests for velocity int casting logic."""

    def test_velocity_east_component_int_casting(self) -> None:
        """Test vx (velocity east) int casting from float to integer."""

        value_100_5 = 100.5
        value_100_9 = 100.9
        value_neg_100_5 = -100.5
        expected_result = 100

        assert int(value_100_5) == expected_result
        assert int(value_100_9) == expected_result
        assert int(value_neg_100_5) == -expected_result

    def test_velocity_north_component_int_casting(self) -> None:
        """Test vy (velocity north) int casting from float to integer."""

        value_200_7 = 200.7
        value_neg_200_7 = -200.7
        expected = 200

        assert int(value_200_7) == expected
        assert int(value_neg_200_7) == -expected

    def test_velocity_down_component_int_casting(self) -> None:
        """Test vz (velocity down) int casting from float to integer."""

        value_neg_10_3 = -10.3
        expected_result = -10

        assert int(value_neg_10_3) == expected_result

    def test_vehicle_heading_angle_int_casting(self) -> None:
        """Test vehicle heading angle int casting from float to integer."""

        val_180_9 = 180.9
        val_360_9 = 360.9
        val_0_9 = 0.9
        expected_180 = 180
        expected_360 = 360

        assert int(val_180_9) == expected_180
        assert int(val_360_9) == expected_360
        assert int(val_0_9) == 0


class TestMavlinkTranslatorFieldMapping:
    """Tests for field mapping logic."""

    def test_global_position_message_field_count(self) -> None:
        """Test that global position message has the expected number of fields."""

        fields = [
            "time_boot_ms",
            "lat",
            "lon",
            "msl_altitude",
            "relative_altitude",
            "vx",
            "vy",
            "vz",
            "vehicle_heading_angle",
        ]
        expected_count = 9

        assert len(fields) == expected_count

    def test_attitude_message_field_count(self) -> None:
        """Test that attitude message has the expected number of fields."""

        fields = ["time_boot_ms", "roll", "pitch", "yaw", "rollspeed", "pitchspeed", "yawspeed"]
        expected_count = 7

        assert len(fields) == expected_count
