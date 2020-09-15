import requests
import math

from turtlebot_rotate import  PI

def distance(pos1, pos2):
    return math.sqrt(math.pow((pos1[0]-pos2[0]), 2) + math.pow((pos1[1]-pos2[1]), 2))

def radiou2dgree(radius):
    return radius*180/PI