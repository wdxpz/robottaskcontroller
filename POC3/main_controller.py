"""
POC3: Multisense based interaction with Connected object

main_controller.py: simplified implementation of robot task controll for POC3
* before start poc3.py, be sure to initiate inspection id manually by postman
  refer https://orangelabschina.atlassian.net/l/cp/G1pWU6ra for detail
"""

import time
import rospy
import redis
from kafka import KafkaProducer
import json

import config
from goto_s import GoToPose
from rotate import RotateController

from logger import getLogger
logger = getLogger('POC3_robot')
logger.propagate = False

msg_header = "robot_controller: "


status_producer = KafkaProducer(bootstrap_servers=config.Kafka_Brokers, 
        compression_type='gzip', value_serializer=lambda x: json.dumps(x).encode())

def send_task_start_end_status_msg(msg):
    try:
        future = status_producer.send(config.Task_Status_Topic, key="".encode(), value=msg)
        # Block until a single message is sent (or timeout)
        result = future.get(timeout=config.Kafka_Blocking_time)
        rospy.loginfo('Kafka operation : send task status {}'.format(msg))
    except Exception as e:
        rospy.logerror('Kafka operation : send task status msg {} error! \n'.format(msg) +  str(e))
        rospy.logerror('Kafka operation : ' + str(result))

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
        future = status_producer.send(config.Wifi_Record_Topic, key="".encode(), value=stop_rec_body_wifi)
        result = future.get(timeout=config.Kafka_Blocking_time)
        logger.info('Kafka operation : send discovery stop msg: {}! '.format(stop_rec_body_wifi))
        #bt
        future = status_producer.send(sim_config.Bt_Record_Topic, key="".encode(), value=stop_rec_body_bt)
        result = future.get(timeout=sim_config.Kafka_Blocking_time)
        rospy.loginfo('Kafka operation : send discovery stop msg: {}! '.format(stop_rec_body_bt))
    except Exception as e:
        rospy.logerror('Kafka operation : send robot position msg error! ' +  str(e))

if __name__=='__main__':
    task_body = {
        "inspection_id": config.inspection_id,
        "task_type": config.task_type,  
        "site_id": config.site_id,
        "robots": [config.robot_id],
        "timestamp": int(time.time()),
        "status": 130, #130:"started", 140:"finished", 150:"terminated"
        "robot": {
            #"robot_id": "tb3_0",
            #"checkpoint_no": 1,
            #"status": 0 # 0:"reached", 1:"left", 2:"missed", 3:"failed", 4:"done"
            },
    }

    #sim task start
    send_task_start_end_status_msg(task_body)


    try:
        rospy.init_node('POC3', anonymous=False)
        navigator = GoToPose()
        rotate_ctl = RotateController()

        # Customize the following values so they are appropriate for your location
        position = {'x': 0.3, 'y' : 0}
        quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}

        rospy.loginfo(msg_header + "Go to (%s, %s) pose", position['x'], position['y'])
        success = navigator.goto(position, quaternion)

        if success:
            rospy.loginfo(msg_header + "reached the desired pose")
            navigator.getMapLocation()
        else:
            rospy.loginfo(msg_header + "The base failed to reach the desired pose")

        # Sleep to give the last log messages time to be sent
        rospy.sleep(1)

        #commend to robot to rotate 360 degree at current place
        step_angle = 360*1.0 / config.Circle_Rotate_Steps
        for i in range(1, config.Circle_Rotate_Steps+1):
            logger.info(msg_header + 'rotate step {}, rotate angle: {}'.format(i, step_angle))
            rotate_ctl.rotate(angle=step_angle)
            rospy.sleep(config.Holding_Step_Time/config.Circle_Rotate_Steps)

    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")


    #sim task end
    task_body["timestamp"] = int(time.time())
    task_body["status"] = 140
    send_task_start_end_status_msg(task_body)
    #sendDiscoveryStopRecords(config.robot_id)





