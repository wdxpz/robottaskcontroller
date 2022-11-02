import time
import math

import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion

PI = 3.1415926535897

class RotateController():
    def __init__(self):
        # self.sub = rospy.Subscriber ('/{}/odom'.format(self.robot_id), Odometry, self.get_rotation)
        self.rotate_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.rotate_command =Twist()
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.ctrl_c = False
        self.rate = rospy.Rate(10)

        rospy.on_shutdown(self.shutdown)

    def publish_once_in_cmd_vel(self, cmd):
        """
        This is because publishing in topics sometimes fails the first time you publish.
        In continuos publishing systems there is no big deal but in systems that publish only
        once it IS very important.
        """
        while not self.ctrl_c:
            connections = self.rotate_pub.get_num_connections()
            if connections > 0:
                self.rotate_pub.publish(cmd)
                break
            else:
                self.rate.sleep()

    def rotate(self, angle=90, speed=90, clockwise=True, stay=2):
        #Converting from angles to radians
        '''
        best configuration for rosbot to rotate 90 degress:
        angular_spped = 1.27
        rate = 20
        '''
        angular_speed = 1.27 #30*math.pi/180  
        rate = 20  
        relative_angle = angle*math.pi/180

        #We wont use linear components
        self.rotate_command.linear.x=0
        self.rotate_command.linear.y=0
        self.rotate_command.linear.z=0
        self.rotate_command.angular.x = 0
        self.rotate_command.angular.y = 0

        # Checking if our movement is CW or CCW
        if clockwise:
            self.rotate_command.angular.z = -abs(angular_speed)
        else:
            self.rotate_command.angular.z = abs(angular_speed)
        
        r = rospy.Rate(rate)
        ticks = int(relative_angle*rate)
        for _ in range(ticks):
            if self.ctrl_c:
                break
            self.publish_once_in_cmd_vel(self.rotate_command)
            r.sleep()

        #Forcing our robot to stop
        rospy.loginfo('send stop rotate command')
        self.rotate_command.angular.z = 0
        self.rotate_pub.publish(self.rotate_command)

    def get_rotation (self, msg):
        orientation_q = msg.pose.pose.orientation
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (self.roll, self.pitch, self.yaw) = euler_from_quaternion (orientation_list)


    def rotate2(self, degrees=90):
        '''
        !!! not validated, so the get_rotation was disabled by comment
        self.sub = rospy.Subscriber ('/{}/odom'.format(self.robot_id), Odometry, self.get_rotation)
        in __init__()
        '''
        # time.sleep(1)
        self.stop_robot()

        target_rad = (degrees * math.pi/180) + self.yaw
        
        if target_rad < (- math.pi):
            target_rad = target_rad + (2 * math.pi)

        if target_rad > (math.pi):
            target_rad = target_rad - (2 * math.pi)
        
        while abs(target_rad - self.yaw) > 0.1 and not self.ctrl_c:
            self.rotate_command.linear.x=0
            self.rotate_command.linear.y=0
            self.rotate_command.linear.z=0
            self.rotate_command.angular.x = 0
            self.rotate_command.angular.y = 0
            self.rotate_command.angular.z = 0.5 * (target_rad - self.yaw)
            self.rotate_pub.publish(self.rotate_command)
            self.rate.sleep()
            self.stop_robot()
            rospy.loginfo('target rad: {}, current rad: {}'.format(target_rad, self.yaw))
        
        self.stop_robot()

    def stop_robot(self):
        #rospy.loginfo("shutdown time! Stop the robot")
        self.rotate_command.linear.x = 0.0
        self.rotate_command.angular.z = 0.0
        self.rotate_pub.publish(self.rotate_command)

    def shutdown(self):
        self.ctrl_c = True
        rospy.loginfo('stopped rotation')
        rospy.sleep(1)

if __name__ == '__main__':
    try:
        rospy.init_node('rotate_test', anonymous=False)

        navigator = RotateController(1, 'rosbot1')

        navigator.rotate()

        # Sleep to give the last log messages time to be sent
        rospy.sleep(2)

    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")
