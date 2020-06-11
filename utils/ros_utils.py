import re
import time
import os
import pickle
import yaml

import rospy
from subprocess import Popen, PIPE, check_output, CalledProcessError
from config import Nav_Process_Pool, Map_Dir

from utils.logger import getLogger
logger = getLogger('utils.turtlebot')
logger.propagate = False

def shell_cmd(command, shell=True, timeout=3):
    # result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    # if result.returncode != 0:
    #     return 1, None
    # return 0, result.stdout
    try:
        result = check_output('timeout {} {}'.format(timeout, command), shell=shell)
        # result = check_output(command, shell=shell)
        return 0, result
    except CalledProcessError as e:
        logger.error(str(e))
        return 1, str(e)

def shell_open(command):
    '''
    run shell commnad witouth waiting for its return
    '''
    try:
        process = Popen(command)
        return 0, process
    except Exception as e:
        logger.error(str(e))
        return 1, str(e)

def checkRobotNode(name='map_server', trytimes=1):
    cmd = 'rosnode ping -c 1 {}'.format(name)

    for _ in range(trytimes):
        retcode, output = shell_cmd(cmd)
        if retcode==0 and len(re.findall('reply', output))>0:
            return True
        time.sleep(1)

    return False

def killNavProcess(inspection_ids=None):
    for id in Nav_Process_Pool.keys():
        if inspection_ids is None or id in inspection_ids:
            logger.info('killed process {} of inspection {}'.format(Nav_Process_Pool[id], id))
            Nav_Process_Pool[id].terminate()
            Nav_Process_Pool.pop(id, None)
            
        

def initROSNode():
    # Initialize
    #threadname = 'inspeciton_{}_robot_{}'.format(inspection_id, robot_id) 
    nodename = 'robotmaster'
    if not checkRobotNode('/'+nodename, trytimes=1):
        logger.info('init node: /'+nodename)
        #disable_signals=True otherwise the main thread will be killed after killNavProcess
        rospy.init_node(nodename, anonymous=False, disable_signals=True)  


def checkMapFile(siteid):
    map_yml = os.path.join(Map_Dir, siteid, 'map.yaml')
    map_pgm = os.path.join(Map_Dir, siteid, 'map.pgm')
    if not os.path.exists(map_yml):
        return False
    
    file = open(map_yml, 'r')
    file_data = file.read()
    file.close()
    all_data = list(yaml.load_all(file_data))[0]
    if all_data['image'] != map_pgm:
        logger.warn('path of map pgm is not consistent in yaml file, auto correct it!')
        all_data['image'] = map_pgm

        try:
            file = open(map_yml, 'w')
            yaml.dump(all_data, file)
            file.close()
        except Exception as e:
            logger.error("error to correct site's map yaml file! " + str(e))
            return False

    return True