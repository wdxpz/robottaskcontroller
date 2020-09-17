from utils.logger import getLogger
logger = getLogger('InspectionMonitor')
logger.propagate = False

from config import Inspection_Status_Codes

Robot_Status = {
    'working': 0,
    'idle': 1,
    'failed': 3
}

class InspectionMonitor(object):

    inspection_monitor = None
   
    def __init__(self):
        self.task_list = {}

    @staticmethod
    def getInspectionMonitor():
        if InspectionMonitor.inspection_monitor is None:
            InspectionMonitor.inspection_monitor = InspectionMonitor()

        return InspectionMonitor.inspection_monitor
    

    def addTask(self, inspection_id, site_id, robot_ids):
        self.task_list[inspection_id] = {
            'site_id': site_id,
            'status': Inspection_Status_Codes['INSPECTION_STARTED'],
            'robots': {}
        }
        for id in robot_ids:
            self.task_list[inspection_id]['robots'][id] = {'status': Robot_Status['working']}

    def setTaskStatus(self, inspection_id, status):
        if inspection_id not in self.task_list.keys():
            logger.error("set task status error, no inspection id: {}".format(inspection_id))
            return
        self.task_list[inspection_id]['status'] = status

    def getTaskStatus(self, inspection_id):
        if inspection_id not in self.task_list.keys():
            logger.error("set task status error, no inspection id: {}".format(inspection_id))
            return None
        return self.task_list[inspection_id]['status']

    def rmTask(self, inspection_id):
        if inspection_id in self.task_list.keys():
            self.task_list.pop(inspection_id, None)

    def isTaskRepeated(self, inspection_id):
        if inspection_id in self.task_list.keys():
            return True
        else:
            return False

    def setRobotIdle(self, inspection_id, robot_id):
        if inspection_id not in self.task_list.keys():
            logger.error("set task status error, no inspection id: {}".format(inspection_id))
            return
        if robot_id not in self.task_list[inspection_id]['robots'].keys():
            logger.error("set robot idle error, no robot: {} in inspection {}".format(robot_id, inspection_id))
            return
        self.task_list[inspection_id]['robots'][robot_id]['status'] = Robot_Status['working']

    def setRobotFailed(self, inspection_id, robot_id):
        if inspection_id not in self.task_list.keys():
            logger.error("set task status error, no inspection id: {}".format(inspection_id))
            return
        if robot_id not in self.task_list[inspection_id]['robots'].keys():
            logger.error("set robot idle error, no robot: {} in inspection {}".format(robot_id, inspection_id))
            return
        self.task_list[inspection_id]['robots'][robot_id]['status'] = Robot_Status['failed']


    def isRobotIdle(self, robot_id, inspection_id=None):
        if inspection_id is None:
            for inspection_id in self.task_list.keys():
                if robot_id in self.task_list[inspection_id]['robots']:
                    return self.task_list[inspection_id]['robots'][robot_id]['status'] == Robot_Status['idle']
        else:
            if inspection_id in self.task_list.keys() and robot_id in self.task_list[inspection_id]['robots'].keys():
                return self.task_list[inspection_id]['robots'][robot_id]['status'] == Robot_Status['idle']

        return True
        
    def isRobotFailed(self, robot_id, inspection_id=None):
        if inspection_id is None:
            for inspection_id in self.task_list.keys():
                if robot_id in self.task_list[inspection_id]['robots']:
                    return self.task_list[inspection_id]['robots'][robot_id]['status'] == Robot_Status['failed']
        else:
            if inspection_id in self.task_list.keys() and robot_id in self.task_list[inspection_id]['robots'].keys():
                return self.task_list[inspection_id]['robots'][robot_id]['status'] == Robot_Status['failed']

        return False

    def isRobotWorking(self, robot_id, inspection_id=None):
        if inspection_id is None:
            for inspection_id in self.task_list.keys():
                if robot_id in self.task_list[inspection_id]['robots']:
                    return self.task_list[inspection_id]['robots'][robot_id]['status'] == Robot_Status['working']
        else:
            if inspection_id in self.task_list.keys() and robot_id in self.task_list[inspection_id]['robots'].keys():
                return self.task_list[inspection_id]['robots'][robot_id]['status'] == Robot_Status['working']

        return False
