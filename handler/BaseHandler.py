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
from lib.ErrorCtrl import ErrorCtrl


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_one_poem(self, id):
        return self.db.get("select * from authors where id = %s", int(id))

    def get_all(self):
        return self.db.query("select * from authors")

    def set_crx_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET,DELETE')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
        self.set_header("Content-Type", "application/json")

    def return_err(self,errno):
        logger.warning('errno:%d',errno)
        res = ErrorCtrl.get_error(errno)
        return self.write(json.dumps(res))

    def params_check(self,data,check_params):
        out = False
        if not check_params or not data:
            return out
        for item in check_params:
            if not data.has_key(item):
                return out
        return True
