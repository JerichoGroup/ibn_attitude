# syntax=docker/dockerfile:1.4
FROM ubuntu:20.04 AS build

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# -------------------- Locale --------------------
RUN apt-get update && apt-get install -y locales && \
    locale-gen en_US en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

ENV LANG=en_US.UTF-8

# -------------------- Base tools --------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3-pip \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    pkg-config \
    vim tmux gdb \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# -------------------- ROS2 Galactic --------------------
RUN apt-get update && apt-get install -y curl gnupg2 lsb-release && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add - && \
    echo "deb http://packages.ros.org/ros2/ubuntu focal main" > /etc/apt/sources.list.d/ros2.list && \
    apt-get update && apt-get install -y \
    ros-galactic-ros-base \
    python3-colcon-common-extensions \
    python3-rosdep \
    && rm -rf /var/lib/apt/lists/*

ENV ROS_DISTRO=galactic
ENV ROS_ROOT=/opt/ros/galactic

RUN rosdep init || true && rosdep update

# -------------------- Python deps --------------------
RUN pip3 install --no-cache-dir \
    "Cython<3.0" \
    pyserial \
    toml \
    pymavlink==2.4.40

# -------------------- Workspace --------------------
WORKDIR /root/dev

ARG INTERFACES_TAG="v0.5.0"

RUN --mount=type=secret,id=gh_token \
    GITHUB_TOKEN=$(cat /run/secrets/gh_token) && \
    mkdir -p src && \
    git clone --branch=${INTERFACES_TAG} --depth 1 \
    https://${GITHUB_TOKEN}:x-oauth-basic@github.com/JerichoGroup/interfaces.git src/interfaces

COPY ./src/ibn_mavlink /root/dev/src/ibn_mavlink

# -------------------- Build --------------------
RUN source /opt/ros/$ROS_DISTRO/setup.bash && \
    rosdep install --from-paths src --ignore-src -r -y

# ==================== RUNTIME ====================
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive \
    ROS_DISTRO=galactic \
    ROS_ROOT=/opt/ros/galactic

COPY --from=build / /

WORKDIR /root/dev
SHELL ["/bin/bash", "-c"]

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
