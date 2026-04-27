from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    pixhawk_node = Node(
        package="ibn_attitude",
        executable="pixhawk_telemetry",
        name="pixhawk_telemetry",
        output="screen",
    )

    gps_node = Node(
        package="ibn_attitude",
        executable="gps_injection",
        name="gps_injection",
        output="screen",
    )

    return LaunchDescription([
        pixhawk_node,
        gps_node
    ])