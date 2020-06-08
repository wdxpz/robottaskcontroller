import rospy
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, PoseWithCovarianceStamped
from tf.transformations import euler_from_quaternion, quaternion_from_euler
import math
from random import sample


from config import Trial_Set_Pose_Count
from utils.logger2 import getLogger
logger = getLogger('turtlebot_initpose')
logger.propagate = False


class PoseIniter():
    def __init__(self, inspection_id, robot_id, init_x, init_y, init_a):

        self.inspection_id = inspection_id
        self.robot_id = robot_id
        self.msg_head = 'inspection:{} robot: {}: '.format(inspection_id,robot_id)
        # self.setpose_pub = rospy.Publisher('/{}/initialpose'.format(self.robot_id), PoseWithCovarianceStamped, latch=True, queue_size=1)
        self.setpose_pub = rospy.Publisher('/{}/initialpose'.format(self.robot_id), PoseWithCovarianceStamped, queue_size=10)
        self.trial_set_pose_flag = True
        self.init_pose = {'x': init_x,'y': init_y,'a': init_a}
        rospy.sleep(1)

        rospy.on_shutdown(self.shutdown)

    def _set_inital_pose(self):
        # Define a set inital pose publisher.
        p = PoseWithCovarianceStamped()
        p.header.stamp = rospy.Time.now()
        p.header.frame_id = "map"
        p.pose.pose.position.x = self.init_pose['x']
        p.pose.pose.position.y = self.init_pose['y']
        p.pose.pose.position.z = self.init_pose['a']
        (p.pose.pose.orientation.x, \
            p.pose.pose.orientation.y, \
            p.pose.pose.orientation.z, \
            p.pose.pose.orientation.w) = quaternion_from_euler(0, 0, self.init_pose['a'])
        # p.pose.covariance[6 * 0 + 0] = 0.5 * 0.5
        # p.pose.covariance[6 * 1 + 1] = 0.5 * 0.5
        # p.pose.covariance[6 * 3 + 3] = math.pi / 12.0 * math.pi / 12.0

        self.setpose_pub.publish(p)

    def set_pose(self):
        count = 0
        while self.trial_set_pose_flag == True:
            count += 1
            logger.info(self.msg_head + 'try no. {} to set roobt init pose'.format(count))
            self._set_inital_pose()
            if count == Trial_Set_Pose_Count:
                self.trial_set_pose_flag = False
            rospy.sleep(1)


    def shutdown(self):
        logger.info(self.msg_head + 'quit pose initialization for rospy shutdown!')
        rospy.sleep(1)