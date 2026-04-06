"""This script connects to a pixhawk via MAVLink, and publishes the """

import time
from math import degrees

from pymavlink import mavutil
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray


def connect_pixhawk(device="/dev/ttyACM0", baud=57600):
    """
    Connect to Pixhawk via MAVLink and return the connection object.
    This function can be imported and used from other files.
    """
    print(f"Connecting to Pixhawk on {device} at {baud} baud...")
    mav = mavutil.mavlink_connection(device, baud=baud)
    mav.wait_heartbeat()
    print("Pixhawk connection established.")
    return mav


class PixhawkPublisher(Node):
    def __init__(self, mav):
        super().__init__("pixhawk_ros2_bridge")

        self.mav = mav

        # Publishers
        self.pub_rpy = self.create_publisher(Float32MultiArray, "/drone_rpy", 10)
        self.pub_speeds = self.create_publisher(Float32MultiArray, "/drone_speeds", 10)

        # Timer to poll MAVLink at 50 Hz
        self.timer = self.create_timer(0.02, self.timer_callback)

    def timer_callback(self):
        msg = self.mav.recv_match(type=["ATTITUDE"], blocking=False)

        if msg is None:
            return

        # Extract angles (radians → degrees)
        roll = degrees(msg.roll)
        pitch = degrees(msg.pitch)
        yaw = degrees(msg.yaw)

        # Extract angular speeds (radians/sec → degrees/sec)
        rollspeed = degrees(msg.rollspeed)
        pitchspeed = degrees(msg.pitchspeed)
        yawspeed = degrees(msg.yawspeed)

        # Publish RPY
        rpy_msg = Float32MultiArray()
        rpy_msg.data = [roll, pitch, yaw]
        self.pub_rpy.publish(rpy_msg)

        # Publish angular speeds
        speed_msg = Float32MultiArray()
        speed_msg.data = [rollspeed, pitchspeed, yawspeed]
        self.pub_speeds.publish(speed_msg)


def main():
    # Connect to Pixhawk
    mav = connect_pixhawk()

    # Start ROS2
    rclpy.init()
    node = PixhawkPublisher(mav)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
