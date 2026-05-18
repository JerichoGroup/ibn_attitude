#!/bin/bash
set -e

echo "[entrypoint] sourcing ROS..."

source /opt/ros/galactic/install/setup.bash

cd /root/dev/src

echo "[entrypoint] cleaning workspace..."

rm -rf build install log

echo "[entrypoint] building workspace..."

colcon build

echo "[entrypoint] sourcing workspace..."

source /root/dev/src/install/setup.bash

echo "[entrypoint] starting command..."

exec "$@"