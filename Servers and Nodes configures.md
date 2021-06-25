# Servers and Nodes configures

* wifi network: Chaos

* robot master: 192.168.28.11 , login: ubuntu/abc123!@# , network: virtual machine

* robot nodes:

  * tb3_0: 192.168.28.81 , ssh: waffle/123456 , wifi: Chaos
    * wifi enabler: 192.168.28.82 ssh: p1/123456 (wifi: Chaos)
    * bt_enabler_0: 192.168.28.83 ssh:pi/123456 (wifi: Chaos)
      * to set the static ip address for pi, please refer [for pi](https://electrondust.com/2017/11/25/setting-raspberry-pi-wifi-static-ip-raspbian-stretch-lite/)
  * tb3_1: 192.168.28.149  ssh: robot/robot , wifi: Chaos
  * rosbot1: 192.168.28.77 ssh: husarion/husarion, wifi: Robot

* Backends

  * zk server: 192.168.12.225, 192.168.12.220, 192.168.12.222
    ssh ubuntu@xxx.xxx.xxx.xxx

    ```
    # To Launch
    cd /usr/zookeeper/zookeeper-3.4.14/bin
    sh zkServer.sh start 
    ```

  * Kafka: 192.168.12.146, 192.168.12.2, 192.168.12.149

    ssh ubuntu@xxx.xxx.xxx.xxx

    ```
    # To Launch
    sudo -i
    cd /usr/kafka/kafka_2.13-2.4.1/
    bin/kafka-server-start.sh config/server.properties &
    ```

    ```
    # to check the topic
    cd /usr/kafka/kafka_2.13-2.4.1/
    bin/kafka-console-consumer.sh --topic audio-test --from-beginning --bootstrap-server 192.168.12.146:9092
    ```

    

  * redis server: 192.168.12.146

    ```
    # To Launch
    cd ~/redis-6.0.8/
    src/redis-server redis.conf
    ```

  * Task Scheduler: 192.168.12.146
    * [Github](https://github.com/orange-cn/patrolling-robot.git) (**mainained the latest version, CI to 146 machine with domainname: "discovery.orangelabschina.cn"**)
    * Gitlab: https://gitlab.tech.orange/kun.qian/robot
    * used for the management of robots, sites, inspections...

    ```
    # To Launch
    sudo -i
    cd /home/ubuntu/robot
    bash start.sh
    ```
  * Task Observer: 192.168.12.146
    * [Github](https://github.com/orange-cn/inspection-observer.git) (**mainained the latest version, CI to 146 machine with domainname: "discovery.orangelabschina.cn"**)
    * Gitlab: 
    * user for monitor the task status
    ```
    # To Launch
    cd /home/ubuntu/inspection-observer
    bash start.sh
    ```
    
  * Yolo Server: 192.168.23.1(internet IP:123.127.237.185) 
    * used for visual recognition request from visual sniffer
    ```
    ssh si@192.168.23.1
    #if rejected
    ## copy public key from ~/.ssh/authorized_keys
    ssh sw@192.168.23.1
    su si  #password: abc123!@#
    nano ~/.ssh/authorized_keys
    ## paste the copies public keys
    eixt
    
    cd ~/yolo-server
    nohup build/yoloserver &
    ```

* Sniffers

  * visual on robot tb3_0

    ```
    ssh ubuntu@192.168.28.28 -> qwe123!@#
    
    cd visual
    
    #To change robotid
    cd ~/visual/video_broker
    vim main.py
    change robot_id = 'tb3_0'
    
    #restart the camera and orchesrator service:
    sudo systemctl start depthcam
    sudo systemctl start orch
    
    #Check depth-cam work:
    http://192.168.28.28:9038/captureId
    
    #start yolo server for visual recognition
    ssh kunqian@192.168.12.121 #passwd: abc123!@#
    cd ~/yolo-server
    ###if need to build the excutable server
    mkdir build3
    cd build3
    cmake .. -DWITH_CUDA=OFF
    make
    ###if need to build the excutable server
    cd ~/yolo-server
    nohup build3/yoloserver &
    ```

    

  * audio on robot x

    ```
    ssh pi@192.168.28.29` -> qwe123!@#
    
    docker ps
    #
    #**dcase2018t2vggish:1.4**: this docker image(sound recognition) is #provides by stephane.louisditpicard@orange.com
    #- **audio_broker:v0**: this docker image is used for receiving the #recognition result and sending the result to Kafka
    #**these modules have been set up as system daemon service (auto start when reboot)**.
    
    #to change the robot id
    cd ~/audio_broker
    vim run_broker.sh
    modify ROBOT_ID in "docker run --net host -e ROBOT_ID='fixed-testbedbj-audio01' audio_broker:v0"
    
    #To check the result
    check topic "audio-test" in 192.168.12.146
    
    #To enter into the container
    systemctl start docker
    docker exec -it container_id bash
    ```
