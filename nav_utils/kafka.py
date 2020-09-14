import copy
import json
from kafka import KafkaProducer
import config

from utils.logger import getLogger
logger = getLogger('utils-kafka')
logger.propagate = False

task_status_producer = KafkaProducer(
    bootstrap_servers=config.Msg_Center_Url, 
        compression_type='gzip', value_serializer=lambda x: json.dumps(x).encode())

# just an example, you don't have to follow this format
task_status_payload = {
    "inspection_id": 3,
    "site_id": "site01",
    'timestamp': 1599033481,
    "robot": {
      "robot_id": "robot03",
      "checkpoint_no": 2,
      "status": 0 # 0:"reached", 1:"left", 2:"missed", 3:"failed"
    },
    'status': 0 #0:"started", 1:"finished", 2:"terminated"
}

robot_status_payload = {
    "timestamp": 1599033481,
    "robot_id": 0,
    "inspection_id": 0,
    "site_id": 0
    "location": '0-0-0'
}

def sendTaskStatusMsg(inspection_id, site_id, task_status, timestamp, robot_id=None, checkpoint_no=None, robot_status=None):
    body = copy.deepcopy(task_status_payload)
    body['inspection_id'] = inspection_id
    body['site_id'] = site_id
    body['timestamp'] = timestamp
    body['status'] = task_status
    if robot_id is None:
        body['robot'] = None
    else:
        body['robot']['robot_id'] = robot_id
        body['robot']['checkpoint_no'] = checkpoint_no
        body['robot']['status'] = robot_status

    try:
        future = task_status_producer.send(config.Task_Status_Topic, key="".encode(), value=body)
        # Block until a single message is sent (or timeout)
        result = future.get(timeout=10)
    except Exception as e:
        logger.error('Kafka operation : send task status msg error! ' +  str(e))

def sendRobotPosMsg(inspection_id, site_id, timestamp, robot_id, pos_x, pos_y, pos_a):
    body = copy.deepcopy(task_status_payload)
    body['inspection_id'] = inspection_id
    body['site_id'] = site_id
    body['timestamp'] = timestamp
    body['robot_id'] = robot_id
    body['location'] = "-".join((pos_x, pos_y, pos_a)) if pos_x is not None else None
    try:
        future = task_status_producer.send(config.Robot_Position_Topic, key="".encode(), value=body)
        # Block until a single message is sent (or timeout)
        result = future.get(timeout=10)
    except Exception as e:
        logger.error('Kafka operation : send robot position msg error! ' +  str(e))