import threading
import time

from kafka import KafkaConsumer

from config import Task_Type, Msg_Center_Url, Task_Topic
from utils.ros_utils import killNavProcess, initROSNode
from utils.inspection_utils import getTasksFromMsgQueue
from tasks.inspection import execInspection

from utils.logger import getLogger
logger = getLogger('main')
logger.propagate = False

task_subscriber = KafkaConsumer(
    bootstrap_servers=Msg_Center_Url,
                         group_id="", auto_offset_reset="earliest")

def execTaskLoop():
    
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
    #init ROS node
    logger.info('Init ROS Node')
    initROSNode()

    logger.info('Start msg subscription!')
    task_subscriber.subscribe([Task_Topic])
    
    for task in task_subscriber:
        logger.info('get task: {}'.format(task))
        if 'task_type' not in task.keys():
            logger.info('error task data, ignored!')
            continue
        if task['task_type'] == Task_Type["Task_Inspection"]:   
            inspection_id = int(task['inspection_id'])
            task_name = 'inpsection: {}'.format(inspection_id)
            logger.info('start inspection task: {}'.format(task_name))
            task = threading.Thread(name=task_name, target=execInspection, args=(task,))
            task.start()
        elif task['task_type'] == Task_Type["Task_KillAllNavProcess"]:
            logger.info('start to kill all existing navigation process!')
            killNavProcess()