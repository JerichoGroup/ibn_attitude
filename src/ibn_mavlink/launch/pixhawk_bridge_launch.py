"""Launch files for ibn_mavlink."""

from launch_ros.actions import Node

from launch import LaunchDescription  # type: ignore[attr-defined]


def generate_launch_description() -> LaunchDescription:
    """Generate launch description."""

    pixhawk_node = Node(
        package="ibn_mavlink",
        executable="pixhawk_bridge",
        name="pixhawk_bridge",
        output="screen",
    )

    gps_node = Node(
        package="ibn_mavlink",
        executable="gps_injection",
        name="gps_injection",
        output="screen",
    )

    return LaunchDescription([pixhawk_node, gps_node])
