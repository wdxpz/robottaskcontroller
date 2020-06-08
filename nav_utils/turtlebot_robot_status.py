robot_status = {}

def setRobotWorking(id, inspection_id):
    robot_status[id] = inspection_id

def setRobotIdel(id):
    if id in robot_status.keys():
        robot_status.pop(id, None)

def isRobotWorking(id):
    if id in robot_status.keys():
        return True
    else:
        return False

def isInspectionRepeated(inspection_id):
    #to prevent simutaneous inspection_id
    for _, inspection in robot_status.items():
        if inspection == inspection_id:
            return True
    return False

def isInspectionRunning():
    if len(robot_status.keys()) > 0:
        return True
    else:
        return False