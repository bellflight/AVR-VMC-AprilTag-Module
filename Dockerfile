FROM docker.io/library/python:3.10 AS poetry-exporter

WORKDIR /work

RUN python -m pip install poetry poetry-plugin-export

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN poetry export -o requirements.txt

# https://ngc.nvidia.com/catalog/containers/nvidia:l4t-ml
# Use the ML version because it already has precompiled OpenCV
FROM nvcr.io/nvidia/l4t-ml:r32.6.1-py3

ENV PYTHON_VERSION=3.10

ENV DEBIAN_FRONTEND=noninteractive

# Fix numpy issues
ENV OPENBLAS_CORETYPE=AARCH64

# Install Python newer than 3.6
# https://github.com/deadsnakes/issues/issues/251
WORKDIR /work/
RUN apt-get update -y
RUN apt-get install -y tzdata curl ca-certificates
RUN curl -L -O https://github.com/bellflight/AVR-Python-arm-deb/releases/download/release/libpython3.10-minimal_3.10.11-1+bionic1_arm64.deb \
 && curl -L -O https://github.com/bellflight/AVR-Python-arm-deb/releases/download/release/libpython3.10-stdlib_3.10.11-1+bionic1_arm64.deb \
 && curl -L -O https://github.com/bellflight/AVR-Python-arm-deb/releases/download/release/python3.10-distutils_3.10.11-1+bionic1_all.deb \
 && curl -L -O https://github.com/bellflight/AVR-Python-arm-deb/releases/download/release/python3.10-lib2to3_3.10.11-1+bionic1_all.deb \
 && curl -L -O https://github.com/bellflight/AVR-Python-arm-deb/releases/download/release/python3.10-minimal_3.10.11-1+bionic1_arm64.deb \
 && curl -L -O https://github.com/bellflight/AVR-Python-arm-deb/releases/download/release/python3.10_3.10.11-1+bionic1_arm64.deb
RUN dpkg -i libpython3.10-minimal_3.10.11-1+bionic1_arm64.deb \
 && dpkg -i libpython3.10-stdlib_3.10.11-1+bionic1_arm64.deb \
 && dpkg -i python3.10-lib2to3_3.10.11-1+bionic1_all.deb \
 && dpkg -i python3.10-distutils_3.10.11-1+bionic1_all.deb \
 && dpkg -i python3.10-minimal_3.10.11-1+bionic1_arm64.deb \
 && dpkg -i python3.10_3.10.11-1+bionic1_arm64.deb \
 && rm *.deb
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python${PYTHON_VERSION} \
 && python${PYTHON_VERSION} -m pip install pip wheel setuptools --upgrade

WORKDIR /app

# Copy libraries
RUN apt-get install -y libssl-dev
COPY src/c/libraries c/libraries

# Install paho C library
RUN cd c/libraries/paho.mqtt.c \
 && cmake -Bbuild -H. -DPAHO_BUILD_STATIC=ON -DPAHO_WITH_SSL=ON -DPAHO_HIGH_PERFORMANCE=ON \
 && cmake --build build/ --target install \
 && ldconfig

# Install paho C++ library
RUN cd c/libraries/paho.mqtt.cpp \
 && cmake -Bbuild -H. -DPAHO_BUILD_STATIC=ON \
 && cmake --build build/ --target install \
 && ldconfig

# another source:
# https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_apriltag/tree/release-ea3

# RUN git clone https://github.com/NVIDIA-AI-IOT/isaac_ros_apriltag \
#  && cd isaac_ros_apriltag \
#  && git checkout v0.9.0-ea1 \
#  && cp -r isaac_ros_apriltag/nvapriltags/lib_aarch64_jetpack44 ../c/libraries/lib_aarch64_jetpack44

RUN wget https://developer.nvidia.com/isaac/download/third_party/april_tags_v5_jp44_nano-tar-xz \
 && tar -xf april_tags_v5_jp44_nano-tar-xz --directory c/libraries \
 && rm april_tags_v5_jp44_nano-tar-xz

# Build the april tag application
COPY src/c/src c/src
COPY src/c/CMakeLists.txt c/CMakeLists.txt
RUN mkdir -p c/build \
 && cd c/build \
 && cmake .. \
 && make -j

COPY --from=poetry-exporter /work/requirements.txt requirements.txt
RUN python${PYTHON_VERSION} -m pip install -r requirements.txt

COPY src .
RUN chmod +x ./docker-entrypoint.sh

RUN rm /usr/bin/python3 && ln -s /usr/bin/python${PYTHON_VERSION} /usr/bin/python3
CMD ["./docker-entrypoint.sh"]