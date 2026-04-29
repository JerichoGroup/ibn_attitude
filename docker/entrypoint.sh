#!/bin/bash
set -e

source /opt/ros/galactic/setup.bash

cd /root/dev/src

echo "[entrypoint] building workspace..."
rm -rf build install log

# colcon build --symlink-install
colcon build

source ~/dev/src/install/setup.bash

exec "$@"
