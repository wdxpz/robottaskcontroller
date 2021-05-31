"""
run this script to simulate robot position sender
"""


import time
import json
# from kafka import KafkaProducer
import redis
import numpy as np

import sim_config
from utils.logger import getLogger
logger = getLogger('robot simulator')
logger.propagate = False




pos_body = {
    "timestamp": 1599033481,
    "robot_id": sim_config.robot_id,
    "inspection_id": sim_config.inspection_id,
    "site_id": sim_config.site_id,
    "location": '0-0-0'
}
pos = [0.0, 0.0, 0.0]
pos_array = [
    [-1.1347986,-0.33763275, 0],
    [-1.3348376,-1.6876328, 0],
    [-2.258, -0.498, 0],
    [-1.6458, -3.341, 0],
    [1.429, -4.0914, 0],
    [-2.2959, -7.2914, 0],
    [-5.396, -8.3914, 0],
    [-2.846, -12.316, 0],
    [1.9048, -13.26, 0],
    [2.304, -9.666, 0],
    [1.928, 0.516, 0],
    [-1.372, 2.75, 0],
    [-4.322, -0.925, 0],
    [1.181696,-0.30600053, 0]
]

# producer = KafkaProducer(
#     bootstrap_servers=config.brokers, compression_type='gzip', value_serializer=lambda x: json.dumps(x).encode())

redis_connector = redis.Redis(host=sim_config.redis_host, port=sim_config.redis_port, db=0)

def sim_robot_pos(duration=10):

    logger.info('start robot position simulation!')
    delay=60*duration    ###for 15 minutes delay 
    close_time=time.time()+delay
    while True:

        if time.time() > close_time:
            break

        time.sleep(1)
        pos_body['timestamp'] = str(int(time.time()))
        #pos = [x + 1e-5 for x in pos]
        #pos = [x + np.random.rand()*5.0 for x in pos]
        pos = pos_array[np.random.randint(0, len(pos_array)-1)]
        pos_str = ['{:.5f}'.format(x) for x in pos]
        pos_body['location'] = '#'.join(pos_str)

        try:
            # future = producer.send('robot-position-test', key="".encode(), value=pos_body)
            # Block until a single message is sent (or timeout)
            # result = future.get(timeout=config.block_waiting_time)
            redis_connector.hmset(sim_config.robot_id, pos_body)
            #redis_connector.hmset('tb3_1', pos_body)

            logger.info('Redis operation : send robot pos record {}'.format(pos_body))
        except Exception as e:
            logger.error('Redis operation : send robot pos record error! ' + str(e))
            continue



