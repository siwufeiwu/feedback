#!/usr/bin/env python
#-*-coding:utf-8-*-

#Version:1.0.0
#Author: Jiwei.Zhang <jiwei.zjw@alibaba-inc.com>
#License:Copyright(c) 2016 Jiwei.Zhang

import MySQLdb
from MySQLdb import converters
from LogCtrl import LogCtrl
from ConfigCtrl import ConfigCtrl


class MysqlCtrl(object):
    """docstring for MysqlCtrl"""

    def __init__(self, conf_file = None):
        self.cfgctrl = ConfigCtrl(conf_file)
        self.log = LogCtrl().getLog()

    def init(self, conf=None):
        conv = converters.conversions.copy()
        conv[246] = float    # convert decimals to floats
        conv[12] = str       # convert datetime to strings
        self.conf = {
            'host':self.cfgctrl.get_config('mysql', 'mysql_host'),
            'port':int(self.cfgctrl.get_config('mysql', 'mysql_port')),
            'user':self.cfgctrl.get_config('mysql', 'mysql_user'),
            'passwd':self.cfgctrl.get_config('mysql', 'mysql_password'),
            'db':self.cfgctrl.get_config('mysql', 'mysql_database'),
            'charset':self.cfgctrl.get_config('mysql', 'mysql_charset'),
        }

        self.conf = conf if conf is not None else self.conf
        try:
            self.connect = MySQLdb.connect(
                connect_timeout=20,
                host=self.conf['host'],
                port=self.conf['port'],
                user=self.conf['user'],
                passwd=self.conf['passwd'],
                db=self.conf['db'],
                charset=self.conf['charset'],
                conv=conv)
            self.log.info('mysql connect success')
        except Exception as e:
            self.log.error(str(e))

    def connect(self):
        self.init()
        return self.connect

    def insert(self, sql):
        cursor = self.connect.cursor()
        try:
            cursor.execute(sql)
            self.connect.commit()
            return cursor.lastrowid
        except Exception as e:
            self.log.error(str(e))
            self.connect.rollback()
            return  None

    def getAllRecord(self, sql):
        res_arr = []
        cursor = self.connect.cursor()
        cursor.execute(sql)
        for row in cursor.fetchall():
            res = {}
            i = 0
            for field_desc in cursor.description:
                res[field_desc[0]] = row[i]
                i += 1
            res_arr.append(res)
        return res_arr




    def destroy(self):
        self.connect.close()
