#!/usr/bin/env python
#-*-coding:utf-8-*-

#Version:1.0.0
#Author: Jiwei.Zhang <jiwei.zjw@alibaba-inc.com>
#License:Copyright(c) 2016 Jiwei.Zhang

import os,sys
import re
import urlparse
import urllib2
import urllib
import chardet
import time
import datetime
import json
import HTMLParser

from bs4 import BeautifulSoup
from ConfigCtrl import ConfigCtrl
from LogCtrl import LogCtrl
from MysqlCtrl import MysqlCtrl


class SpiderCtrl(object):
    """docstring for AgentCtrl"""

    def __init__(self, conf_file = None):
        self.root_path = os.path.dirname(os.path.dirname(__file__))
        self.cfgctrl = ConfigCtrl(conf_file)
        self.mysql = MysqlCtrl()
        self.log = LogCtrl().getLog()
        self.day = 15

    def request(self, method, url, data=None, retry=5):
        if not url or not method:
            return None
        send_header = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Upgrade-Insecure-Requests':1,
            # 'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6'
        }
        while retry != 0:
            if method == 'GET':
                req = urllib2.Request(url)
            elif method == 'POST':
                url_value = urllib.urlencode(data)
                req = urllib2.Request(url, data=url_value)
            req.headers = send_header
            # req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0')
            # print req.get_header('User-Agent')
            try:
                response = urllib2.urlopen(req, timeout=120)
                content = response.read()
                self.log.info(len(content))
                if (response.getcode() != 200) or (len(content) < 200):
                    self.log.info('count:%d, request failed: %s' % ((5 - retry + 1), url))
                    time.sleep(0.5)
                    response = urllib2.urlopen(req, timeout=120)
                    content = response.read()
                else:
                    break
            except Exception as e:
                self.log.error(str(e))
            retry -= 1
        # print response.info()
        return content

    def handleHtmlEncoding(self, html_cont):
        # dist_type = sys.getfilesystemencoding()
        dist_type = 'utf-8'
        org_type = chardet.detect(html_cont)['encoding']
        if org_type == 'gkb' or org_type == 'GBK':
            return html_cont.decode('gbk', 'ignore').encode(dist_type)
        elif org_type == 'gb2312' or org_type == 'GB2312':
            return html_cont.decode('gb2312', 'ignore').encode(dist_type)
        elif org_type == 'utf-8' or org_type == 'UTF-8':
            return html_cont
        else:
            return html_cont.decode(org_type, 'ignore').encode(dist_type)

    def crawHuaWeiMacket(self, app='shuqi', switch = True):
        new_urls = set()
        count = 1
        root_url = self.cfgctrl.get_config(app, 'huawei_root_url')
        new_urls.add(root_url + str(count))

        while len(new_urls) != 0:
            old_url = new_urls.pop()
            self.log.info(old_url)
            html_cont = self.request('GET', old_url)
            soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
            #print soup.original_encoding
            nodes = soup.find_all('div', class_=re.compile(r"comment"))
            node_total = soup.find_all('span', class_=re.compile(r"title"))

            for node in nodes:
                node_content = node.find('p', class_='content')
                node_sub = node.find('p', class_='sub').find_all('span')
                name = str(node_sub[1].contents).lstrip('[').rstrip(']').decode('unicode-escape').replace("'", '').replace('u', '')
                model = str(node_sub[3].contents).lstrip('[').rstrip(']').decode('unicode-escape').replace("'", '').replace('u', '')
                ctime = str(node_sub[4].contents).lstrip('[').rstrip(']').replace('u', '').replace("'", '')
                ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.mktime(datetime.datetime.strptime(ctime,"%Y-%m-%d %H:%M").timetuple())))
                ctime = time.mktime(time.strptime(ctime,'%Y-%m-%d %H:%M:%S'))
                if (not switch ) and (int(ctime) < int(time.time() - self.day*24*60*60)):
                    self.log.info('craw to the end, total crawed %d' % (count))
                    return
                ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ctime)))
                date = ctime.split()[0]
                comment = str(node_content.contents).lstrip('[').rstrip(']').replace('\\r', '').replace('\\n', '').replace('\\t', '').decode('unicode-escape').replace("'", '').replace('u', '').replace('\\', '').replace('"', '')
                #preg = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#��?%…���??&*（）]')
                #preg = re.compile(u'\U00010000-\U0010ffff')
                preg = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
                name = preg.sub('', unicode(name))
                comment = preg.sub('', unicode(comment))
                model = re.sub(r'<a href="http://appstore.hawei.com:80/">', '', model)
                model = re.sub(r'</a>', '', model)
                sql = 'insert into comment (`source`, `app`, `comment_time`, `content`, `name`, `model`, `date`) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s") ' % (u'华为应用市场', str(app), ctime, comment, name, model, date)
                self.log.info(sql)
                if self.mysql.insert(sql) is None:
                    self.log.error('mysql insert failed')
                count += 1

            new_urls.add(root_url + str(int(old_url.split('=')[len(old_url.split('=')) - 1]) + 1))
        self.log.info('华为应用市场爬取[%s]评论数为:%s' % ( str(app), str(count)))

    def crawBdShouJiZhuShouMacket(self, app = 'shuqi', switch = True):
        new_urls = set()
        count = 1
        root_url = self.cfgctrl.get_config(app, 'baidushoujizhushou_root_url')
        new_urls.add(root_url + str(count))

        while len(new_urls) != 0:
            old_url = new_urls.pop()
            self.log.info(old_url)
            html_cont = self.request('GET', old_url)
            soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
            #print soup.original_encoding
            nodes = soup.find_all('li', class_=re.compile(r"comment"))
            if len(nodes) == 0:
                break

            for node in nodes:
                node_content = node.find('p').contents[0]
                node_name = node.find('em').contents[0]
                node_time = node.find('div', class_='comment-time').contents[0]
                preg = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
                name = preg.sub('', unicode(node_name))
                comment = preg.sub('', unicode(node_content))
                ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.mktime(datetime.datetime.strptime(node_time,"%Y-%m-%d %H:%M").timetuple())))
                ctime = time.mktime(time.strptime(ctime,'%Y-%m-%d %H:%M:%S'))
                if (not switch ) and (int(ctime) < int(time.time() - self.day*24*60*60)):
                    continue
                ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ctime)))
                date = ctime.split()[0]
                sql = 'insert into comment (`source`, `app`, `comment_time`, `content`, `name`, `date`) values ("%s", "%s", "%s", "%s", "%s", "%s") ' % (u'百度手机助手', str(app), ctime, comment, name, date)
                self.log.info(sql)
                if self.mysql.insert(sql) is None:
                    self.log.error('mysql insert failed')
                count += 1

            new_urls.add(root_url + str(int(old_url.split('=')[len(old_url.split('=')) - 1]) + 1))
        self.log.info('百度手机助手应用市场爬取[%s]评论数为:%s' % ( str(app), str(count)))

    def crawWanDouJia(self, app='shuqi', switch = True):
        new_urls = set()
        count = 1
        root_url = self.cfgctrl.get_config(app, 'wandoujia_root_url')
        new_urls.add(root_url + str(count))

        while len(new_urls) != 0:
            old_url = new_urls.pop()
            self.log.info(old_url)
            html_cont = self.request('GET', old_url)
            soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
            #print soup.original_encoding
            nodes = soup.find_all('li', class_=re.compile(r"normal-li"))
            if len(nodes) == 0:
                break

            for node in nodes:
                name = node.find_all('span')[0].contents[0]
                comment = node.find_all('span')[2].contents[0]
                node_time = node.find_all('span')[1].contents[0]
                time_now = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()-24*60*60))
                try:
                    ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.mktime(datetime.datetime.strptime(time_now[:-5] + node_time,"%Y-%m-%d %H:%M").timetuple())))
                except Exception as e:
                    self.log.warning('time is %s parser failed' % (node_time))
                    if len(re.findall(r"\d+", node_time)) == 0:
                        continue
                    time_dig = re.findall(r"\d+", node_time)
                    time_str = time_now[:5] + str(time_dig[0]) + '-' + str(time_dig[1]) + time_now[-6:]
                    ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.mktime(datetime.datetime.strptime(time_str,"%Y-%m-%d %H:%M").timetuple())))
                ctime = time.mktime(time.strptime(ctime,'%Y-%m-%d %H:%M:%S'))
                if (not switch ) and (int(ctime) < int(time.time() - self.day*24*60*60)):
                    continue
                ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ctime)))
                date = ctime.split()[0]
                sql = 'insert into comment (`source`, `app`, `comment_time`, `content`, `name`, `date`) values ("%s", "%s", "%s", "%s", "%s", "%s") ' % (u'豌豆��?', str(app), ctime, comment, name, date)
                self.log.info(sql)
                if self.mysql.insert(sql) is None:
                    self.log.error('mysql insert failed')
                count += 1

            new_urls.add(root_url + str(int(old_url.split('comment')[len(old_url.split('comment')) - 1]) + 1))
        self.log.info('豌豆荚应用市场爬取[%s]评论:%s' % (str(app),  str(count)))

    def crawYingYongBao(self, app='shuqi', switch = True):
        new_urls = set()
        count = 1
        root_url = self.cfgctrl.get_config(app, 'yingyongbao_root_url')
        new_urls.add(root_url)

        while len(new_urls) != 0:
            old_url = new_urls.pop()
            self.log.info(old_url)
            json_str = self.request('GET', old_url)
            json_dict = json.loads(json_str)
            if not json_dict.has_key('obj') or json_dict is None:
                self.log.warning('json data has no obj field')
                break

            total = int(json_dict['obj']['total'])
            next_param = json_dict['obj']['contextData']
            has_next = json_dict['obj']['hasNext']
            if has_next != 1:
                self.log.warning('spider has craw to end, total crawed %d' % (total))
                break

            for node in json_dict['obj']['commentDetails']:
                content = node['content']
                name = node['nickName']
                score = node['score']
                ctime = node['createdTime']
                if (not switch ) and (int(ctime) < int(time.time() - self.day*24*60*60)):
                    self.log.info('应用宝爬取[%s]评论:%s' % ( str(app), str(count)))
                    return
                ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ctime)))
                date = ctime.split()[0]
                preg = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
                name = preg.sub('', unicode(name))
                content = preg.sub('', unicode(content))
                sql = 'insert into comment (`source`, `app`, `comment_time`, `content`, `name`, `date`, `comment_level`) values ("%s", "%s", "%s", "%s", "%s", "%s", "%d") ' % (u'应用��?', str(app), ctime, content, name, date, score)
                self.log.info(sql)
                if self.mysql.insert(sql) is None:
                    self.log.error('mysql insert failed')
                count += 1

            new_urls.add(root_url + next_param)
        self.log.info('应用宝爬取[%s]评论��?:%s' % ( str(app), str(count)))

    def craw360(self, app='shuqi', switch = True):
        new_urls = set()
        count = 1
        data = {
            'callback':'jQuery172014259591416684492_1479436591868',
            'c':'message',
            'a':'getmessage',
            'start':0,
            'count':10
        }

        if app == 'shuqi':
            data['baike'] = '书旗免费小说'
        else:
            data['baike'] = 'iReader'

        root_url = self.cfgctrl.get_config(app, '360_root_url')
        new_urls.add(root_url)

        while len(new_urls) != 0:
            old_url = new_urls.pop()
            self.log.info(old_url+'?'+urllib.urlencode(data))
            json_str = self.request('POST', old_url,data)
            json_str = json_str.replace('try{jQuery172014259591416684492_1479436591868(', '').replace(');}catch(e){}', '')
            json_dict = json.loads(json_str)
            if not json_dict.has_key('data') or json_dict is None:
                self.log.warning('json data has no data field')
                break

            total = int(json_dict['data']['total'])
            if len(json_dict['data']['messages']) == 0:
                self.log.warning('spider has craw to end, total crawed %d' % (total))
                return

            for node in json_dict['data']['messages']:
                content = node['content']
                name = node['username']
                score = int(node['score'])
                ctime = node['create_time']
                ctime = time.mktime(time.strptime(ctime,'%Y-%m-%d %H:%M:%S'))
                model = node['model']
                if (not switch ) and (int(ctime) < int(time.time() - self.day*24*60*60)):
                    self.log.info('360手机助手爬取[%s]评论数为:%s' % (str(app),  str(count)))
                    return
                ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ctime)))
                date = ctime.split()[0]
                preg = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
                name = preg.sub('', unicode(name))
                model = preg.sub('', unicode(model))
                content = preg.sub('', unicode(content))
                sql = 'insert into comment (`source`, `app`, `comment_time`, `content`, `name`, `date`, `comment_level`, `model`) values ("%s", "%s", "%s", "%s", "%s", "%s", "%d", "%s") ' % (u'360手机助手', str(app), ctime, content, name, date, score, model)
                self.log.info(sql)
                if self.mysql.insert(sql) is None:
                    self.log.error('mysql insert failed')
                count += 1
            data['start'] += 10
            new_urls.add(root_url)
        self.log.info('360手机助手爬取[%s]评论数为:%s' % ( str(app), str(count)))

    def crawOppo(self, app='shuqi', switch = True):
        new_urls = set()
        count = 1
        page_total = 1
        page_curr = 1
        data = {
            'page':1
        }

        if app == 'shuqi':
            data['id'] = 10618969
        else:
            data['id'] = 10634088

        root_url = self.cfgctrl.get_config(app, 'oppo_root_url')
        new_urls.add(root_url)

        while len(new_urls) != 0 and page_curr <= page_total:
            old_url = new_urls.pop()
            self.log.info(old_url+'?'+urllib.urlencode(data))
            json_str = self.request('POST', old_url, data)
            json_dict = json.loads(json_str)
            if not json_dict.has_key('commentsList') or json_dict is None:
                self.log.warning('json data has no obj field')
                break

            total = int(json_dict['totalNum'])
            page_total = int(json_dict['totalPage'])
            page_curr = int(json_dict['currPage'])

            for node in json_dict['commentsList']:
                content = node['word']
                name = node['userNickName']
                model = node['source']
                version = node['version']
                ctime = node['createDate']
                ctime = time.mktime(time.strptime(ctime.replace('.', '-') + ' 12:00:00','%Y-%m-%d %H:%M:%S'))
                if (not switch ) and (int(ctime) < int(time.time() - self.day*24*60*60)):
                    self.log.info('oppo应用市场爬取[%s]评论数为:%s' % (str(app),  str(count)))
                    return
                ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ctime)))
                date = ctime.split()[0]
                preg = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
                name = preg.sub('', unicode(name))
                content = preg.sub('', unicode(content))
                model = preg.sub('', unicode(model))
                sql = 'insert into comment (`source`, `app`, `comment_time`, `content`, `name`, `date`, `model`, `version`) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s") ' % (u'oppo应用商店', str(app), ctime, content, name, date, model, version)
                self.log.info(sql)
                if self.mysql.insert(sql) is None:
                    self.log.error('mysql insert failed')
                count += 1

            data['page'] += 1
            new_urls.add(root_url)
        self.log.info('oppo应用市场爬取[%s]评论数为:%s' % (str(app),  str(count)))

    def crawMeiZu(self, app='shuqi', switch = True):
        new_urls = set()
        count = 1
        data = {
            'start':0,
            'max':10
        }

        if app == 'shuqi':
            data['app_id'] = 254019
        else:
            data['app_id'] = 1848956

        root_url = self.cfgctrl.get_config(app, 'meizu_root_url')
        new_urls.add(root_url)
        h = HTMLParser.HTMLParser()

        while len(new_urls) != 0:
            old_url = new_urls.pop()
            self.log.info(old_url+'?'+urllib.urlencode(data))
            json_str = self.request('POST', old_url, data)
            json_dict = json.loads(json_str)
            if not json_dict.has_key('value') or json_dict is None:
                self.log.warning('json data has no obj field')
                break

            if len(json_dict['value']['list']) == 0:
                break

            for node in json_dict['value']['list']:
                content = node['comment']
                name = node['user_name']
                content = h.unescape(content)
                name = h.unescape(name)
                version = node['version_name']
                ctime = node['create_time']
                ctime = time.mktime(time.strptime(ctime + ' 12:00:00','%Y-%m-%d %H:%M:%S'))
                if (not switch ) and (int(ctime) < int(time.time() - self.day*24*60*60)):
                    self.log.info('魅族应用市场爬取[%s]评论数为:%s' % (str(app),  str(count)))
                    return
                ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ctime)))
                date = ctime.split()[0]
                preg = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
                name = preg.sub('', unicode(name))
                content = preg.sub('', unicode(content))
                sql = 'insert into comment (`source`, `app`, `comment_time`, `content`, `name`, `date`, `version`) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s") ' % (u'魅族应用商店',  str(app), ctime, content, name, date, version)
                self.log.info(sql)
                if self.mysql.insert(sql) is None:
                    self.log.error('mysql insert failed')
                count += 1

            data['start'] += 10
            new_urls.add(root_url)
        self.log.info('魅族应用市场爬取[%s]评论数为:%s' % (str(app), str(count)))




if __name__ == "__main__":
    spider = SpiderCtrl()
    spider.mysql.connect()
    for app in ['shuqi', 'zhangyue']:
        try:
            spider.crawHuaWeiMacket(app=app, switch=False)
            spider.crawBdShouJiZhuShouMacket(app=app, switch=False)
            spider.crawWanDouJia(app=app, switch=False)
            spider.crawYingYongBao(app=app, switch=False)
            spider.craw360(app=app, switch=False) #403
            spider.crawOppo(app=app, switch=False)
            spider.crawMeiZu(app=app, switch=False)
            spider.log.info("%s craw all market done" % app)
            time.sleep(5)
        except Exception as e:
            spider.log.error("========================================")
            spider.log.error("spider has occued a error")
            time.sleep(5)
            continue
    spider.mysql.destroy()
