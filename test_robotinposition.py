import time

import config
from utils.msg_utils import sendSyncCmdMsg


sendSyncCmdMsg(inspection_id=558, site_id=123, timestamp=str(int(time.time())), 
    robot_id='tb3_01', cmd='photo')