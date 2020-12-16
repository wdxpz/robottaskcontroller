import threading
import time


from config import Inspection_Status_Codes, Enable_Influx, Pos_Value_Splitter, Robot_Model

from navigation.turtlebot_launch import Turtlebot_Launcher
from navigation.turltlebot_cruise import runRoute
from navigation.turtlebot_robot_status import setRobotWorking, setRobotIdel, isRobotWorking, isInspectionRunning, isInspectionRepeated
from utils.msg_utils import sendTaskStatusMsg
from utils.ros_utils import killNavProcess, checkMapFile
from monitor import InspectionMonitor

from utils.logger import getLogger
logger = getLogger('execInspection')
logger.propagate = False

inspection_monitor = InspectionMonitor.getInspectionMonitor()

def execInspection(data):
    try: 
        inspection_id = int(data['inspection_id'])
        inspection_type = int(data['task_type'])
        site_id = str(data['site_id'])
        robots = data['robots']
        robot_ids =  [robot['robot_id'] for robot in robots]
        '''
        #assign robot model by split robot_id
        '''
        for id in robot_ids:
            if id.startswith("tb3"):
                robots[id]['model'] = 'waffle_pi'
            elif id.startswith("ros2p"):
                robots[id]['model'] = 'rosbot2_pro'
            else:
                raise Exception('error in naming of robot_id: {}'.format(id))
    except Exception as e:
        logger.error("Error! command parameters error. " + str(e))
        sendTaskStatusMsg(inspection_id, site_id, robots, robot_ids,
                    Inspection_Status_Codes['ERR_CMD_PARAMETERS'],
                    str(int(time.time())))
        return
    
    if not checkMapFile(site_id):
        logger.error("Error!, map parameters error, exit!")
        sendTaskStatusMsg(inspection_id, site_id, robots, robot_ids,
                    Inspection_Status_Codes['ERR_CMD_PARAMETERS'],
                    str(int(time.time())))
        return

    #just for testing to prevent same inspection ids happen at the same time
    if inspection_monitor.isTaskRepeated(inspection_id):
        logger.error("Error! simultaneous same insepction_id, discard the later!")
        return
        
    working_robots = []
    for id in robot_ids:
        if inspection_monitor.isRobotWorking(id):
            working_robots.append(id)
    if len(working_robots) > 0:
        logger.error("Error!, required robot occupied, exit!")
        sendTaskStatusMsg(inspection_id, site_id, robots, robot_ids,
                    Inspection_Status_Codes['ERR_ROBOT_OCCUPIED'],
                    str(int(time.time())))
        return

    #logger.info('try to kill existed navigation process before start!')
    #TODO: this process can will kill all of current running nav processes, it is a BUG!
    #TODO: modify it and remove isInspectionRunning() check
    ####################################################################################
    #killNavProcess has been changed:
    #  1. kill corresponding nav process with specific inspection_ids, or 
    #  2. kill all existed nav inspections
    #so we should not kill any nav process at the beginning of an inpsection
    
    #killNavProcess()
        
    logger.info('[launch_nav] launch robot with inspection id: {}, robots: {}'.format(inspection_id, robots))
    bot_launcher =Turtlebot_Launcher(inspection_id, site_id, robots)
    try:
        #launch navigation mode for multi-robots
        bot_launcher.launch()
    except Exception as e:
        logger.error("Error!, failed to start robots, exit!")
        sendTaskStatusMsg(inspection_id, site_id, robots, robot_ids,
                    Inspection_Status_Codes['ERR_ROBOT_START'],
                    str(int(time.time())))
        logger.info('try to kill existed navigation process after failed start!')
        killNavProcess([inspection_id])
        return 

    #start navigation
    try:
        #navigate robot
        nav_subtasks = []
        nav_subtasks_over = {}
        for id in robot_ids:
            task_name = 'robot: {} of inpsection: {}'.format(id, inspection_id)
            nav_subtasks_over[task_name] = False
        for robot in robots:
            id = robot['robot_id']
            robot_model = robot['model']
            #prepare cruising data
            route = []
            for pt in robot['subtasks']:
                route.append(
                    {
                        'point_no': pt[0],
                        'position':{
                            # 'x': pt[1] if robot_model in Robot_Model[0:2] else pt[2],
                            # 'y': pt[2] if robot_model in Robot_Model[0:2] else pt[1]*-1.0
                            'x': pt[2] if robot_model in Robot_Model[0:2] else pt[2],
                            'y': pt[1]*-1.0 if robot_model in Robot_Model[0:2] else pt[1]*-1.0
                        },
                        'quaternion': {'r1': 0, 'r2': 0, 'r3': 0, 'r4': 1}
                    }
                )
            try:
                org_pos = [float(v) for v in robot['original_pos'].split(Pos_Value_Splitter)]
            except Exception as e:
                logger.error('ERROR! original_pos for robot {} not correct!'.format(id))
                sendTaskStatusMsg(inspection_id, site_id, robots, robot_ids,
                    Inspection_Status_Codes['ERR_CMD_PARAMETERS'],
                    str(int(time.time())))
                return
            task_name = 'robot: {} of inpsection: {}'.format(id, inspection_id)
            task = threading.Thread(name=task_name, target=runRoute, \
                args=(inspection_id, inspection_type, site_id, robot_ids, id, robot_model, robot_ids, route, org_pos, nav_subtasks_over,))
            nav_subtasks.append(task)
        for t in nav_subtasks:
            logger.info("Start inspection subtask thread: {}.".format(t.getName()))
            # t.setDaemon(True)
            t.start()
        msg = 'Inspection {} by robots {} started sucessfully!'.format(inspection_id, robot_ids)
        logger.info(msg)
        inspection_monitor.addTask(inspection_id, site_id, robot_ids)
        sendTaskStatusMsg(inspection_id, site_id, robots, robot_ids,
                    Inspection_Status_Codes['INSPECTION_STARTED'],
                    str(int(time.time())))
        return
    except Exception as e:
        logger.error("Error!, navigation failed, exit! \n " + str(e))
        inspection_monitor.rmTask(inspection_id)
        sendTaskStatusMsg(inspection_id, site_id, robots, robot_ids,
                    Inspection_Status_Codes['ERR_INSPECTION_FAILED'],
                    str(int(time.time())))
        logger.info('try to kill existed navigation process after failed navigation!')
        killNavProcess([inspection_id])
        return 

    logger.info('!!!inspection done!!!')