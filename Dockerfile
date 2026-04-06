ARG BASE_IMAGE=dustynv/ros:galactic-ros-base-l4t-r32.4.4
FROM --platform=linux/arm64/v8 ${BASE_IMAGE} AS build

ENV DEBIAN_FRONTEND=noninteractive \
	SHELL=/bin/bash
SHELL ["/bin/bash", "-c"] 

WORKDIR /tmp

# Locale
RUN locale-gen en_US en_US.UTF-8 && \
	update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
ENV LANG=en_US.UTF-8

# Clean ROS2 apt sources (these are expired onces that prevents apt-get update from working))
RUN rm -f /etc/apt/sources.list.d/ros2* && \
	rm -f /etc/apt/sources.list.d/ros-latest.list

# Install dependencies/tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
		build-essential \
		cmake \
		git \
		python3-pip \
		python3-cffi \
		pkg-config \
		vim tmux gdb \
		iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
	toml \
	pyserial \
	jetson-stats \
	pymavlink

WORKDIR /root/dev

ARG GITHUB_TOKEN=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
ARG TAG="dev"

# Clone needed repos
RUN mkdir src && \
	git clone --branch=${TAG} --depth 1 https://${GITHUB_TOKEN}@github.com/JerichoGroup/ibn_attitude.git src/ibn_attitude && \
	git clone --branch=${TAG} --depth 1 https://${GITHUB_TOKEN}@github.com/JerichoGroup/interfaces.git src/interfaces

# Build ROS2 workspace
RUN . /opt/ros/${ROS_DISTRO}/install/setup.sh && \
	colcon build --symlink-install --cmake-args "-DBUILD_TESTING=OFF"


# ==================== RUNTIME IMAGE ====================
FROM nvcr.io/nvidia/l4t-base:r32.4.4

COPY --from=build / /

ENV DEBIAN_FRONTEND=noninteractive \
	SHELL=/bin/bash \
	ROS_DISTRO=galactic \
	ROS_ROOT=/opt/ros/galactic

WORKDIR /root/dev/

ENTRYPOINT ["/bin/bash", "-i"]
CMD ["bash"]
