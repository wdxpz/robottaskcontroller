robot_id = 'rosbot1'
task_type = 50
site_id = 'bj02'
inspection_id = 880
sim_robot_duration = 5 #minitues

Task_Inspection_AT_Rushtime = 50 #50

##robot navigation configuration
Wait_For_GoToPose_Time = 120
Holding_Step_Time = 60
Holding_Time_Variance = 1
Circle_Rotate_Steps = 4
Rotate_Speed = 30
Valid_Range_Radius = 0.1


#Kafka
Kafka_Brokers = ["192.168.12.146:9092"]
Task_Topic = "task-test"
Task_Status_Topic = "task-status-test"
Wifi_Record_Topic = "wifi-sniffer-test"
Bt_Record_Topic = "bt-sniffer-test"
Visual_Topic = "video-test"
Kafka_Blocking_time = 1

#redis
redis_host = "192.168.12.146"
redis_port = "6379"

#robot motion paras
Circle_Rotate_Steps = 4
Rotate_Speed = 30