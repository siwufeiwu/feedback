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
from bs4 import BeautifulSoup
from ConfigCtrl import ConfigCtrl

class SpiderCtrl(object):
    """docstring for AgentCtrl"""

    def __init__(self, conf_file = None):
        self.root_path = os.path.dirname(os.path.dirname(__file__))
        self.cfgctrl = ConfigCtrl()

    def request(self, method, url, data, retry=2):
        if not url or not method:
            return None
        while retry != 0:
            if method == 'GET':
                url_value = urllib.urlencode(data)
                response = urllib2.urlopen(url + '?' + url_value)
                if response.getcode() != 200:
                    response = urllib2.urlopen(url + '?' + url_value)
                else:
                    break
            elif method == 'POST':
                url_value = urllib.urlencode(data)
                send_header = {
                    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    # 'Accept-Encoding':'gzip, deflate, sdch',
                    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6'
                }
                req = urllib2.Request(url, data=url_value)
                req.headers = send_header
                # req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0')
                # print req.get_header('User-Agent')
                response = urllib2.urlopen(req, timeout=60)
                if response.getcode() != 200:
                    response = urllib2.urlopen(req, timeout=60)
                else:
                    break
            retry -= 1
        # print response.info()
        return response.read()

    def handleHtmlEncoding(self, html_cont):
        # dist_type = sys.getfilesystemencoding()
        dist_type = 'utf-8'
        org_type = chardet.detect(html_cont)['encoding']
        print org_type, dist_type
        if org_type == 'gkb' or org_type == 'GBK':
            return html_cont.decode('gbk', 'ignore').encode(dist_type)
        elif org_type == 'gb2312' or org_type == 'GB2312':
            return html_cont.decode('gb2312', 'ignore').encode(dist_type)
        elif org_type == 'utf-8' or org_type == 'UTF-8':
            return html_cont
        else:
            return html_cont.decode(org_type, 'ignore').encode(dist_type)

    def crawHuaWeiMacket(self, switch = True):
        if not switch:
            return True

        new_urls = set()
        old_urls = set()
        limit, count = 0, 0
        root_url = 'http://appstore.huawei.com/comment/commentAction.action'
        data = {
            'appId':'C6092',
            'appName':'书旗小说',
            '_page':1
        }
        new_urls.add(root_url)
        # links = soup.find_all('a', href=re.compile(r"/view/\d+\.htm"))
        # for link in links:
        #     new_url = link['href']
        #     new_full_url = urlparse.urljoin(page_url, new_url)
        #     new_urls.add(new_full_url)

        while len(new_urls) != 0:
            html_cont = self.request('POST', new_urls.pop(), data)
            # print html_cont
            soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
            # print soup.original_encoding
            nodes = soup.find_all('div', class_=re.compile(r"comment"))

            comment_list = []
            for node in nodes:
                node_content = node.find('p', class_='content')
                node_sub = node.find('p', class_='sub').find_all('span')
                contact = str(node_sub[1].contents).lstrip('[').rstrip(']')
                model = str(node_sub[3].contents).lstrip('[').rstrip(']')
                ctime = str(node_sub[4].contents).lstrip('[').rstrip(']').replace('u', '').replace("'", '')
                ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.mktime(datetime.datetime.strptime(ctime,"%Y-%m-%d %H:%M").timetuple())))
                comment = str(node_content.contents).lstrip('[').rstrip(']').replace('\\r', '').replace('\\n', '').replace('\\t', '').decode('unicode-escape')
                print contact, model, ctime
                comment_list.append(comment)


if __name__ == "__main__":
    spider = SpiderCtrl()
    spider.crawHuaWeiMacket()
