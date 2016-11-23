#!/usr/bin/env python
#-*-coding:utf-8-*-

#Version:1.0.0
#Author: Jiwei.Zhang <jiwei.zjw@alibaba-inc.com>
#License:Copyright(c) 2016 Jiwei.Zhang

import os
import ConfigParser

class ConfigCtrl(object):
    """docstring for AgentCtrl"""

    def __init__(self, conf_file = None):
        self.root_path = os.path.dirname(os.path.dirname(__file__))
        self.conf_path = os.path.join(self.root_path, "conf")
        self.conf_file = os.path.join(self.conf_path, conf_file) if conf_file else os.path.join(self.conf_path, "app.cfg")
        self.conf = ConfigParser.ConfigParser()

    def get_config(self, section, key):
        if not os.path.exists(self.conf_file):
            return None

        self.conf.read(self.conf_file)
        if self.conf.has_option(section, key):
            return self.conf.get(section, key)
        else:
            return None

    # use this method as less as possible
    def set_config(self, section, key, value):
        if not os.path.exists(self.conf_file):
            return None

        cfgfile = open(self.conf_file, 'a')
        if not self.conf.has_section(section):
            self.conf.add_section(section)
            self.conf.set(section, key, value)
        else:
            self.conf.set(section, key, value)

        self.conf.write(cfgfile)
        cfgfile.close()

if __name__ == "__main__":
    cfgctrl = ConfigCtrl()
    cfgctrl.set_config('application', 'test', 'hello world')
    print cfgctrl.get_config('application', 'test')
    cfgctrl.conf.remove_option('application', 'test')
    print cfgctrl.get_config('application', 'test')
    print cfgctrl.get_config('mysql', 'mysql_host')
