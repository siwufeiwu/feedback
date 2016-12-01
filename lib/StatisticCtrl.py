#!/usr/bin/env python
#-*-coding:utf-8-*-

#Version:1.0.0
#Author: Jiwei.Zhang <jiwei.zjw@alibaba-inc.com>
#License:Copyright(c) 2016 Jiwei.Zhang

import os,sys
import re
import time
import datetime
import csv
import codecs

from ConfigCtrl import ConfigCtrl
from LogCtrl import LogCtrl
from MysqlCtrl import MysqlCtrl


class StatisticCtrl(object):
    """docstring for StatisticCtrl"""

    def __init__(self, conf_file = None):
        self.cfgctrl = ConfigCtrl(conf_file)
        self.mysql = MysqlCtrl()
        self.log = LogCtrl().getLog()
        self.market = {
            '1':u'百度手机助手',
            '2':u'应用宝',
            '3':u'安智市场',
            '4':u'华为应用市场',
            '5':u'豌豆荚',
            '6':u'360手机助手',
            '7':u'oppo应用商店',
            '8':u'魅族应用商店'
        }

    def makeMarketSourceTotalWithDate(self, file_name=u'各大应用市场每天的评论数目.csv'):
        csv_data = {}
        sql = "select date, source,  count(source) as total from comment  where date>='%s'  group by source, date order by date asc" % ('2016-10-27')
        all_records = self.mysql.getAllRecord(sql)
        if len(all_records) == 0:
            self.log.warning('query res None, sql is %s' % (sql))
            return
        for row in all_records:
            if not csv_data.has_key(str(row['date'])):
                csv_data[str(row['date'])] = {}
            if not csv_data[str(row['date'])].has_key(int(row.get('source', 0))):
                csv_data[str(row['date'])][int(row.get('source', 0))] = 0
            csv_data[str(row['date'])][int(row.get('source', 0))] = int(row.get('total', 0))

        csvfile = file(file_name, 'wb')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['日期', '百度手机助手', '应用宝', '华为应用市场', '豌豆荚', '360手机助手', 'oppo应用商店', '魅族应用商店'])
        data = []
        for k,v in csv_data.items():
            self.log.info(str(k) + str(v))
            data.append((k, v.get(1,0), v.get(2, 0), v.get(4, 0), v.get(5,0), v.get(6,0), v.get(7,0), v.get(8,0)))
        data.sort(key=lambda x : str(x[0]))
        writer.writerows(data)
        csvfile.close()

    def makeMarketCategoryDetail(self, file_name=u'各大应用市场评论类型详情.csv'):
        sql = "SELECT source, comment_type, COUNT(source) as total FROM comment WHERE date>='2016-10-27' GROUP BY source, comment_type ORDER BY source"
        all_records = self.mysql.getAllRecord(sql)
        if len(all_records) == 0:
            self.log.warning('query res None, sql is %s' % (sql))
            return
        csv_data = {}
        for row in all_records:
            if not csv_data.has_key(str(row['source'])):
                csv_data[str(row['source'])] = {}
            if not csv_data[str(row['source'])].has_key(int(row.get('comment_type', 0))):
                csv_data[str(row['source'])][int(row.get('comment_type', 0))] = 0
            csv_data[str(row['source'])][int(row.get('comment_type', 0))] = int(row.get('total', 0))

        csvfile = file(file_name, 'wb')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['市场', '需求类', 'bug类', '咨询类', '体验类', '竞品对比', '其他'])
        data = []
        for k,v in csv_data.items():
            self.log.info(str(k) + str(v))
            if k == 0: continue
            self.log.info(self.market.get(k))
            data.append((k, v.get(1,0), v.get(2, 0), v.get(3, 0), v.get(4,0), v.get(5,0), v.get(6,0)))
        data.sort(key=lambda x : str(x[0]))
        writer.writerows(data)
        csvfile.close()

    def makeMarketCategoryTotal(self, file_name=u'各大应用市场各评论类型分布.csv'):
        date = '2016-10-27'
        sql = "SELECT comment_type, COUNT(comment_type) as total  FROM comment WHERE date>='%s' GROUP BY comment_type ORDER BY comment_type" % (date)
        all_records = self.mysql.getAllRecord(sql)
        if len(all_records) == 0:
            self.log.warning('query res None, sql is %s' % (sql))
            return
        sql = "SELECT count(*) as total FROM `comment`  WHERE date>='%s'" % (date)
        total = self.mysql.getAllRecord(sql)[0]['total']

        csvfile = file(file_name, 'wb')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['类型', '占比'])
        data = []
        for row in all_records:
            self.log.info(str(row))
            if int(row['comment_type']) == 0: continue
            data.append((int(row['comment_type']), (float(row.get('total', 0)) / total ) * 100))
        # data.sort(key=lambda x : str(x[0]))
        writer.writerows(data)
        csvfile.close()


    def makeMarketMoodDetail(self, file_name=u'各大应用市场情绪详情.csv'):
        sql = "SELECT source, comment_level, COUNT(source) as total FROM comment WHERE date>='2016-10-27' GROUP BY source, comment_level ORDER BY source"
        all_records = self.mysql.getAllRecord(sql)
        if len(all_records) == 0:
            self.log.warning('query res None, sql is %s' % (sql))
            return
        csv_data = {}
        for row in all_records:
            if not csv_data.has_key(str(row['source'])):
                csv_data[str(row['source'])] = {}
            if not csv_data[str(row['source'])].has_key(int(row.get('comment_level', 0))):
                csv_data[str(row['source'])][int(row.get('comment_level', 0))] = 0
            csv_data[str(row['source'])][int(row.get('comment_level', 0))] = int(row.get('total', 0))

        csvfile = file(file_name, 'wb')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['市场', '好评', '一般', '差评'])
        data = []
        for k,v in csv_data.items():
            self.log.info(str(k) + str(v))
            if k == 0: continue
            self.log.info(self.market.get(k))
            data.append((k, v.get(1,0), v.get(2, 0), v.get(3, 0)))
        data.sort(key=lambda x : str(x[0]))
        writer.writerows(data)
        csvfile.close()


    def makeMarketMoodTotal(self, file_name=u'各大应用市场情绪分布.csv'):
        date = '2016-10-27'
        sql = "SELECT comment_level, COUNT(comment_level) as total  FROM comment WHERE date>='%s' GROUP BY comment_level ORDER BY comment_level" % (date)
        all_records = self.mysql.getAllRecord(sql)
        if len(all_records) == 0:
            self.log.warning('query res None, sql is %s' % (sql))
            return
        sql = "SELECT count(*) as total FROM `comment`  WHERE date>='%s'" % (date)
        total = self.mysql.getAllRecord(sql)[0]['total']

        csvfile = file(file_name, 'wb')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['类型', '占比'])
        data = []
        for row in all_records:
            self.log.info(str(row))
            if int(row['comment_level']) == 0: continue
            data.append((int(row['comment_level']), (float(row.get('total', 0)) / total ) * 100))
        # data.sort(key=lambda x : str(x[0]))
        writer.writerows(data)
        csvfile.close()


if __name__ == "__main__":
    spider = StatisticCtrl()
    spider.mysql.connect()
    spider.makeMarketSourceTotalWithDate()
    spider.makeMarketCategoryDetail()
    spider.makeMarketCategoryTotal()
    spider.makeMarketMoodDetail()
    spider.makeMarketMoodTotal()
    spider.mysql.destroy()
