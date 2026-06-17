#!/bin/bash
set -e

echo "[startup] sourcing ROS and workspace..."
source /opt/ros/galactic/install/setup.bash
source /root/dev/install/setup.bash

echo "[startup] launching GPS node..."
exec ros2 run ibn_mavlink gps_injection
