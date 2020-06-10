
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = False

PI = 3.1415926535897

#logger
log_file = os.path.join(BASE_DIR, 'robot_task_controller.log')

#map service
Map_Dir = os.path.join(BASE_DIR, 'map')
Create_Site_Endoint = 'http://www.bestfly.ml:8000/site/'
Delete_Site_Endpoint = 'http://www.bestfly.ml:8000/site/'

#robot launch configuration
ROS_Launch_File = 'catkin_ws/src/multirobot_nv/launch/startall.launch'
Launch_Max_Try = 3

#robot pose initialization configration
Trial_Set_Pose_Count = 3

#robot navigation configuration
Wait_For_GoToPose_Time = 60
Holding_Step_Time = 20
Holding_Time_Variance = 1
Circle_Rotate_Steps = 4
Rotate_Speed = 30
Valid_Range_Radius = 0.1
Holding_Time = Holding_Step_Time+360/Rotate_Speed+Holding_Time_Variance
##time interval to upload to tsdb
Pos_Collect_Interval = 0.2
Upload_Interval = 2
##navigation prcocess pickle file
Nav_Pickle_File = os.path.join(BASE_DIR, 'nav_process.pkl')
#tsdb
upload_URL = 'www.bestfly.ml'
upload_PORT = 8086
upload_DB = 'robot'
Table_Name_Robot_Pos = 'robot_poss'
Table_Name_Robot_Event = 'robot_event'


#Inspection Status Codes
Inspection_Status_Codes ={
    'CMD_SENT': 100,
    'CDM_ACCEPTED': 110,
    'INSPECTION_STARTED': 130, 
    'INSPECTION_FINISHED': 140,
    'ERR_CMD_PARAMETERS': 200,
    'ERR_ROBOT_OCCUPIED': 210,
    'ERR_ROBOT_START': 220,
    'ERR_INSPECTION_STILL_RUNNING': 230
}
#Inspection Status Update Entrypoint
Inspection_Status_Endpoint='http://www.bestfly.ml:8000/inspection/'

#MSG center entrypoint
Msg_Center_Endpoint='http://127.0.0.1:8001/tasks/'