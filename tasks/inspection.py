import threading
import time


from config import Inspection_Status_Codes

from nav_utils.turtlebot_launch import Turtlebot_Launcher
from nav_utils.turltlebot_cruise import runRoute
from nav_utils.turtlebot_robot_status import setRobotWorking, setRobotIdel, isRobotWorking, isInspectionRunning, isInspectionRepeated
from utils.ros_utils import killNavProcess, checkMapFile
from utils.inspection_utils import updateInspection

from utils.logger import getLogger
logger = getLogger('execInspection')
logger.propagate = False


def execInspection(data):
    try: 
        inspection_id = int(data['inspection_id'])
        site_id = str(data['site_id'])
        robots = data['robots']
        robot_ids = robots.keys()
    except Exception as e:
        logger.error("Error! command parameters error. " + str(e))
        updateInspection(inspection_id, Inspection_Status_Codes['ERR_CMD_PARAMETERS'])
        return
    
    if not checkMapFile(site_id):
        logger.error("Error!, map parameters error, exit!")
        updateInspection(inspection_id, Inspection_Status_Codes['ERR_CMD_PARAMETERS'])
        return

    if isInspectionRepeated(inspection_id):
        logger.error("Error! simultaneous same insepction_id, discard the later!")
        return

    #only allow one inspection at same time
#    if isInspectionRunning():
#        logger.error("Error! An inspection is in running, exit!")
#        #updateInspection(inspection_id, Inspection_Status_Codes['ERR_INSPECTION_STILL_RUNNING'])
#       return
        
    working_robots = []
    for id in robot_ids:
        if isRobotWorking(id):
            working_robots.append(id)
    if len(working_robots) > 0:
        logger.error("Error!, required robot occupied, exit!")
        updateInspection(inspection_id, Inspection_Status_Codes['ERR_ROBOT_OCCUPIED'])
        return

    for id in robot_ids:
        setRobotWorking(id, inspection_id)

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
        updateInspection(inspection_id, Inspection_Status_Codes['ERR_ROBOT_START'])
        logger.info('try to kill existed navigation process after failed start!')
        for id in robot_ids:
            setRobotIdel(id)
        killNavProcess([inspection_id])
        return 

    #start navigation
    try:
        #navigate robot
        nav_tasks = []
        nav_tasks_over = {}
        for id in robot_ids:
            task_name = 'robot: {} of inpsection: {}'.format(id, inspection_id)
            nav_tasks_over[task_name] = False
        for id in robot_ids:
            #prepare cruising data
            route = []
            for pt in robots[id]['subtask']:
                route.append(
                    {
                        'point_no': pt[0],
                        'position':{
                            'x': pt[1],
                            'y': pt[2]
                        },
                        'quaternion': {'r1': 0, 'r2': 0, 'r3': 0, 'r4': 1}
                    }
                )
            org_pose = robots[id]['org_pos']
            task_name = 'robot: {} of inpsection: {}'.format(id, inspection_id)
            task = threading.Thread(name=task_name, target=runRoute, \
                args=(inspection_id, id, route, org_pose, nav_tasks_over,))
            nav_tasks.append(task)
        for t in nav_tasks:
            logger.info("Start inspection subtask thread: {}.".format(t.getName()))
            t.setDaemon(True)
            t.start()
        msg = 'Inspection {} by robots {} started sucessfully!'.format(inspection_id, robot_ids)
        logger.info(msg)
        updateInspection(inspection_id, Inspection_Status_Codes['INSPECTION_STARTED'])
        return

    except Exception as e:
        logger.error("Error!, navigation failed, exit!")
        updateInspection(inspection_id, Inspection_Status_Codes['ERR_INSPECTION_FAILED'])
        logger.info('try to kill existed navigation process after failed navigation!')
        for id in robot_ids:
            setRobotIdel(id)
        killNavProcess([inspection_id])
        return 