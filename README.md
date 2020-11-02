# 1. Hosts

* wifi network: Chaos
* robot master: 192.168.28.11 , login: sw/abc123!@# , wifi: Cloud
* robot nodes:
  * tb3_0: 192.168.28.81 , ssh: waffle/123456 , wifi: Chaos
    * wifi enabler: 192.168.28.82 ssh: p1/123456 (wifi: Chaos)
    * bt_enabler_0: 192.168.28.83 ssh:pi/123456 (wifi: Chaos)
  * tb3_1: 192.168.28.149  ssh: robot/robot , wifi: Chaos
  * ros2p_0: 192.168.28.77 ssh: husarion/husarion, wifi: Chaos
  
* to set the static ip address for pi, please refer [for pi](https://electrondust.com/2017/11/25/setting-raspberry-pi-wifi-static-ip-raspbian-stretch-lite/)

# 2. Install

## 2.1. Robot Master Node

* Install ROS1

  if need to change apt source and rosdep source, please refer to 

  ```
  sudo sh -c '. /etc/lsb-release && echo "deb http://mirrors.ustc.edu.cn/ros/ubuntu/ $DISTRIB_CODENAME main" > /etc/apt/sources.list.d/ros-latest.list'
  ```

  * install ROS1 from sources:

```
$ sudo apt-get update
$ sudo apt-get upgrade
$ wget https://raw.githubusercontent.com/ROBOTIS-GIT/robotis_tools/master/install_ros_kinetic.sh && chmod 755 ./install_ros_kinetic.sh && bash ./install_ros_kinetic.sh
$ rosedep update
##Install Dependent ROS 1 Packages
$ sudo apt-get install ros-kinetic-joy ros-kinetic-teleop-twist-joy ros-kinetic-teleop-twist-keyboard ros-kinetic-laser-proc ros-kinetic-rgbd-launch ros-kinetic-depthimage-to-laserscan ros-kinetic-rosserial-arduino ros-kinetic-rosserial-python ros-kinetic-rosserial-server ros-kinetic-rosserial-client ros-kinetic-rosserial-msgs ros-kinetic-amcl ros-kinetic-map-server ros-kinetic-move-base ros-kinetic-urdf ros-kinetic-xacro ros-kinetic-compressed-image-transport ros-kinetic-rqt-image-view ros-kinetic-gmapping ros-kinetic-navigation ros-kinetic-interactive-markers

$ cd ~/catkin_ws/src/
$ git clone https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
$ git clone -b kinetic-devel https://github.com/ROBOTIS-GIT/turtlebot3.git
$ cd ~/catkin_ws && catkin_make

$ sudo apt-get install ros-kinetic-hector-mapping

$ nano .bashrc

source /opt/ros/kinetic/setup.bash
source ~/catkin_ws/devel/setup.bash
export ROS_MASTER_URI=http://192.168.27.1:11311
export ROS_HOSTNAME=192.168.27.1
export TURTLEBOT3_MODEL=waffle_pi
```

* install ROS from packages
  * ROS Kinetic: refer [Ubuntu install of ROS Kinetic](http://wiki.ros.org/kinetic/Installation/Ubuntu)
  * ROS Melodic: refer [Ubuntu install of ROS Melodic](http://wiki.ros.org/melodic/Installation/Ubuntu)

## 2.2 Install Rosbot 2.0 support

### update environment and install neccesary packages

```
mkdir -p ~/ros_workspace/src
cd ~/ros_workspace/src
catkin_init_workspace
cd ..
catkin_make

cd src
git clone https://github.com/husarion/rosbot_description.git
git clone https://github.com/husarion/tutorial_pkg.git

sudo apt update
sudo apt install python-rosdep2
sudo rosdep init
rosdep update
#Install dependencies
rosdep install --from-paths src --ignore-src -r -y

#compile
cd ~/ros_workspace
catkin_make

#install enviroment
nano ~/.bashrc
# add: export ~/ros_workspace/devel/setup.sh
source ~/.bashrc


### install slam and navigation launch

sudo apt-get install ros-kinetic-robot-localization

#copy rosbot config yamls to multirobot_nv package
cd ~/catkin_ws/src/multirobot_nv/param
git clone https://github.com/husarion/tutorial_pkg.git
cd turorial_pkg
mv config/ ../rosbot_param
cd ..
rm -rf turorial_pkg
```

Implementation reference for Rosbot 2.0

1. [map navigation](https://husarion.com/tutorials/ros-tutorials/9-map-navigation/)
2. [config files for movebase](https://github.com/husarion/tutorial_pkg/tree/master/config)

## 2.3 Install robotmaster service

* requirements 

  ```
  $ cd ~ & mkdir projects
  $ cd projects
  $ git clone https://github.com/wdxpz/robotmaster.git
  $ pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "django<2"
  $ pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "djangorestframework<3.10"
  $ pip install -i https://pypi.tuna.tsinghua.edu.cn/simple apscheduler
  $ pip install requests
  
  $ sudo apt-get install libmagickwand-dev
  $ pip install Wand
  
  pip install influxdb
  
  ```

## 2.3 Install ROS launch_robot package

```
$ git clone https://github.com/wdxpz/turtlebot_master_scripts.git
$ catkin_create_pkg multirobot_nv

# copy files from git into ~/catkin_ws/src/multirobot_nv
```





# 2. PreSettings

## 2.1 SLAM

To get more accurate map, **cartographer** methods is recommended:

To install cartographer, see see [ROS 1 SLAM](http://emanual.robotis.com/docs/en/platform/turtlebot3/slam/#ros-1-slam) for how to install cartographer for Kinetic

to use cartographer for SLAM:

```
$ export TURTLEBOT3_MODEL=${TB3_MODEL}
#on turtlebot node
$ roslaunch turtlebot3_bringup turtlebot3_robot.launch
#on turtlebot master
$ roslaunch turtlebot3_teleop turtlebot3_teleop_key.launch
$ roslaunch turtlebot3_slam turtlebot3_slam.launch slam_methods:=cartographer
$ rosrun map_server map_saver -f /save_dir/map

```

### 2.2 Navigation

the default navigation params need to modified to tune the navigation in specific environment. 

* In our case, we intend to make the distance between two adjacent robot checkpoints not too far, so we can make the `sime_time` in `turtlebot3_navigation/param/dwa_local_planner_params_$(model).yaml` smaller, in Bejing office:

```
$roscd turtlebot3_navigation
$cd param
$nano dwa_local_planner_params_waffle_pi.yaml

# Forward Simulation Parameters
  sim_time: 1.5

```

* To avoid obstacle but use limited space in Beijing office, we also modified `turtlebot3_navigation/param/costmap_common_param_$(model).yaml`

```
$roscd turtlebot3_navigation
$cd param
$nano costmap_common_params_waffle_pi.yaml

inflation_radius: 1.0
cost_scaling_factor: 10.0
```

# 3. Requirements

## master node

1. pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "django<2"
2. pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "djangorestframework<3.10"
3. pip install -i https://pypi.tuna.tsinghua.edu.cn/simple apscheduler
4. see [Requirement](createsite/robot_site/readme.md) for  createsite package

## turtlebot node

1. sudo apt-get install ros-<distro>-robot-upstart, replace “<distro>” by your ROS version: kinetic, melodic, …

# 4. Launch robot at turtlebot node

1. Deploy project `launch_robot` in `~/catkin_ws/src`
2. power on to auto launch the robot
2. see usage in [README.md](https://github.com/wdxpz/turtlebot_node_scripts/blob/master/README.md) of project [turtlebot_node_scripts](https://github.com/wdxpz/turtlebot_node_scripts)

# 5. Launch navigation at turtlebot master
1. deploy project `multirobot_nv` in `~/catkin_ws/src`

2. config `startall.launch` file

3. see how-to in [README.md](https://github.com/wdxpz/turtlebot_master_scripts/blob/master/README.md) of project [turtlebot_master_scripts](https://github.com/wdxpz/turtlebot_master_scripts)

4. manually launch anvigation

   ```
   roslaunch multirobot_nv startall.launch
   ```




5. launch by robotmaster service, see it in next section

# 6. robotmaster Service

## 6.1. createsite service

export current map data from map_server node, and save it in local, convert it to jpg and create the site with specific name and the jpg in server.

**required**: map_server node activated by slam or navigation

```
GET http://server_ip:port/createsite/?name=test2&desc=beijing office floor 233&forced=n

#name(required) : site name, string
#desc (optional): site description, string
#forced (optional): forced to overwrited existed site, string(['y', 'yes', 'true'] for True )
```
## 6.2. launch navigation service

```
POST http://server_ip:port/launch/

json body:
{
        'inspection_id': 103,
        'site_id': 'office12'
        'robots': {
            'robot_id1': {
                'org_pos': "(1.4, 10.5, 0)",
                'subtask': "[(1, x1, y1), (2, x2, y2), ...]"
            },
            'robot_id2': {
                'org_pos': "(5.5, 12.5, 0)",
                'subtask': "[(3, x3, y3), (4, x4, y4), ...]"
            },
            'robot_id3': {
                ...
            },
            ...
        }
    }
```

# Run Service with Docker

## On Mac

### Reference [Using ROS with Docker in macOS](https://www.xiaokeyang.com/blog/using_ros_with_docker_in_macos)

### 1. Run roscore in docker container

* start container with port mapping to 11311, 
    * option `-net=host` will not work in MacOS because docker in macOS itself runs inside a virtual machine. The above setting merely shares the same address with the virtual machine rather than the actual host 

```
$ docker run -it --rm --name roscore -p 11311:11311 ros:kinetic-robot bash
```
* in the container, start the roscore

```
$ ./ros_entrypoint.sh 
$ ip=$(hostname -i)
$ export ROS_IP=$ip
$ roscore
```

### 2 Run ros node in another docker container

* start the container

```
$ ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' roscore)
$ docker run -it --rm --name node --env ROS_MASTER_URI=http://$ip:11311 ros:kinetic-robot bash
```
* config the env variables

```
$ ./ros_entrypoint.sh 
$ ip=$(hostname -i)
$ export ROS_IP=$ip
$ echo $ROS_IP
$ echo $ROS_MASTER_URI
```

* run ros app

```
$ rosnode ping /roscore 
```

## On Linux

#### start roscore

```
$ docker run -it --network host --env ROS_IP=192.168.27.1 --rm --name roscore ros:kinetic-robot roscore
```

#### deploy robot master servcie

* start container

  ```
  $sudo docker run -it --network host --env ROS_IP=192.168.27.1 --env ROS_MASTER_URI=http://192.168.27.1:11311 --env TURTLEBOT3_MODEL=waffle_pi --rm --name robotmaster -v /home/sw/projects:/projects ros:kinetic-robot bash
  ```

* install requirements

  ```
  #optional: change ROS apt source
  $ sudo sh -c '. /etc/lsb-release && echo "deb http://mirrors.ustc.edu.cn/ros/ubuntu/ $DISTRIB_CODENAME main" > /etc/apt/sources.list.d/ros-latest.list'
  ```

  

  ```
  $ sudo apt-get update
  $ sudo apt-get install -y ros-kinetic-joy ros-kinetic-teleop-twist-joy ros-kinetic-teleop-twist-keyboard ros-kinetic-laser-proc ros-kinetic-rgbd-launch ros-kinetic-depthimage-to-laserscan ros-kinetic-rosserial-arduino ros-kinetic-rosserial-python ros-kinetic-rosserial-server ros-kinetic-rosserial-client ros-kinetic-rosserial-msgs ros-kinetic-amcl ros-kinetic-map-server ros-kinetic-move-base ros-kinetic-urdf ros-kinetic-xacro ros-kinetic-compressed-image-transport ros-kinetic-rqt-image-view ros-kinetic-gmapping ros-kinetic-navigation ros-kinetic-interactive-markers
  
  $ cd ~ & mkdir catkin_ws 
  $ cd catkin_ws
  $ mkdir src 
  $ cd src
  $ git clone https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
  $ git clone -b kinetic-devel https://github.com/ROBOTIS-GIT/turtlebot3.git
  $ cd ~/catkin_ws && catkin_make
  
  $ sudo apt-get install -y python-pip
  $ pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "django<2"
  $ pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "djangorestframework<3.10"
  $ pip install -i https://pypi.tuna.tsinghua.edu.cn/simple apscheduler
  $ pip install requests
  $ sudo apt-get install libmagickwand-dev
  $ pip install Wand
  $ pip install influxdb
  ```

* clone project

  ```
  $ cd ~
  $ mkdir projects
  $ cd projects
  $ git clone https://github.com/wdxpz/robotmaster.git robotmaster
  $ cd ~/catkin_ws/src
  $ git clone https://github.com/wdxpz/turtlebot_master_scripts.git multirobot_nv
  ```

  

