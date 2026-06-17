#!/bin/bash
set -e

echo "[startup] sourcing ROS and workspace..."
source /opt/ros/galactic/install/setup.bash
source /root/dev/install/setup.bash

echo "[startup] launching..."
exec ros2 launch ibn_mavlink pixhawk_bridge_launch.py
