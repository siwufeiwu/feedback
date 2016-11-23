#!/usr/bin/env python
#-*-coding:utf-8-*-

#Version:1.0.0
#Author: Jiwei.Zhang <jiwei.zjw@alibaba-inc.com>
#License:Copyright(c) 2016 Jiwei.Zhang

import tornado.web
import tornado.gen
import tornado.escape
import logging
import json
from BaseHandler import BaseHandler


class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html')
