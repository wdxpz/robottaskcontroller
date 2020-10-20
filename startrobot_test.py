import sys
import json

from kafka import KafkaProducer
import config
from utils.logger import getLogger

logger = getLogger('taskcenter_simulator')
logger.propagate = False

task_producer = KafkaProducer(
    bootstrap_servers=config.Kafka_Brokers, 
        compression_type='gzip', value_serializer=lambda x: json.dumps(x).encode())

def startTask():
    task_body = {
        "task_type": 0, # 0 for Task_Inspection
        "inspection_id": 3,
        "site_id": "bj01",
        "robots": [
            {
                "robot_id": "tb3_0",
                "model": "waffle_pi",
                "original_pos": "0.0-0.0-0.0", # x-y-angle
                "subtasks": [
                    [1, 0, 0.5], # sequential number - x - y
                    [2, 0.5, 0.5]
                ]
            }
        ]
    }

    sendMsg(task_body)

def killNavProcess():
    kill_command = {
        "task_type": 10 # 10 for Task_KillAllNavProcess
    }

    sendMsg(kill_command)

def sendMsg(body):
    try:
        future = task_producer.send(config.Task_Topic, key="".encode(), value=body)
        # Block until a single message is sent (or timeout)
        _ = future.get(timeout=config.Kafka_Blocking_time)
        logger.info('successfully send task {} !'.format(body))
    except Exception:
        logger.error('fail to send task {} ! '.format(body))

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1]=='s':
        startTask()
    else:
        killNavProcess()
        

