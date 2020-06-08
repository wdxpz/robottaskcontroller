import requests
import os
import pickle
from Queue import Queue

import config

from utils.logger import getLogger
logger = getLogger('utils.inspection_status')
logger.propagate = False

Robot_Task_Cache = Queue()
Robot_Task_Cache_File = '/robot_task_cache.pkl'


class File(object):
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise OSError('{file_path} not exist'.format(file_path = file_path))
        self.file_path = os.path.abspath(file_path)

    def status(self):
        open_fd_list = self.__get_all_fd()
        open_count = len(open_fd_list)
        is_opened = False
        if open_count > 0:
            is_opened = True

        return {'is_opened': is_opened, 'open_count': open_count}

    def __get_all_pid(self):
        """获取当前所有进程"""
        return [ _i for _i in os.listdir('/proc') if _i.isdigit()]

    def __get_all_fd(self):
        """获取所有已经打开该文件的fd路径"""
        all_fd = []
        for pid in self.__get_all_pid():
            _fd_dir = '/proc/{pid}/fd'.format(pid = pid)
            if os.access(_fd_dir, os.R_OK) == False:
                continue

            for fd in os.listdir(_fd_dir):
                fd_path = os.path.join(_fd_dir, fd)
                if os.path.exists(fd_path) and os.readlink(fd_path) == self.file_path:
                    all_fd.append(fd_path)

        return all_fd


def updateInspection(id, status_code):
    body = {
        "inspection_id": id,
        "status": status_code
    }
    try:
        requests.put(config.Inspection_Status_Endpoint, body)
    except Exception as e:
        logger.error("Error to update Inspection {} status. ".format(id) + str(e))


def addTaskIntoMsgQueue(data):
    Robot_Task_Cache.put(data)
    old_queue = None
    try:
        file_status = File(Robot_Task_Cache_File).status()
        if file_status['is_opened']:
            return
    except OSError as e:
        logger.info("Task MSG Queue file not exitsed!")
        old_queue = Queue()

    try:
        if old_queue is None:
            with open(Robot_Task_Cache_File, 'rb') as f:
                old_queue = pickle.load(f)
        while not Robot_Task_Cache.empty():
            task_data = Robot_Task_Cache.get_nowait()
            old_queue.append(task_data)
        with open(Robot_Task_Cache_File, 'wb') as f:
            pickle.dump(old_queue, f)   
    except Exception as e:
        logger.error("Error to insert Task data into MSG queue! " + str(e))

def getTasksFromMsgQueue():
    while File(Robot_Task_Cache_File).status()['is_opened']:
        pass
    try:
        with open(Robot_Task_Cache_File, 'rb') as f:
            task_queue = pickle.load(f)
        os.remove(Robot_Task_Cache_File)
        return task_queue
    except Exception as e:
        logger.error("Error to insert Task data into MSG queue! " + str(e))
