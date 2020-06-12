import os
import copy
import time
import pickle
import xml.etree.ElementTree as ET
from os.path import expanduser

import rospy
import tf

from config import ROS_Launch_File, Map_Dir, Launch_Max_Try, Nav_Process_Pool, DEBUG
from utils.ros_utils import checkRobotNode, shell_open

#from utils.logger import logger
from utils.logger import getLogger
logger = getLogger('Turtlebot_Launcher')
logger.propagate = False


class Turtlebot_Launcher():
    def __init__(self, inspection_id, siteid, robots):
        self.robots = robots
        self.siteid = siteid
        self.inspection_id = inspection_id

    def launch(self):
        
        launched = False
        for i in range(Launch_Max_Try):
            logger.info('Start trial no. {} to launch navigation in multirobot mode!'.format(i+1))
            try:
                self.checkRobotsOn()
                self.startNavigation()
                rospy.sleep(5)
                #self.checkRobotsNav()
                #rospy.sleep(3)
                self.checkRobotsBaselink()
                launched = True
                break
            except Exception as e:
                logger.error('launch: ' + str(e))
                msg = 'Faild of trial no. {} to launch navigation in multirobot mode. '.format(i+1) + str(e)
                logger.info(msg)

        if launched:
            logger.info('Succeed in trial no. {} to launch navigation in multirobot mode!'.format(i+1))
        else:
            msg = 'Faild to launch navigation in multirobot mode after {} trials'.format(Launch_Max_Try)
            logger.error(msg)
            raise Exception(msg)

    def checkRobotsOn(self):
        robot_ids = self.robots.keys()
        failed_robots = []
        
        for id in robot_ids:
            try:
                self.checkRobotOnline(id)
            except Exception as e:
                logger.error('checkRobotsOn: '+ str(e))
                failed_robots.append(id)
                break

        if len(failed_robots) != 0:
            msg = 'checkRobotsOn: robots {} not online !!!!'.format(failed_robots)
            logger.error(msg)
            raise Exception(msg)
    
    def checkRobotsNav(self):
        robot_ids = self.robots.keys()
        failed_robots = []
        
        for id in robot_ids:
            try:
                self.checkRobotNavOK(id)
            except Exception as e:
                logger.error('checkRobotsNav: ' + str(e))
                failed_robots.append(id)
                break

        if len(failed_robots) != 0:
            msg = 'robot: {} navigation not ready!'.format(failed_robots)
            logger.error(msg)
            raise Exception(msg)

    def checkRobotsBaselink(self):
        robot_ids = self.robots.keys()
        failed_robots = []
        
        for id in robot_ids:
            try:
                self.checkRobotBaselinkOK(id)
            except Exception as e:
                logger.error('checkRobotsBaselink: ' + str(e))
                failed_robots.append(id)
                break

        if len(failed_robots) != 0:
            msg = 'robot: {} /baselink not ready for map location!'.format(failed_robots)
            logger.error(msg)
            raise Exception(msg)

    @staticmethod
    def checkRobotOnline(robot_id):
        robot_core_node = '/{}/turtlebot3_core'.format(robot_id)
        logger.info('start to check robot {} by ping rosnode {}'.format(robot_id, robot_core_node))
        if not checkRobotNode(robot_core_node, trytimes=1):
            msg = 'checkRobotOnline: robot {} not online!'.format(robot_id)
            logger.error(msg)
            raise Exception(msg)
        logger.info('robot {} is online!'.format(robot_id))

    @staticmethod
    def checkRobotNavOK(robot_id):
        robot_movebase_node = '/{}/move_base'.format(robot_id)
        logger.info('start to check robot {} by ping rosnode {}'.format(robot_id, robot_movebase_node))
        if not checkRobotNode(robot_movebase_node, trytimes=1):
            msg = 'checkRobotNavOK: robot {} navigation not ready, not found {}!'.format(robot_id, robot_movebase_node)
            logger.error(msg)
            raise Exception(msg)
        logger.info('robot {} navigation is ready!'.format(robot_id))

    @staticmethod
    def checkRobotBaselinkOK(robot_id):
        logger.info('start to check robot {} ready for map location by listen to /{}/baselink.'.format(robot_id, robot_id))
        listener = tf.TransformListener()
        try:
            listener.waitForTransform("/map", "/{}/base_link".format(robot_id), rospy.Time(0), rospy.Duration(10.0))
            logger.info('checkRobotBaselinkOK: /{}/base_link is ready for map location!'.format(robot_id))
        except Exception as e:
            logger.info('checkRobotBaselinkOK: /{}/base_link is not ready for map location! '.format(robot_id) + str(e))
            raise Exception('/{}/base_link is not ready for map location! '.format(robot_id))
            

    def startNavigation(self):
        launch_file = self.buildLaunchFile()
        launch_file = launch_file.split('/')[-1]
        command = ['roslaunch', 'multirobot_nv',  launch_file]

        ret_code, ret_pro = shell_open(command)
        if ret_code != 0:
            msg = 'launch navigation failed, command [{}] not work!'.format(command)
            logger.error(msg)
            raise Exception(msg)        
        else:
            if self.inspection_id in Nav_Process_Pool.keys():
                ret_pro.terminate()
                msg = "Found same and not finished inspection_id is running nav process, nav terminated!"
                logger.error(msg)
                raise Exception("Found same and not finished inspection_id is running nav process, nav terminated!")
  
            Nav_Process_Pool[self.inspection_id] = ret_pro


    def buildLaunchFile(self):
        org_launch_file = os.path.join(expanduser("~"), ROS_Launch_File)

        new_launch_file = org_launch_file.split('.')[0]+'_new.launch'

        tree = ET.parse(org_launch_file)
        root = tree.getroot()

        #modify mapserver node
        map_path = os.path.join(Map_Dir, self.siteid, 'map.yaml')
        logger.info('map path: ' + map_path)
        mapnode = root[0]
        mapnode.getchildren()[0].attrib['value'] = map_path
        
        #create robot nodes
        robot_ids = self.robots.keys()
        for id in robot_ids:
            newnode = copy.deepcopy(root[1])
            newnode.getchildren()[0].attrib['value'] = id
            newnode.getchildren()[1].attrib['name'] = id + "_init_x"
            newnode.getchildren()[1].attrib['value'] = str(self.robots[id]['org_pos'][0])
            newnode.getchildren()[2].attrib['name'] = id + "_init_y"
            newnode.getchildren()[2].attrib['value'] = str(self.robots[id]['org_pos'][1])
            newnode.getchildren()[3].attrib['name'] = id + "_init_a"
            newnode.getchildren()[3].attrib['value'] = '0.0'
            root.append(newnode)
        #delete the template robot node
        root.remove(root[1])

        try:
            tree.write(new_launch_file)
            return new_launch_file
        except Exception as e:
            logger.error(str(e))
        