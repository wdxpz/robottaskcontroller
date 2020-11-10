import sys
import json

import rospy
import tf

from kafka import KafkaProducer
import config
from utils.ros_utils import initROSNode
from utils.logger import getLogger

logger = getLogger('taskcenter_simulator')
logger.propagate = False

task_producer = KafkaProducer(
    bootstrap_servers=config.Kafka_Brokers, 
        compression_type='gzip', value_serializer=lambda x: json.dumps(x).encode())

def startTask():
    task_body = {
        "task_type": 0, # 0 for Task_Inspection
        "inspection_id": 6,
        "site_id": "bj01",
        "robots": [
            {
                "robot_id": "rosbot1", #"tb3_0",
                "model": "rosbot2_pro", #waffle_pi",
                "original_pos": "0.0#0.0#0.0", # x-y-angle
                "subtasks": [
                    [1, 0.0, 0.3], # sequential number - x - y
                    #[2, 0.1, 0.5], 
                    #[3, 0.3, 0.7]
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

def checkRobotBaselinkOK(robot_id):
        logger.info('start to check robot {} ready for map location by listen to /{}/baselink.'.format(robot_id, robot_id))
        listener = tf.TransformListener()
        try:
            listener.waitForTransform("/map", "/{}/base_link".format(robot_id), rospy.Time(0), rospy.Duration(10.0))
            logger.info('checkRobotBaselinkOK: /{}/base_link is ready for map location!'.format(robot_id))
        except Exception as e:
            logger.info('checkRobotBaselinkOK: /{}/base_link is not ready for map location! '.format(robot_id) + str(e))
            raise Exception('/{}/base_link is not ready for map location! '.format(robot_id))

def sendMsg(body):
    try:
        future = task_producer.send(config.Task_Topic, key="".encode(), value=body)
        # Block until a single message is sent (or timeout)
        _ = future.get(timeout=config.Kafka_Blocking_time)
        logger.info('successfully send task {} !'.format(body))
    except Exception:
        logger.error('fail to send task {} ! '.format(body))

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1]=='start':
        startTask()
    elif sys.argv[1]=='locate':
        initROSNode('testlocation')
        checkRobotBaselinkOK('tb3_0')
    else:
        killNavProcess()
        

