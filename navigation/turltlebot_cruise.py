#!/usr/bin/env python

'''
Copyright (c) 2016, Nadya Ampilogova
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import threading
import time
import copy
import datetime
import yaml
from Queue import Queue

import rospy
import tf
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
from geometry_msgs.msg import Point, Twist, Pose
from apscheduler.schedulers.background import BackgroundScheduler


import config
from turtlebot_goto import GoToPose
from turtlebot_rotate import RotateController, PI
from turtlebot_initpose import PoseIniter
from nav_math import distance, radiou2dgree
from turtlebot_robot_status import setRobotIdel, setRobotWorking, isRobotWorking
from turtlebot_launch import Turtlebot_Launcher


from utils.logger import getLogger
from utils.ros_utils import checkRobotNode, shell_cmd, killNavProcess
from utils.time_utils import dt2timestamp
from utils.kafka import sendTaskStatusMsg, sendRobotPosMsg
from utils.tsdb import DBHelper
from tasks.monitor import InspectionMonitor

inspection_monitor = InspectionMonitor.getInspectionMonitor()

logger = getLogger('turtlebot_cruise')
logger.propagate = False

def initParas():
    databody = {
        'inspection_id': 0,
        'site_id': 0,
        'robot_id': 0,
        'original_pose': None,
        'cur_x': 0,
        'cur_y': 0,
        'cur_theta': 0,
        'cur_time': 0,
        'pre_time': 0,
        'robot_status': {
            'id': 0,
            'route_point_no': None,
            'holding_pos': (0, 0), #(x, y, angle)
            #for element in 'enter', 'stay', 'leave', it will be (angle: timestamp)
            'enter': (),            
            'leave': ()
        },
        'flag_arrive_last_checkpoint': False,
        # flag to say the robot is in way home, no need to record and analyze data
        'flag_in_returning': False, 
        'pose_queue': Queue(maxsize=0),
        #there will be two kinds of records into the post_pose_queue
        # pos_record: (0, x, y, angle, time)
        # event_record: (1, waypoint_no, enter_time, leave_time)
        'post_pose_queue': Queue(maxsize =0),
        'dbhelper': DBHelper(),
        'lock': threading.Lock(),
        'flag_in_inspection': threading.Event(),
        'msg_head': 'inspection:{} robot: {}: '
    }
    return databody
    

def resetRobotStatus(paras, waypoint_no=None):

    paras['robot_status']['id'] = paras['robot_id'] 
    paras['robot_status']['route_point_no'] = waypoint_no
    paras['robot_status']['holding_pos'] = (0, 0)
    paras['robot_status']['enter'] = ()
    paras['robot_status']['leave'] = ()

def getMapLocation(paras):

    listener = tf.TransformListener()
    try:
        listener.waitForTransform("/map", "/{}/base_link".format(paras['robot_id']), rospy.Time(0), rospy.Duration(10.0))
        while paras['flag_in_inspection'].isSet():
            paras['cur_time'] =  datetime.datetime.utcnow()

            trans, rot = listener.lookupTransform("/map", "/{}/base_link".format(paras['robot_id']), rospy.Time(0))

            if paras['original_pose'] is None:
                paras['original_pose'] = (trans, rot)
                logger.info(paras['msg_head'] + 'readPose: find start pose: {}'.format(paras['original_pose']))
            else:
                if paras['flag_in_returning']:
                    return

            pose_pos = (trans, rot)
            paras['pose_queue'].put((pose_pos, paras['cur_time']))   
            paras['pre_time'] = paras['cur_time']

            rospy.sleep(config.Pos_Collect_Interval)

    except Exception as e:
        logger.error('getMapLocation Error of robot: {} \n'.format(paras['robot_id'])+str(e))
        return
        # raise Exception('getMapLocation Error of robot: {}'.format(paras['robot_id']))

def analyzePose(paras):
  
    while paras['flag_in_inspection'].isSet():
        if paras['pose_queue'] is None:
            logger.info(paras['msg_head'] + 'analyzePose: exit for main process terminates')
            return

        if paras['pose_queue'].empty():
            continue

        pose_record = paras['pose_queue'].get()
        pose_pos, pose_time = pose_record[0], pose_record[1]

        #convert to x, y, angle
        # cur_x = pose_pos.position.x
        # cur_y = pose_pos.position.y
        # rot_q = pose_pos.orientation
        #(_,_,cur_theta) = euler_from_quaternion ([rot_q.x,rot_q.y,rot_q.z,rot_q.w])
        paras['cur_x'] = pose_pos[0][0]
        paras['cur_y'] = pose_pos[0][1]
        rot_q = pose_pos[1]
        (_,_, paras['cur_theta']) = euler_from_quaternion (rot_q)
        
        #convert form radius to degree
        paras['cur_theta'] = radiou2dgree(paras['cur_theta'])
        # rospy.loginfo("current position: x-{}, y-{}, theta-{}".format(cur_x, cur_y, cur_theta))
        
        if inspection_monitor.isRobotWorking(paras['robot_id'], paras['inspection_id']):
            x, y, a = paras['cur_x'], paras['cur_y'], paras['cur_theta']
        else:
            x, y, a = None, None, None
        sendRobotPosMsg(paras['inspection_id'], paras['site_id'], str(int(dt2timestamp(pose_time))), 
                    robot_id=paras['robot_id'], 
                    pos_x=x, pos_y=y, pos_a=a)
        #put into post_pose_cache for uploading
        #value at index [0] is to indicate: 0--pos record, 1--event record
        if config.Enable_Influx:
            paras['post_pose_queue'].put((0, paras['cur_x'], paras['cur_y'], paras['cur_theta'], pose_time.isoformat("T")))

        #robot not arrive at a point or already leave a point
        if paras['robot_status']['route_point_no'] is None or len(paras['robot_status']['leave'])>0:
            continue

        #tell if robot leave current point
        if (pose_time - paras['robot_status']['enter'][1]).total_seconds() > (config.Holding_Time) or \
            distance(paras['robot_status']['holding_pos'], (paras['cur_x'], paras['cur_y'], paras['cur_theta'])) > config.Valid_Range_Radius:
            
            #paras['lock'].acquire()
            paras['robot_status']['leave'] = (paras['cur_theta'], pose_time)
            reportRobotEvent(paras, event_code=1, checkpoint_no=paras['robot_status']['route_point_no'], ts=dt2timestamp(pose_time))
            logger.info(paras['msg_head'] + 'ananlyzePose: find leave waypoint time, the record of current waypoint is: \n {}'.format(paras['robot_status']))

            #influx
            if config.Enable_Influx:
                paras['post_pose_queue'].put((1, paras['robot_status']['route_point_no'], paras['robot_status']['enter'][1].isoformat("T"), paras['robot_status']['leave'][1].isoformat("T")))
            
            if paras['flag_arrive_last_checkpoint']:
                logger.info(paras['msg_head'] + 'set in returning flag at leaving the last checkpoint')
                paras['flag_in_returning'] = True
            resetRobotStatus(paras)
            #paras['lock'].release()
            continue

def uploadCacheData(paras):
    pos_records = []
    event_records = []

    while not paras['post_pose_queue'].empty():
        rec = paras['post_pose_queue'].get()
        if rec[0] == 0:
            pos_records.append(rec[1:])
        else:
            event_records.append(rec[1:])

    t = threading.Thread(target=paras['dbhelper'].upload, args=(paras['inspection_id'], paras['site_id'], paras['robot_id'], pos_records, event_records))
    t.setDaemon(True)
    t.start()

def buildFullRoute(paras, route, org_pose):
    #prepare navigation route to make robot return to original position after the job
    ##add reversed point list and original robot pos into the route
    if len(route) == 0:
        return []

    full_route = copy.deepcopy(route)
    route_len = len(route)
    return_index = range(2, route_len+1)
    return_index.reverse()
    for pt, index in zip(route[:-1][::-1], return_index):
        pt['point_no'] = index*-1
        full_route.append(pt)
        
    pt = copy.deepcopy(route[0])
    pt['point_no'] = -1
    pt['position']['x'], pt['position']['y'] = org_pose[0], org_pose[1]
    pt['quaternion']['r1'], pt['quaternion']['r2'], \
        pt['quaternion']['r3'],  pt['quaternion']['r4'] = 0, 0, 0, 1
    full_route.append(pt)
    logger.info(paras['msg_head'] + 'build full route: \n {}'.format(full_route))

    return full_route

def setEnterEvent(paras, pt_num, pt):
    paras['lock'].acquire()
    paras['robot_status']['route_point_no'] = pt_num
    paras['robot_status']['enter'] = (paras['cur_theta'], paras['cur_time'])
    paras['robot_status']['route_point_pos'] = (pt['position']['x'], pt['position']['y'])
    paras['robot_status']['holding_pos'] = (paras['cur_x'], paras['cur_y'])
    logger.info(paras['msg_head'] + 'runRoute: arrive at a waypoint,  the record of current waypoint is: \n {}'.format(paras['robot_status']))
    paras['lock'].release()

def reportTaskStatus(paras, ts=time.time(), task_status=config.Inspection_Status_Codes["INSPECTION_STARTED"]):
    sendTaskStatusMsg(paras['inspection_id'], paras['site_id'], task_status, str(int(ts)))

def reportRobotEvent(paras, event_code, checkpoint_no=None, ts=time.time()):
    """
    event_code: 0:"reached", 1:"left", 2:"missed", 3:"failed", 4:"done"
    """
    if event_code == 3:
        task_status=config.Inspection_Status_Codes["INSPECTION_STARTED_WITH_ERROR"]
    else:
        task_status=config.Inspection_Status_Codes["INSPECTION_STARTED"]
    sendTaskStatusMsg(paras['inspection_id'], paras['site_id'], 
            task_status, str(int(ts)), 
            robot_id=paras['robot_id'],  checkpoint_no=checkpoint_no,  robot_status=event_code)  
            

def clearTasks(paras, scheduler, ts=time.time(), task_status=config.Inspection_Status_Codes["INSPECTION_STARTED"]):
    #set the task over flag
    task_name = 'robot: {} of inpsection: {}'.format(paras['robot_id'], paras['inspection_id'])
    paras['nav_subtasks_over'][task_name] = True
    
    paras['flag_in_inspection'].clear()
    if scheduler is not None and scheduler.running:
        scheduler.shutdown()

    if task_status == config.Inspection_Status_Codes["INSPECTION_TERMINATED"] or \
        task_status == config.Inspection_Status_Codes["INSPECTION_TERMINATED_WITH_ERROR"]:
        for id in paras['all_robot_ids']:
            inspection_monitor.setRobotIdle(paras['inspection_id'], id)
            sendRobotPosMsg(paras['inspection_id'], paras['site_id'], str(int(ts)), 
                            robot_id=id, 
                            pos_x=None, pos_y=None, pos_a=None)
        reportTaskStatus(paras, ts=ts, task_status=task_status)
        logger.info('all nav taks terminated with code {}, trying to kill navigation process at runRoute quit!'.format(task_status))
        killNavProcess([paras['inspection_id']])
        inspection_monitor.rmTask(paras['inspection_id'])        
    else:
        #config.Inspection_Status_Codes["INSPECTION_STARTED_WITH_ERROR"]
        #config.Inspection_Status_Codes["INSPECTION_STARTED"]
        if task_status == config.Inspection_Status_Codes["INSPECTION_STARTED_WITH_ERROR"]:
            inspection_monitor.setRobotFailed(paras['inspection_id'], paras['site_id'])
            inspection_robot_status_code = 3
        else:
            inspection_monitor.setRobotIdle(paras['inspection_id'], paras['site_id'])
            inspection_robot_status_code = 4
        sendRobotPosMsg(paras['inspection_id'], paras['site_id'], str(int(ts)), 
                robot_id=paras['robot_id'], 
                pos_x=None, pos_y=None, pos_a=None)
        
        all_subtasks_over = True
        robot_failed = False
        for _, over_flag in paras['nav_subtasks_over'].items():
            if not over_flag:
                all_subtasks_over = False
                break
        for id in paras['all_robot_ids']:
            if inspection_monitor.isRobotFailed(paras['robot_id'], paras['inspection_id']):
                robot_failed = True 
                break
           
        reportRobotEvent(paras, event_code=inspection_robot_status_code, checkpoint_no=None, ts=ts)  
        logger.info('robot: {} inspection done with code {}'.format(paras['robot_id'], inspection_robot_status_code))  
        
        if all_subtasks_over: 
            status_code = config.Inspection_Status_Codes["INSPECTION_FINISHED_WITH_ERROR"] \
                if robot_failed else config.Inspection_Status_Codes["INSPECTION_FINISHED"]
            reportTaskStatus(paras, ts=ts, task_status=status_code)
            logger.info('all nav taks finished with status code {}, trying to kill navigation process at runRoute quit!'.format(status_code))
            killNavProcess([paras['inspection_id']])
            inspection_monitor.rmTask(paras['inspection_id'])

def setInReturn(paras, scheduler):
    paras['flag_in_returning'] = True
    paras['flag_in_inspection'].clear()
    if scheduler is not None and scheduler.running:
        scheduler.shutdown()
    
def runRoute(inspectionid, siteid, robotid, robot_ids, route, org_pose, nav_subtasks_over):
    paras = initParas()

    #reset global variables
    paras['inspection_id'] = inspectionid 
    paras['site_id'] = siteid
    paras['robot_id'] = robotid
    paras['all_robot_ids'] = robot_ids
    paras['msg_head'] = paras['msg_head'].format(inspectionid,robotid)
    paras['original_pose'] = None
    paras['cur_x'], paras['cur_y'], paras['cur_theta'] = 0, 0, 0
    paras['cur_time'], paras['pre_time'] = 0, 0
    paras['flag_arrive_last_checkpoint'] = False
    paras['flag_in_returning'] = False
    paras['pose_queue'].empty()
    paras['post_pose_queue'].empty()
    paras['nav_subtasks_over'] = nav_subtasks_over
    resetRobotStatus(paras)
    

    if type(route) != list:
        msg = paras['msg_head'] + "required param route in type: list. Empty the route"
        logger.error(msg)
        route = []

    if len(route) == 0:
        msg = paras['msg_head'] + 'route point list is empty!'
        logger.info(msg)

    try:
        paras['flag_in_inspection'].set()  

        logger.info(paras['msg_head'] + 'start to init robot {} pose as x:{}, y:{}, a:0.0'.format(paras['robot_id'], org_pose[0], org_pose[0]))
        pose_initer = PoseIniter(paras['inspection_id'], paras['robot_id'], org_pose[0], org_pose[1], 0.0)
        pose_initer.set_pose()

        # start to probe robot's position
        # odom_sub = rospy.Subscriber("/{}/odom".format(robot_id), Odometry, readPose)
        # logger.info(msg_head + 'start analyze pose thread')
        locater_t =  threading.Thread(name='{}_get_pose'.format(paras['robot_id']), target=getMapLocation, args=(paras,))
        locater_t.setDaemon(True)
        locater_t.start()

        analyzer_t = threading.Thread(name='{}_analyze_pose'.format(paras['robot_id']), target=analyzePose, args=(paras,))
        analyzer_t.setDaemon(True)
        analyzer_t.start()

        if config.Enable_Influx:
            scheduler = BackgroundScheduler()  
            scheduler.add_job(lambda: uploadCacheData(paras), 'interval', seconds=config.Upload_Interval)
            scheduler.start()


        #init the rotate controller
        rotate_ctl =  RotateController(paras['inspection_id'], paras['robot_id'])
        
        #build the full route to make the robot return to its original position
        full_route = buildFullRoute(paras, route, org_pose)
        route_len = len(route)
        
        #start navigation
        navigator = GoToPose(paras['inspection_id'], paras['robot_id'])
        for index, pt in enumerate(full_route, start=1):

            # if config.DEBUG:
            # logger.info('testing: skip cruise!!!')
            # while original_pose is None:
            #     pass
            # break

            if rospy.is_shutdown():
                ts = time.time()
                logger.error(paras['msg_head'] + 'runRoute quit for rospy shutdown')
                clearTasks(paras, scheduler, ts, config.Inspection_Status_Codes["INSPECTION_TERMINATED_WITH_ERROR"])
                break

            pt_num = pt['point_no']

            #to check if robot is still online
            try:
                Turtlebot_Launcher.checkRobotOnline(paras['robot_id'])
            except Exception as e:
                ts = time.time()
                logger.error("robot {} not online anymore! Terminate its navigation routine! \n".format(paras['robot_id']) + str(e))
                clearTasks(paras, scheduler, ts, config.Inspection_Status_Codes["INSPECTION_STARTED_WITH_ERROR"])
                break

            # Navigation
            logger.info(paras['msg_head'] + "Go to No. {} pose".format(pt_num))
            success = navigator.goto(pt['position'], pt['quaternion'])
            # pose_initer.set_pose()
            if not success:
                logger.warn(paras['msg_head'] + "Failed to reach No. {} pose".format(pt_num))
                #send miss event to tsdb
                if index <= route_len:
                    reportRobotEvent(paras, event_code=2, checkpoint_no=pt_num)
                    if config.Enable_Influx:
                        paras['dbhelper'].writeMissPointEvent(paras['inspection_id'], paras['site_id'], paras['robot_id'], datetime.datetime.utcnow(), pt_num)
                if index == route_len:
                    setInReturn(paras, scheduler)
                continue
            logger.info(paras['msg_head'] + "Reached No. {} pose".format(pt_num))
            
            
            if pt_num == route[-1]['point_no']:
                logger.info(paras['msg_head'] + 'Set flag of arrivging the last checkpoint')
                paras['flag_arrive_last_checkpoint'] = True

            if index > route_len:
                # returning route
                if paras['flag_arrive_last_checkpoint'] == False:
                    logger.info(paras['msg_head'] + 'set in returning flag at first returning point')
                setInReturn(paras, scheduler)
                continue  
            
            #set point enter information
            setEnterEvent(paras, pt_num, pt)
            reportRobotEvent(paras, event_code=0, checkpoint_no=paras['robot_status']['route_point_no'])

            #commend to robot to rotate 360 degree at current place
            step_angle = 360*1.0 / config.Circle_Rotate_Steps
            for i in range(1, config.Circle_Rotate_Steps+1):
                logger.info(paras['msg_head'] + 'runRoute: rotate step {}, rotate angle: {}'.format(i, step_angle))
                rotate_ctl.rotate(angle=step_angle)
                rospy.sleep(config.Holding_Step_Time/config.Circle_Rotate_Steps)

            #this guarantee to send the parameters out
            rospy.sleep(0.5)

        #to make the analyzePose thread finished after unsubscribe the odom topic
        logger.info(paras['msg_head'] + 'runRoute: finished route, unregister topic odom!')
        ts = time.time()
        clearTasks(paras, scheduler, ts, config.Inspection_Status_Codes["INSPECTION_STARTED"])
    except rospy.ROSInterruptException:
        logger.info(paras['msg_head'] + "runRoute quit for Ctrl-C caught")
        ts = time.time()
        clearTasks(paras, scheduler, ts, config.Inspection_Status_Codes["INSPECTION_TERMINATED"])
        


if __name__ == '__main__':
        # Read information from yaml file
    with open("route.yaml", 'r') as stream:
        dataMap = yaml.load(stream)

    # runRoute(0, 'no3_0', dataMap)
