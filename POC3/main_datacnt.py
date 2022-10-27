"""
POC3: Multisense based interaction with Connected object

main_datacnt.py: simplified implementation of data center for POC3

"""

import time
import datetime
import redis
from kafka import KafkaConsumer
import json
import requests

import config

from logger import getLogger
logger = getLogger('POC3_datacenter')
logger.propagate = False

RushTime = datetime.datetime.now().replace( hour=18, minute=0, second=0, microsecond=0 )

def getRobotTask(robot_id):
    url = "http://123.127.237.146:8080/api/v1/robot/{}".format(robot_id)
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    robot = response.json()
    site = robot["robots"][0]["RobotSite"]
    url = "http://192.168.12.146:8080/api/v1/inspection/site/{}".format(site)
    response = requests.request("GET", url, headers=headers, data=payload)
    site = response.json()
    inspection_id = site["inspections"][0]["InspectionId"]
    return inspection_id
    

def switchoffBulb():
    url = "http://192.168.28.103:3033/bulb/switch?device_name=bulb_1&action=off"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    

def switchonBulb():
    url = "http://192.168.28.103:3033/bulb/switch?device_name=bulb_1&action=on"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)

def switchFinger():
    url = "http://192.168.28.103:3033/finger/switch/?device_name=finger_1"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)

def start_datacnt():
    task_subscriber = KafkaConsumer(
        bootstrap_servers=Kafka_Brokers,
        group_id="robot_controller2", auto_offset_reset="earliest")
    task_subscriber.subscribe([config.Task_Status_Topic])
    
    visual_subscriber = KafkaConsumer(
        bootstrap_servers=Kafka_Brokers,
        group_id="robot_controller2", auto_offset_reset="earliest")
    visual_subscriber.subscribe([config.Visual_Status_Topic])

    visual_record_reader = None
    visual_record_reader_thread = None
    current_inspection_id =None

    for task in task_subscriber:
        task = json.loads(task.value)
        logger.info('get task: {}'.format(task))
        if 'task_type' not in task.keys():
            logger.info('ERROR TASK DATA, ignored!')
            continue
        if task['task_type'] != Task_Inspection_AT_RUSHTIME:
            logger.info('NOT CORRECT TASK TYPE, ignored!')
            continue
        if current_inspection_id:
            if task["inspection_id"] != current_inspection_id:
                logger("NOT ONGOING TASK, ignored!")
                continue

        if task['status'] == 130: #TASK STARTED
            current_inspection_id = task["inspection_id"]
            visual_record_reader = VisualRecordReader(visual_subscriber, task["inspection_id"], task["timestamp"])
            visual_record_reader_thread = Thread(target = visual_record_reader.run, args =())
            visual_record_reader_thread.start()
        
        if task['status'] in [140, 150]: #TASK FINISHED OR TERMINATED
            visual_record_reader.terminate()
            visual_record_reader_thread.join()


class VisualRecordReader():
    def __init__(self, reader, inspectioin_id, start_ts):
        self._running = True
        self.inspection_id = inspectioin_id
        self.task_start_ts = start_ts
        self.reader = reader
        self.robot_list = {}
        self.detect_person = False
      
    def terminate(self):
        self._running = False
        
    def run(self):
        for record in self.reader:
            if not self._running: break
            record = json.loads(record.value)
            #check record time
            if record["timestamp"] < self.task_start_ts:
                logger.info('Invalid (early) visual record: {}'.format(record))
                continue
            #check record's inspection id is current inpsection
            robot_id = record["id"].split("-")[0]
            if robot_id not in self.robot_list.keys():
              self.robot_list[robot_id] = getRobotTask(robot_id)
            robot_task_id = self.robot_list[robot_id]
            if robot_task_id != self.inspectioin_id:
                logger.info('Invalid (other task) visual record: {}'.format(record))
                continue

            # if person detected
            if record["category"] == "person":
                if datetime.datetime.now() < RushTime:
                    logger.info('Person detected before rushtime: {}'.format(record))
                else:
                    logger.info('Person detected after rushtime: {}'.format(record))
                    logger.info('switch off powner!!!')
                    switchoffBulb()
                    switchFinger()
                    break

if __name__ == "__main__":
    switchFinger()

