#!/bin/bash
set -e

source /opt/ros/galactic/setup.bash

cd /root/dev

echo "[entrypoint] building workspace..."
rm -rf build install log

colcon build --symlink-install

source install/setup.bash

exec "$@"