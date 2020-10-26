import threading
import time
import json

from kafka import KafkaConsumer

from config import Task_Type, Kafka_Brokers, Task_Topic
from utils.ros_utils import killNavProcess, initROSNode
from tasks.inspection import execInspection

from utils.logger import getLogger
logger = getLogger('main')
logger.propagate = False

task_subscriber = KafkaConsumer(
    bootstrap_servers=Kafka_Brokers,
                         group_id="robot_controller", auto_offset_reset="earliest")

# def execTaskLoop():
    
#     while True:
#         task = getTasksFromMsgQueue()
#         if task is None:
#             time.sleep(1)
#             continue
#         task_type, task_data = task[0], task[1]
#         if task_type == Task_Type["Task_Inspection"]:   
#             inspection_id = int(task_data['inspection_id'])
#             task_name = 'inpsection: {}'.format(inspection_id)
#             logger.info('start inspection task: {}'.format(task_name))
#             task = threading.Thread(name=task_name, target=execInspection, args=(task_data,))
#             task.start()
#         elif task_type == Task_Type["Task_KillAllNavProcess"]:
#             logger.info('start to kill all existing navigation process!')
#             killNavProcess()

if __name__ == "__main__":
    #init ROS node
    logger.info('Init ROS Node')
    initROSNode()

    logger.info('Start msg subscription!')
    task_subscriber.subscribe([Task_Topic])
    
    for task in task_subscriber:
        task = json.loads(task.value)
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