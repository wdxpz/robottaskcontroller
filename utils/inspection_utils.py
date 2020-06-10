import requests
import json

from config import Msg_Center_Endpoint, Inspection_Status_Endpoint

from utils.logger import getLogger
logger = getLogger('utils.inspection_utils')
logger.propagate = False


def updateInspection(id, status_code):
    body = {
        "inspection_id": id,
        "status": status_code
    }
    is_error = False
    try:
        response = requests.put(Inspection_Status_Endpoint, body)
        if response.status_code != 200:
            is_error = True
    except Exception as e:
        logger.error(str(e))
        is_error = True

    if is_error:
        logger.error("Failed to update Inspection {} status to {}!".format(id, status_code))


def getTasksFromMsgQueue():
    is_error = False
    try:
        response = requests.get(Msg_Center_Endpoint)
        if response.status_code != 200:
            is_error = True
        if response.content is None or len(response.content) == 0:
            return None 
        data = json.loads(response.content)['data']
        task_data = json.loads(data)
    except Exception as e:
        logger.error(str(e))
        is_error = True

    if is_error:
        msg = "Failed to get new task data from MSG center! "
        logger.error(msg)
        return None
    

    logger.info("Succeeded to get new task data from MSG center!")
    return task_data
