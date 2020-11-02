# Install ROS
## 网络时间协议(NTP，Network Time Protocol)
* 设置方法是安装chrony之后用ntpdate命令指定ntp服务器即 可。
* 这样一来会表示服务器和当前计算机之间的时间误差，进而会调到服务器的时间。这 就是通过给不同的PC指定相同的NTP服务器，将时间误差缩短到最小的方法。

```
$ sudo apt-get install -y chrony ntpdate 
$ sudo ntpdate -q ntp.ubuntu.com
```
## change ROS apt source
```
sudo sh -c '. /etc/lsb-release && echo "deb http://mirrors.ustc.edu.cn/ros/ubuntu/ $DISTRIB_CODENAME main" > /etc/apt/sources.list.d/ros-latest.list'
```
then, follow official guides to install ROS

## change default python from 2 to 3
**seems not good to change python 2 to 3 because ROS catkin_make uses cmake binded with python2, once the system default python is changed to python3, catkin_make will not work**
```
update-alternatives --remove python /usr/bin/python2
update-alternatives --install /usr/bin/python python /usr/bin/python3 10
```


# ROS Knowledge 
1. [ROS python client library](http://wiki.ros.org/rospy)
2. [ROS Command](http://wiki.ros.org /ROS/CommandLineTools), [cheatsheet](https://github.com/ros/cheatsheet/releases)

# Operation
## SLAM
1. in remote-pc, open new terminal, run

```
$ roscore
```
2. ssh Turtlebot pc, in terminal, run 

```
$ roslaunch turtlebot3_bringup turtlebot3_robot.launch
```
you will see:

```
[INFO] [1583226443.156238]: --------------------------
[INFO] [1583226443.159682]: Connected to OpenCR board!
[INFO] [1583226443.163006]: This core(v1.2.3) is compatible with TB3 Waffle or Waffle Pi
[INFO] [1583226443.166428]: --------------------------
[INFO] [1583226443.169656]: Start Calibration of Gyro
[INFO] [1583226445.526265]: Calibration End
```

1. in remote-pc, open new terminal, run

```
$ export TURTLEBOT3_MODEL=${TB3_MODEL}
$ roslaunch turtlebot3_slam turtlebot3_slam.launch slam_methods:=gmapping
```
to do visual slam

1. in remote-pc, run 

```
$ export TURTLEBOT3_MODEL=${TB3_MODEL}
$ roslaunch turtlebot3_teleop turtlebot3_teleop_key.launch
```
you will see

```
Control Your TurtleBot3!
  ---------------------------
  Moving around:
          w
     a    s    d
          x

  w/x : increase/decrease linear velocity
  a/d : increase/decrease angular velocity
  space key, s : force stop

  CTRL-C to quit
```
to teleoperate the robot to move

1. save the map, in remote-pc, run 

```
$ rosrun map_server map_saver -f /save_dir
```

**Tips for SLAM**

1. when manually operate the robot, do not to do vigorous movements such as changing the speed too quickly or rotating too fast.

2. the robot should scan every corner of the environment to be measured

3. change slam method, like **Hector**, **Cartographer** 

   ```
   roslaunch turtlebot3_slam turtlebot3_slam.launch slam_methods:=cartographer
   ```

   see [ROS 1 SLAM](http://emanual.robotis.com/docs/en/platform/turtlebot3/slam/#ros-1-slam) for how to install cartographer for Kinetic

   **Hector**, **Cartographer** is better than Gmapping, and **Cartographer** is recommended by paper [Comparison of Various SLAM System for Mbile Robot in an Indoor Environment](https://www.researchgate.net/publication/328007381_Comparison_of_Various_SLAM_Systems_for_Mobile_Robot_in_an_Indoor_Environment)

   **For tuning Cartographer** , refer [Tuning methodology](https://google-cartographer-ros.readthedocs.io/en/latest/tuning.html)

4. For tuning Gmapping, refer: [Tuning Guide]([Tuning Guide](http://emanual.robotis.com/docs/en/platform/turtlebot3/slam/#tuning-guide)). For Gmapping, 5 parameters in `turtlebot3_slam/launch/turtlebot3_gmapping.launch`may be tuned:

   ```
   maxUrange
   map_update_interval
   minimumScore
   linearUpdate
   angularUpdate
   ```

   

## navigation

1. remote pc:

```
$ roscore
```
1. turtulebot pc:

```
$ roslaunch turtlebot3_bringup turtlebot3_robot.launch
```
1. remote pc:

```
#The ${TB3_MODEL} is the name of the model you are using in burger, waffle, waffle_pi
$ export TURTLEBOT3_MODEL=${TB3_MODEL}
$ roslaunch turtlebot3_navigation turtlebot3_navigation.launch map_file:=$HOME/map.yaml

#####
# navigation without rviz
$ roslaunch turtlebot3_navigation amcl.launch map_file:=$HOME/map.yaml
```
**map: when copy map.yaml and map.pgm exported from host1 to host2, it is very important to change the path of image to host2**
```
#image: /home/sw/map.pgm(path in host1)
#
image: /home/waffle/map/map.pgm (path in host2)
****
```
1. Estimate Initial Pose in remote pc:
    * Click the 2D Pose Estimate button.
    * Click on the approxtimate point in the map where the TurtleBot3 is located and drag the cursor to indicate the direction where TurtleBot3 faces.
    * Then move the robot back and forth with tools like the turtlebot3_teleop_keyboard node to collect the surrounding environment information and find out where the robot is currently located on the map.
    * The turtlebot3_teleop_keyboard node used for Estimate Initial Pose should be terminated after use. If it does not, the robot will behave strangely because the topic overlaps with the /cmd_vel topic from the navigation node of the next step.

```
$ export TURTLEBOT3_MODEL=${TB3_MODEL}
$ roslaunch turtlebot3_teleop turtlebot3_teleop_key.launch
```

1. Send Navigation Goal at remote pc:
    * Click the 2D Nav Goal button, in the menu of RViz, a very large green arrow appears. This green arrow is a marker that can specify the destination of the robot. The root of the arrow is the x and y position of the robot, and the orientation pointed by the arrow is the theta direction of the robot
    * Click on a specific point in the map to set a goal position and drag the cursor to the direction where TurtleBot should be facing at the end

## Simulation - Gazebo
1. Gazebo Installation
    * refer [通过Gazebo仿真学TurtleBot3（二）——环境搭建](https://blog.csdn.net/u010853356/article/details/79226764)
    * install TB3 msg, funciton, simulation packages
```
$ mkdir -p ~/catkin_ws/src
$ cd ~/catkin_ws/src
$ git clone https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
$ git clone https://github.com/ROBOTIS-GIT/turtlebot3.git
$ git clone https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git
$ cd ~/catkin_ws
$ rosdep install --from-paths src -i -y
$ catkin_make
```
注意以上命令第7行，采用rosdep install依赖安装的方式，安装了TB3代码中依赖的各种ROS软件包。rosdep install主要基于软件package包目录下package.xml文件中的依赖项关系来安装依赖项，具体说明见ROS官方wiki。
catkin_make编译后，还需要将新工程的ROS环境设置加入~/.bashrc文件，命令如下：

```
$ echo "source ~/catkin_ws/devel/setup.bash " >> ~/.bashrc
$ source ~/.bashrc
```
最后还可以根据所选用的TB3机器人是Burger还是Waffle，将其作为环境变量加入~/.bashrc文件，以方便后续使用。否则每次运行程序都需要先输入“export TURTLEBOT3_MODEL=burger”或者“export TURTLEBOT3_MODEL=waffle”。
　　命令如下：

```
$ echo "export TURTLEBOT3_MODEL=burger" >> ~/.bashrc
$ source ~/.bashrc
```
2. 


# Sources to navigate robot

## how to set robot initial pose
1. refer to [如何用代码设置机器人初始坐标实现 2D Pose Estimate功能](https://www.cnblogs.com/kuangxionghui/p/8335853.html)

2. refer to [How to Modify a Robot’s Coordinates When it Arrives at a Checkpoint?](https://www.theconstructsim.com/ros-qa-140-how-to-modify-a-robots-coordinates-when-it-arrives-at-a-checkpoint/)

## how to get robot position and angle from the original position
1. subscribe /odom topic to get robot pose (position and orientation), refer [How to know the Pose of a robot (Python) ?](https://www.theconstructsim.com/ros-qa-know-pose-robot-python/)
   
```
Now we will create a script named inside the check_odometry/src/ directory. Add the following code to the script file
#!/usr/bin/env python

import rospy
from nav_msgs.msg import Odometry

def callback(msg):
    print(msg.pose.pose)
    
rospy.init_node('check_odometry')
odom_sub = rospy.Subscriber('/odom', Odometry, callback)
rospy.spin()

#We will now create a launch file with name inside the check_odometry/launch/ directory with the following content
<launch>
    <node pkg="check_odometry" type="check_odom.py" name="check_odometry" output="screen" />
</launch>

```
1. convert orientation to angle, refer [How to know the direction that the Robot is pointing to from pose?](https://answers.ros.org/question/196938/how-to-know-the-direction-that-the-robot-is-pointing-to-from-pose/)

```
#C++
tf::Quaterion quat;
tf::quaternionMsgToTF(msg->pose.pose.orientation, orientation);
tf::Matrix3x3 orTmp(quat);
orTmp.getRPY(roll, pitch, yaw);

#python
import rospy
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
from geometry_msgs.msg import Point, Twist
from math import atan2
x = 0.0
y= 0.0
theta = 0.0
def newOdom(msg):
    global x
    global y
    global theta

    x = msg.pose.pose.position.x
    y = msg.pose.pose.position.y

    rot_q = msg.pose.pose.orientation
    (roll,pitch,theta) = euler_from_quaternion ([rot_q.x,rot_q.y,rot_q.z,rot_q.w])
rospy.init_node("speed_controller")
sub = rospy.Subscriber("/odom",Odometry,newOdom)
```
## save ROS map to readable image
1. refer to [how to correctly convert OccupancyGrid format message to image ?](https://answers.ros.org/question/163801/how-to-correctly-convert-occupancygrid-format-message-to-image/)
```
def callback(self,data):
     self.width = data.info.width
     self.height = data.info.height
     self.resolution = data.info.resolution
     self.length = len(data.data)
     #self.min_line = []

     #creat an mat to load costmap
     costmap_mat = cv.CreateMat(self.height,self.width,cv.CV_8UC1)
     
     for i in range(1,self.height):
            for  j in range(1,self.width):
               cv.Set2D(costmap_mat,self.width-j,self.height-i,255-int(float(data.data[(i-1)*self.width+j])/100*255))
```
1. maybe change subscribe to topic `nav_msgs/OccupancyGrid`, see [map_server](http://wiki.ros.org/map_server)
2. or directly using `hector_compressed_map_transport`, [github](https://github.com/tu-darmstadt-ros-pkg/hector_slam/tree/catkin/hector_compressed_map_transport)

## autonomous move robot 
1. refer to [Learn TurtleBot and ROS](https://learn.turtlebot.com/), or find the source codes in [turtlebot](/docs/turtlebot)
    * [move to a specific point in the map](https://learn.turtlebot.com/2015/02/01/14/), see [code](https://github.com/markwsilliman/turtlebot/blob/master/go_to_specific_point_on_map.py)
    * [move the robot along a route, and execute task at each point](https://learn.turtlebot.com/2015/02/04/5/), see [code](https://github.com/markwsilliman/turtlebot/blob/master/follow_the_route.py)
    * [get the battery status](https://learn.turtlebot.com/2015/02/01/16/), see [code](https://github.com/markwsilliman/turtlebot/blob/master/kobuki_battery.py)
    
## rotate robot 
1. how to rotate a specific relative angle, refer [How to rotate a robot to a desired heading using feedback from odometry](https://www.theconstructsim.com/ros-qa-135-how-to-rotate-a-robot-to-a-desired-heading-using-feedback-from-odometry/), **not rely on current pose value**
2. how to rotate by angle speed, refer to [Rotating Left/Right](http://wiki.ros.org/turtlesim/Tutorials/Rotating%20Left%20and%20Right) **rely on current pose value**

# InfluxDB 
## install
```
sudo apt-get install python-influxdb
```
## python examples to manipulate infuxDB
refer [InfluxDB——python使用手册](https://www.cnblogs.com/huang-yc/p/10500209.html)

# Development
## Hosts
1. Turtlebot remote-pc:
host: ubuntu16 on virtualbox
ip:192.168.3.89
account:sw
password:abc123!@#

2. Turtlebot pc:
host: raspberry pi 3 on bot
ip: 192.168.3.90
account: waffle
password: 123456

## Install Packages
1. pip3 install -U rospkg
2. sudo apt-get install python-requests (python2)
3. sudo apt-get install python-influxdb

## launch robot
1. on master, run `roscore`
2. on turtlebot, run

```
#1. launch a robot at turtlebot
$roslaunch turtlebot3_bringup turtlebot3_robot.launch
```
```
##2. launch the navigation at turtlebot

#donwload amcl_demo.launch from: https://github.com/NVIDIA-AI-IOT/turtlebot3/blob/master/turtlebot_apps/turtlebot_navigation/launch/amcl_demo.launch into turtlebot3_navigation package directory, add 'waffle_pi' at <arg name='model'>, like: <arg name="model" default="$(env TURTLEBOT3_MODEL)" doc="model type [burger, waffle, waffle_pi]"/>
# $ roslaunch turtlebot3_navigation amcl_demo.launch map_file:=/tmp/my_map.yaml
# existed error!!!

$ roslaunch turtlebot3_navigation turtlebot3_navigation.launch open_rviz:=false initial_pose_x:=0 initial_pose_y:=0 initial_pose_a:=0 update_min_d:=0.1 update_min_a:=0.2 map_file:=/home/waffle/map/map.yaml
```
* ***For multirobots launch and navigation***
    * refer to [load multiple turtlebots3](http://emanual.robotis.com/docs/en/platform/turtlebot3/applications/#load-multiple-turtlebot3s) for launch multirobots
    * refer to [Virtual SLAM by Multiple TurtleBot3s](http://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/#virtual-slam-by-multiple-turtlebot3s) for slam with multirobots
    * refer to [multi_robot](https://github.com/ferherranz/multi_robot) for implementation of the multi robot configuration for bringup and navigation

* ***System feadbacks***
    * succeeded if you can see "odom received!"

    * error: "Timed out waiting for transform from base_footprint to map to become available before running costmap, tf error: canTransform: target_frame map does not exist.. canTransform returned after 0.100927 timeout was 0.1", refer [causes](https://www.codeleading.com/article/3546825816/;jsessionid=AB4A7A5725CA9642AF55C8A3F3D421A0)
    * 雷达信息不正确，所以导致出现这种错误，单独测试雷达数据，查看topic是否正确。 **此时雷达很有可能不装** try: `rostopic hz /scan`，或重启robot.launch和navigation.launch
    *  ＵＳＢ端口供电不足（很少的原因，可以换台电脑测一下）, 充电
    *  ｔｆ转换延迟: -- try restarting turtlebot3_robot.launch and then turtlebot3_navigation.launch several times

1. on master, run 

```
#the following solution seems not works at last, various fault happens when import tf, 
#**seems we can only use python2**
python3 /docs/turtlebot/go_to_specific_point_on_map.py
```
* ***System feadbacks***
    * if navigation module say: `
Aborting because a valid plan could not be found. Even after executing all recovery behaviors` and python client receive `comm state PREEMPTING`, it is because the goal position is not reachable

* error: `ImportError: dynamic module does not define module export function (PyInit__tf2)`
    * it is because tf2_ros was compiled for python2, see [solution](https://gist.github.com/yukke42/b6f409930240f424f69b16eb6bc374b2) to recompile for python3
    * **the above method not works, now we can only use python2 to import tf**
    
    
    ```
    ##if prompt 'no module: em', install:
    $ sudo apt-get install python3-empy
    
    $ git clone https://github.com/ros/geometry2 ~/autoware/ros/src/geometry2
$ catkin_make -DPYTHON_EXECUTABLE=/usr/bin/python3 -DPYTHON_LIBRARY=/usr/lib/python3.6/config-3.6m-x86_64-linux-gnu/libpython3.6.so -DPYTHON_VERSION=3
$ source ./devel/setup.bash
    ```

$ python3
Python 3.6.8 (default, Jan 14 2019, 11:02:34) 
[GCC 8.0.1 20180414 (experimental) [trunk revision 259383]] on linux
Type "help", "copyright", "credits" or "license" for more information.

>>> import tf
>>> from tf.transformations import quaternion_from_euler

    ```


# Navigation Tune
## initial pose estimation 
in `turtlebot3_navigation/launch/amcl.launch.xml`
```
<!-- 它在初始位置估计中被用作为高斯分布的初始x坐标值。--> 
<arg name="initial_pose_x" default="0.0"/>
<!-- 它在初始位置估计中被用作为高斯分布的初始y坐标值。--> 
<arg name="initial_pose_y" default="0.0"/>
<!-- 它在初始位置估计中被用作为高斯分布的初始yaw坐标值。--> 
<arg name="initial_pose_a" default="0.0"/>

<!-- 执行滤波器更新之前所需的平移运动(以米为单位) -->
<param name="update_min_d" value="0.2"/>
<!-- 执行滤波器更新之前所需的旋转运动(以弧度表示) -->
<param name="update_min_a" value="0.2"/>
```
## obstacle estimation
in `turtlebot3_navigation/param/costmap_common_params_burger.yaml` or `turtlebot3_navigation/param/costmap_common_params_waffle.yaml`
```
# 当物体与机器人的距离在如下距离内时，将物体视为障碍物。
obstacle_range: 2.5
# 传感器值大于如下距离的数据被视为自由空间(freespace)。
raytrace_range: 3.5
```

