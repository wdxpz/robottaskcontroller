#!/usr/bin/env python

import os
import re
import time
import requests

from wand.image import Image

import config
from utils.ros_utils import shell_cmd
from utils.logger import getLogger
logger = getLogger('map_utils')
logger.propagate = False


def saveMap(map_path):
    if not os.path.exists(map_path):
        os.makedirs(map_path)
    
    #export map from ros map_server
    mapfilepath = os.path.join(map_path, 'map')
    cmd = 'rosrun map_server map_saver -f {}'.format(mapfilepath)
    result, _ = shell_cmd(cmd)
    if result == 1:
        logger.error('saveMap: error in running ' + cmd)
        return None
    logger.info('saveMap: succeeded in export site map to path: {}'.format(map_path))
    
    mapfile = os.path.join(map_path, 'map.pgm')
    yamlfile = os.path.join(map_path, 'map.yaml')
    jpgfile = os.path.join(map_path, 'map.jpg')
    #conver jpg file form pgm file
    with Image(filename=mapfile) as img:
        img.format = 'jpeg'
        img.save(filename=jpgfile)
    if os.path.exists(jpgfile):
        logger.info('saveMap: succeeded in convert site map to jpeg into path: {}'.format(map_path))
        return (mapfile, yamlfile, jpgfile)
    else:
        logger.error('saveMap: failed in convert site map to jpeg into path: {}'.format(map_path))
        return None
        
def deleteRemoteSite(sitename):
    logger.info('delete site {} from remote db'.format(sitename))
    # logger.info(config.Delete_Site_Endpoint)
    # endpoint = config.Delete_Site_Endpoint.format(sitename)
    endpoint = config.Delete_Site_Endpoint + sitename
    # logger.info(endpoint)
    response = requests.delete(endpoint)
    
    if response.status_code != 200:
        raise Exception('deleteRemoteSite Error!')
    logger.info('utils: succeeded in delete site {} from remote db'.format(sitename))


def createRemoteSite(sitename, description):
    logger.info('create site {} in remote db'.format(sitename))
    jpgfile = 'map.jpg'
    jpgfilepath = os.path.join(config.Map_Dir, sitename, jpgfile)

    files = {
        'site_map': (jpgfile, open(jpgfilepath, 'rb'))
        #'site_map': open(jpgfilepath, 'rb')
    }
    values = {
        'site_name': sitename,
        'site_description': description
    }

    responose = requests.post(config.Create_Site_Endoint, files=files, data=values)

    if responose.status_code != 200:
        raise Exception('createRemoteSite Error! status_code: {}'.format(responose.status_code))
    logger.info('utils: succeeded in create site {} from remote db'.format(sitename))


if __name__ == '__main__':
    # print(checkServer('rosout'))
    print(checkServer('map_server'))

    cmd = "rosrun map_server map_save -f {}".format('/home/sw/map')
    print(shell_cmd(cmd))

