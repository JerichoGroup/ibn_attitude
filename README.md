# ibn_attitude
This repository contains a python script that connects to a pixhawk that runs ArduCopter
It then reads live from the drone certain params that are of interest to ibn, and publishes them over ros2
The script runs from a docker that is built for ARM64 architecture
The docker is based on the ibn_ros docker file

* Config:  
the config allows to change the topic names and the frequency to poll MAVLink.  
with defaults being:
    ```bash
    attitude_topic_name = "/mavlink/attitude"
    altitude_topic_name = "/mavlink/altitude"
    hz = 50
    ```

* Output:
  &nbsp;

    a topic publishing the attitude of the drone    
    msg:
    ```bash
    Metadata metadata
    std_msgs/Header header
    uint32 time_boot_ms
    float64 roll
    float64 pitch
    float64 yaw
    float64 rollspeed
    float64 pitchspeed
    float64 yawspeed
    ```
  
    a topic publishing the altitude of the drone  
    msg: 
    ```bash
    std_msgs/Header header
    Metadata metadata
    float64 alt
    ```

* Docker
  &nbsp;

    build the docker:  
    ```
    docker buildx create --use
    docker buildx build \
      --platform linux/arm64 \
      --secret id=gh_token,src=./ibn_token_secret \
      -t pixhawk_bridge:ibn .
    ```

    
    run the docker:  
    ```
    docker run
    ```
