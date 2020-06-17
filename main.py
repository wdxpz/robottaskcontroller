import threading
import time

from config import Task_Type

from utils.ros_utils import killNavProcess, initROSNode
from utils.inspection_utils import getTasksFromMsgQueue
from tasks.inspection import execInspection

from utils.logger import getLogger
logger = getLogger('main')
logger.propagate = False

def execTaskLoop():
    #init ROS node
    logger.info('Init ROS Node')
    initROSNode()

    logger.info('start msg loop!')

    while True:
        task = getTasksFromMsgQueue()
        if task is None:
            time.sleep(1)
            continue
        task_type, task_data = task[0], task[1]
        if task_type == Task_Type["Task_Inspection"]:   
            inspection_id = int(task_data['inspection_id'])
            task_name = 'inpsection: {}'.format(inspection_id)
            logger.info('start inspection task: {}'.format(task_name))
            task = threading.Thread(name=task_name, target=execInspection, args=(task_data,))
            task.start()
        elif task_type == Task_Type["Task_KillAllNavProcess"]:
            logger.info('start to kill all existing navigation process!')
            killNavProcess()

if __name__ == "__main__":
    execTaskLoop()