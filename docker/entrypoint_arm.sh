#!/bin/bash
set -e

echo "[startup] sourcing ROS..."

source /opt/ros/galactic/install/setup.bash

echo "[startup] sourcing workspace..."

source /root/dev/install/setup.bash

echo "[startup] launching..."

exec ros2 launch ibn_mavlink pixhawk_bridge_launch.py

echo "[startup] done."