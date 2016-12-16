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
import time
import datetime
import json
import HTMLParser

from bs4 import BeautifulSoup
from ConfigCtrl import ConfigCtrl
from LogCtrl import LogCtrl


class CrawCtrl(object):
    """docstring for AgentCtrl"""

    def __init__(self, conf_file = None):
        self.root_path = os.path.dirname(os.path.dirname(__file__))
        self.cfgctrl = ConfigCtrl(conf_file)
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

    def crawHaoMeiSe(self, begin, end):
        new_urls = set()
        count = int(begin)
        root_url = self.cfgctrl.get_config('other', 'haomeise_root_url')
        new_urls.add(root_url + str(count))

        while len(new_urls) != 0 and count <= int(end):
            old_url = new_urls.pop()
            self.log.info(old_url)
            html_cont = self.request('GET', old_url)
            soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
            #nodes = soup.find_all('img')
            #nodes = soup.img['src']
            nodes = soup.find_all('img', src=re.compile(r"^http://.*jpg$"))
            if len(nodes) == 0:
                break

            for node in nodes:
                img = str(node['src'])
                print img

            count += 1
            new_urls.add(root_url + str(count))


if __name__ == "__main__":
    spider = CrawCtrl()
    spider.crawHaoMeiSe(21, 50)
