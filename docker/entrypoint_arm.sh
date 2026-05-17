#!/bin/bash
set -e

source /opt/ros/galactic/install/setup.bash
source /root/dev/src/install/setup.bash

echo "[entrypoint] ROS environment ready"

exec "$@"