#!/usr/bin/env python
#-*-coding:utf-8-*-

#Version:1.0.0
#Author: Jiwei.Zhang <jiwei.zjw@alibaba-inc.com>
#License:Copyright(c) 2016 Jiwei.Zhang

import logging
import os
import sys

log_path = os.path.join(os.path.dirname(os.getcwd()), 'log')
print log_path
log_path = os.path.abspath(log_path)
if log_path not in sys.path:
    sys.path.append(log_path)

class LogCtrl(object):
    """docstring for LogCtrl"""

    def __init__(self, log_name=None):
        log_name = log_name if log_name is not None else 'app.log'
        self.formatt = '[%(asctime)s] [%(name)s] [%(levelname)s] [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'
        logging.basicConfig(level=logging.DEBUG,
                            format=self.formatt,
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=os.path.join(log_path, log_name),
                            filemode='a')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(self.formatt)
        console.setFormatter(formatter)
        self.logger = logging.getLogger('')
        self.logger.addHandler(console)

    def getLog(self):
        return self.logger
