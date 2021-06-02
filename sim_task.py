import time

import redis
from kafka import KafkaProducer
import json

import sim_config
from sim_robot import sim_robot_pos
from utils.logger import getLogger
logger = getLogger('sim_task')
logger.propagate = False



status_producer = KafkaProducer(bootstrap_servers=sim_config.Kafka_Brokers, 
        compression_type='gzip', value_serializer=lambda x: json.dumps(x).encode())

def fake_send_task_start_end_status_msg(msg):
    try:
        future = status_producer.send(sim_config.Test_Topic, key="".encode(), value=msg)
        # Block until a single message is sent (or timeout)
        result = future.get(timeout=sim_config.Kafka_Blocking_time)
        logger.info('Kafka operation : send task status {}'.format(msg))
    except Exception as e:
        logger.error('Kafka operation : send task status msg {} error! \n'.format(msg) +  str(e))
        logger.error('Kafka operation : ' + str(result))

def sendDiscoveryStopRecords(robot_id):
    stop_rec_body_wifi = {
        'timestamp': 0, # value 0 says the inspection related with the corresponding robot was finished
        'id': robot_id+"-wifi01"
    }
    stop_rec_body_bt = {
        'timestamp': 0, # value 0 says the inspection related with the corresponding robot was finished
        'id': robot_id+"-bt01"
    }
    try:
        #wifi
        future = status_producer.send(sim_config.Wifi_Record_Topic, key="".encode(), value=stop_rec_body_wifi)
        result = future.get(timeout=sim_config.Kafka_Blocking_time)
        logger.info('Kafka operation : send discovery stop msg: {}! '.format(stop_rec_body_wifi))
        #bt
        future = status_producer.send(sim_config.Bt_Record_Topic, key="".encode(), value=stop_rec_body_bt)
        result = future.get(timeout=sim_config.Kafka_Blocking_time)
        logger.info('Kafka operation : send discovery stop msg: {}! '.format(stop_rec_body_bt))
    except Exception as e:
        logger.error('Kafka operation : send robot position msg error! ' +  str(e))

if __name__=='__main__':
    task_body = {
        "inspection_id": sim_config.inspection_id,
        "task_type": sim_config.task_type,  
        "site_id": sim_config.site_id,
        "robots": [sim_config.robot_id],
        "timestamp": int(time.time()),
        "status": 130, #130:"started", 140:"finished", 150:"terminated"
        "robot": {
            #"robot_id": "tb3_0",
            #"checkpoint_no": 1,
            #"status": 0 # 0:"reached", 1:"left", 2:"missed", 3:"failed", 4:"done"
            },
    }

    #sim task start
    fake_send_task_start_end_status_msg(task_body)


    #sim robot position
    sim_robot_pos(sim_config.sim_robot_duration)


    #sim task end
    task_body["timestamp"] = int(time.time())
    task_body["status"] = 140
    fake_send_task_start_end_status_msg(task_body)
    sendDiscoveryStopRecords(sim_config.robot_id)





