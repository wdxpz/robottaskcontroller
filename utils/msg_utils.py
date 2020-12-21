import copy
import json

import redis
from kafka import KafkaProducer

import config
from utils.logger import getLogger

logger = getLogger('utils-kafka')
logger.propagate = False

status_producer = KafkaProducer(
    bootstrap_servers=config.Kafka_Brokers, 
        compression_type='gzip', value_serializer=lambda x: json.dumps(x).encode())

redis_connector = redis.Redis(host=config.redis_host, port=config.redis_port, db=0)

# just an example, you don't have to follow this format
task_status_payload = {
    "inspection_id": 3,
    "task_type": 0,
    "site_id": "site01",
    'timestamp': 1599033481,
    "robot": {
      "robot_id": "robot03",
      "checkpoint_no": 2,
      "status": 0 # 0:"reached", 1:"left", 2:"missed", 3:"failed"
    },
    'status': 0 #0:"started", 1:"finished", 2:"terminated"
}

robot_position_payload = {
    "timestamp": 1599033481,
    # "robot_name": 0,
    "inspection_id": 0,
    # "site_id": 0,
    # "location": '0-0-0'
}

robot_sync_cmd_paylaod = {
    "timestamp": 1599033481,
    "robot_id": 0,
    "inspection_id": 0,
    "site_id": 0,
    "cmd": 'photo'
}

def sendTaskStatusMsg(inspection_id, inspection_type, site_id, robots, task_status, timestamp, robot_id=None, checkpoint_no=None, robot_status=None):
    body = copy.deepcopy(task_status_payload)
    body['inspection_id'] = inspection_id
    body['task_type'] = inspection_type
    body['site_id'] = site_id
    body['robots'] = robots
    body['timestamp'] = timestamp
    body['status'] = task_status
    if robot_id is None:
        body['robot'] = None
    else:
        body['robot']['robot_id'] = robot_id
        body['robot']['checkpoint_no'] = checkpoint_no
        body['robot']['status'] = robot_status

    try:
        future = status_producer.send(config.Task_Status_Topic, key="".encode(), value=body)
        # Block until a single message is sent (or timeout)
        result = future.get(timeout=config.Kafka_Blocking_time)
        logger.info('Kafka operation : send task status {}'.format(body))
    except Exception as e:
        logger.error('Kafka operation : send task status msg {} error! \n'.format(body) +  str(e))
        logger.error('Kafka operation : ' + str(result))

def sendRobotPosMsg(inspection_id, site_id, timestamp, robot_id, pos_x, pos_y, pos_a):
    body = copy.deepcopy(robot_position_payload)
    body['inspection_id'] = inspection_id
    body['site_id'] = site_id
    body['timestamp'] = timestamp
    body['robot_id'] = robot_id
    body['location'] = config.Pos_Value_Splitter.join((str(pos_x), str(pos_y), str(pos_a))) if pos_x is not None else ''
    ###send to kafka robot-position-topic
    # try:
    #     future = status_producer.send(config.Robot_Position_Topic, key="".encode(), value=body)
    #     # Block until a single message is sent (or timeout)
    #     result = future.get(timeout=config.Kafka_Blocking_time)
    # except Exception as e:
    #     logger.error('Kafka operation : send robot position msg error! ' +  str(e))

    ###directly send robot position msg to redis
    try:
        redis_connector.hmset(robot_id, body)
        # logger.info('Redis operation : send robot pos record {}'.format(body))
        logger.info('Redis operation : send robot pos {}#{}'.format(pos_x, pos_y))
        logger.info('Redis operation : send {}'.format(body))
    except Exception as e:
        logger.error('Redis operation : send robot pos record error! ' + str(e))

def sendSyncCmdMsg(inspection_id, site_id, timestamp, robot_id, cmd='photo'):
    body = copy.deepcopy(robot_position_payload)
    body['inspection_id'] = inspection_id
    # body['site_id'] = site_id
    body['timestamp'] = timestamp
    body['robot_name'] = robot_id
    # body['cmd'] = cmd
    ##send to kafka robot-position-topic
    try:
        future = status_producer.send(config.Robot_Position_Topic, key="".encode(), value=body)
        # Block until a single message is sent (or timeout)
        result = future.get(timeout=config.Kafka_Blocking_time)
        logger.info('Kafka operation : send robot sync cmd msg: {}! '.format(cmd))
    except Exception as e:
        logger.error('Kafka operation : send robot position msg error! ' +  str(e))