"""Launch files for ibn_mavlink."""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
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

    return LaunchDescription([
        pixhawk_node,
        gps_node
    ])