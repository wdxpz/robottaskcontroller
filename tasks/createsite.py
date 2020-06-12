#!/usr/bin/env python
import sys
import os
import getopt

import config
from map_utils.map_utils import deleteRemoteSite, createRemoteSite, saveMap
from utils.ros_utils import checkRobotNode
from utils.logger import getLogger

logger = getLogger('createSite')
logger.propagate = False

Status_Succeeded = 0
Stauts_File_Existed = 10
Status_Failed = 20


def createSite(sitename='test', description='', forced=True):
    if not checkRobotNode('map_server', trytimes=1):
        logger.error('createsite exit! Not found map_server')
        raise Exception('not found map_server from rosnode')

    map_path = os.path.join(config.Map_Dir, sitename)

    if os.path.exists(map_path):
        if not forced:
            logger.info('site {} existed! choose not to overwrite existed site!'.format(sitename))
            return
    try:
        deleteRemoteSite(sitename)
        saveMap(map_path)
        createRemoteSite(sitename, description)
    except Exception as e:
        logger.error('createsite {} error! {}'.format(sitename, str(e)))
        raise Exception('createsite error')

    logger.info('succeeded to create site {}'.format(sitename)
    
if __name__ == '__main__':
    sitename = 'test'
    description = ''

    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "hs:d:", ['site=', 'desc='])
    except getopt.GetoptError:
        print('createsite.py -s <sitename> -d <desciption>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('createsite.py -s <sitename> -d <desciption>')
            sys.exit()
        elif opt in ('-s', '--site'):
            sitename = arg
        elif opt in ('-d', '--desc'):
            description = arg

    createSite(sitename, description)