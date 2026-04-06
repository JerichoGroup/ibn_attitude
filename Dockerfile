#
# this dockerfile roughly follows the 'Install ROS From Source' procedures from:
#   https://docs.ros.org/en/galactic/Installation/Ubuntu-Development-Setup.html
#
ARG BASE_IMAGE=dustynv/ros:galactic-ros-base-l4t-r32.4.4
FROM --platform=linux/arm64/v8 ${BASE_IMAGE} AS build

ENV DEBIAN_FRONTEND=noninteractive \
	SHELL=/bin/bash
SHELL ["/bin/bash", "-c"] 

WORKDIR /tmp

# # change the locale from POSIX to UTF-8
RUN locale-gen en_US en_US.UTF-8 && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
ENV LANG=en_US.UTF-8

# 
# install development packages
#
RUN rm -f /etc/apt/sources.list.d/ros2* && rm -f /etc/apt/sources.list.d/ros-latest.list
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
		build-essential \
		cmake \
		git \
		pkg-config \
		yasm \
		nano \
		libbullet-dev \
		libjpeg-dev libpng-dev libtiff-dev \
		libavcodec-dev libavformat-dev libswscale-dev libavresample-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libxvidcore-dev x264 libx264-dev libfaac-dev libmp3lame-dev libtheora-dev \
		libfaac-dev libmp3lame-dev libvorbis-dev \
		libopencore-amrnb-dev libopencore-amrwb-dev \
		libdc1394-22 libdc1394-22-dev libxine2-dev libv4l-dev v4l-utils \
		libgtk-3-dev libtbb-dev libatlas-base-dev gfortran libprotobuf-dev protobuf-compiler libgoogle-glog-dev libgflags-dev libgphoto2-dev libhdf5-dev doxygen \ 
		libyaml-cpp-dev qt5-default libgdal-dev libtinyxml2-dev libcunit1-dev \
		python3-cffi \
		vim gdb tmux iputils-ping \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN pip3 install --no-cache-dir protobuf==3.15.1 pyserial hydra-core==1.3.2 jetson-stats

ENV PATH="/usr/local/cuda-10.0/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
	LD_LIBRARY_PATH="/usr/local/cuda-10.0/targets/aarch64-linux/lib:/usr/lib/aarch64-linux-gnu/tegra:/usr/lib/aarch64-linux-gnu"

COPY cuda-debs /home/cuda-debs
RUN mkdir -p /usr/local/cuda-10.0/targets/aarch64-linux/lib && \
	rm /usr/local/cuda && \
	ln -s /usr/local/cuda-10.0 /usr/local/cuda && \
	dpkg -i /home/cuda-debs/* && \
	rm -rf /home/cuda-debs/

RUN mkdir -p /root/dev
WORKDIR "/root/dev"

RUN git clone --branch=v2.1.0 --depth 1 https://github.com/yse/easy_profiler.git && \
	cd easy_profiler && mkdir build && cd build && cmake .. && \
	make -j7 install

RUN git clone --branch=v2.3 --depth 1 https://github.com/geographiclib/geographiclib.git && \
	cd geographiclib && \
	find . -name "CMakeLists.txt" -exec sed -i 's/\(cmake_minimum_required\s*(VERSION\s*\)\(.*\))/\13.10.0)/' {} + && \
	mkdir build && cd build && cmake .. && \
	make -j7 install

RUN git clone --branch=v3.6.0 --depth 1 https://github.com/taskflow/taskflow.git && \
	cd taskflow && \
	find . -name "CMakeLists.txt" -exec sed -i 's/\(cmake_minimum_required\s*(VERSION\s*\)\(.*\))/\13.10.0)/' {} + && \
	mkdir build && cd build && cmake .. -DTF_BUILD_TESTS=OFF -DTF_BUILD_EXAMPLES=OFF && \
	make -j7 install

RUN git clone --branch=3.4 --depth 1 https://gitlab.com/libeigen/eigen.git && \
	cd eigen && \
	mkdir build && cd build && cmake .. && \
	make -j7 install

RUN git clone --branch=v1.12.0 --depth 1 https://github.com/gabime/spdlog.git && \
	cd spdlog && \
	mkdir build && cd build && cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr .. && \
	make -j7 install

RUN rm -rf easy_profiler geographiclib taskflow eigen spdlog

COPY opencv-deb /home/opencv-deb
RUN apt-get purge -y '*opencv*' || echo "previous OpenCV installation not found" && \
	dpkg -i --force-depends /home/opencv-deb/*.deb && \
    apt-get update && \
    apt-get install -y -f --no-install-recommends && \
    dpkg -i /home/opencv-deb/*.deb && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

ARG GITHUB_TOKEN=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
ARG TAG="v0.4.0"

RUN	git clone --branch=${TAG} --depth 1 https://${GITHUB_TOKEN}@github.com/JerichoGroup/IBN.git && \
	cd IBN && mkdir build && cd build && \
	cmake .. && \
	make install -j && \
	cd ../ && \
	rm -rf build

RUN mv IBN ../ && \
	mkdir src && \
	git clone --branch=${TAG} --depth 1 https://${GITHUB_TOKEN}@github.com/JerichoGroup/ibn_ros.git src/ibn_ros && \
	git clone --branch=${TAG} --depth 1 https://${GITHUB_TOKEN}@github.com/JerichoGroup/interfaces.git src/interfaces && \
	git clone --branch=${TAG} --depth 1 https://${GITHUB_TOKEN}@github.com/JerichoGroup/alexmos-gimbal.git src/alexmos-gimbal && \
	mkdir -p src/ibn_utils/scripts && wget --header "Authorization: token ${GITHUB_TOKEN}" -O src/ibn_utils/scripts/test.yaml \
			https://raw.githubusercontent.com/JerichoGroup/ibn_utils/${TAG}/scripts/test.yaml && \
	. /opt/ros/${ROS_DISTRO}/install/setup.sh && colcon build --symlink-install --cmake-args "-DBUILD_TESTING=OFF"

# remove some static libraries to reduce image size
RUN rm -rf /usr/lib/aarch64-linux-gnu/libcudnn_static_v7.a \
		   /usr/lib/aarch64-linux-gnu/libnvinfer_static.a \
		   /usr/local/cuda/lib64/libcufft_static.a \
		   /usr/local/cuda/lib64/libcufft_static_no_callback.a \
		   /usr/local/cuda/lib64/libcublas_static.a \
		   /usr/local/cuda/lib64/libcurand_static.a

# setup entrypoints
COPY ./entrypoints/* /root/.
RUN cat /root/bashrc-append.bash >> /root/.bashrc

FROM nvcr.io/nvidia/l4t-base:r32.4.4
COPY --from=build / /

ENV DEBIAN_FRONTEND=noninteractive \
	SHELL=/bin/bash
SHELL ["/bin/bash", "-c"] 

WORKDIR "/root/dev/"
ENV PATH="/usr/local/cuda-10.0/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
	LD_LIBRARY_PATH="/usr/local/cuda-10.0/targets/aarch64-linux/lib:/usr/lib/aarch64-linux-gnu/tegra:/usr/lib/aarch64-linux-gnu" \
	DEBIAN_FRONTEND=noninteractive \
	SHELL=/bin/bash \
	ROS_DISTRO=galactic \
	ROS_ROOT=/opt/ros/galactic

CMD ["bash"]
ENTRYPOINT ["/bin/bash", "-i", "-c", "/root/entrypoint.sh"]

