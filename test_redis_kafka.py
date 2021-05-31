import redis
from kafka import KafkaProducer
import json

from utils.logger import getLogger
logger = getLogger('test_redis_kafka')
logger.propagate = False

robot_id = 'tb3_0'
task_type = 30
site_id = 'bj02'
inspection_id =562

def test_redis_service():
    #redis
    redis_host = "123.1127.237.146"
    redis_port = "6379"

    robot_position_payload = {
        "timestamp": 1599033481,
        "robot_id": 'hello_a',
        "inspection_id": 0,
        "site_id": 0,
        "location": '0-0-0'
    }
    redis_connector = redis.Redis(host=redis_host, port=redis_port, db=0)
    try:
        redis_connector.hmset(0, robot_position_payload)

        logger.info('Redis operation : send robot pos {}#{}'.format(10, 2))
        logger.info('Redis operation : send {}'.format(body))
    except Exception as e:
        logger.error('Redis operation : send robot pos record error! ' + str(e))

def test_kafka_service():
    # Kafka setting
    Kafka_Brokers = ["123.1127.237.146:9092"]
    Test_Topic = "orange-test"
    Kafka_Blocking_time = 1
    status_producer = KafkaProducer(bootstrap_servers=Kafka_Brokers, compression_type='gzip', value_serializer=lambda x: json.dumps(x).encode())

def fake_send_task_start_end_status_msg():
    body = {
        "inspection_id": inspection_id,
        "task_type": task_type,  
        "site_id": site_id,
        "robots": ["tb3_0"],
        "timestamp": str(int(time.time())),
        "status": 130, #130:"started", 140:"finished", 150:"terminated"
        "robot": {
            #"robot_id": "tb3_0",
            #"checkpoint_no": 1,
            #"status": 0 # 0:"reached", 1:"left", 2:"missed", 3:"failed", 4:"done"
            },
    }

    Kafka_Brokers = ["192.168.12.146:9092"]
    Test_Topic = "task-status-test"
    Kafka_Blocking_time = 1

    status_producer = KafkaProducer(bootstrap_servers=Kafka_Brokers, 
            compression_type='gzip', value_serializer=lambda x: json.dumps(x).encode())

    try:
        future = status_producer.send(Test_Topic, key="".encode(), value=body)
        # Block until a single message is sent (or timeout)
        result = future.get(timeout=Kafka_Blocking_time)
        logger.info('Kafka operation : send task status {}'.format(body))
    except Exception as e:
        logger.error('Kafka operation : send task status msg {} error! \n'.format(body) +  str(e))
        logger.error('Kafka operation : ' + str(result))

if __name__=='__main__':
    fake_send_robot_ready_status_msg()



