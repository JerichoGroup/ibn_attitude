#!/bin/bash
set -e

source /opt/ros/galactic/install/setup.bash

cd /root/dev/src

echo "[entrypoint] building workspace..."

rm -rf build install log

colcon build

source install/setup.bash

exec "$@"
