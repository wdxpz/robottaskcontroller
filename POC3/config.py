robot_id = 'rosbot1'
task_type = 30
site_id = 'bj02'
inspection_id = 563
sim_robot_duration = 5 #minitues

Task_Inspection_AT_RUSHTIME: 50


#Kafka
Kafka_Brokers = ["192.168.12.146:9092"]
Task_Topic = "task-test"
Task_Status_Topic = "task-status-test"
Wifi_Record_Topic = "wifi-sniffer-test"
Bt_Record_Topic = "bt-sniffer-test"
Kafka_Blocking_time = 1

#redis
redis_host = "192.168.12.146"
redis_port = "6379"

#robot motion paras
Circle_Rotate_Steps = 4
Rotate_Speed = 30