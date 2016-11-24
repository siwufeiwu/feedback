#!/usr/bin/env python
#-*-coding:utf-8-*-

#Version:1.0.0
#Author: Jiwei.Zhang <jiwei.zjw@alibaba-inc.com>
#License:Copyright(c) 2016 Jiwei.Zhang

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
from tornado.options import define, options
from tornado.escape import json_encode, json_decode
import torndb
import handler
import os
import logging
from lib.ConfigCtrl import ConfigCtrl
from handler.BaseHandler import BaseHandler
from handler.IndexHandler import IndexHandler

# define("port", default=8000, type=int, help='run on the given port')

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s %(name)s %(levelname)s %(filename)s %(funcName)s %(lineno)d %(message)s',
#                     datefmt='%m-%d %H:%M:%S',
#                     filename='./log/app.log',
#                     filemode='a')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', IndexHandler),
        ]
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "template"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies = False,
            cookie_secret = ""
        )

        tornado.web.Application.__init__(self, handlers, **settings)

        self.cfg = ConfigCtrl()
        self.db = torndb.Connection(
            host = self.cfg.get_config('mysql', 'mysql_host') + ':' + self.cfg.get_config('mysql', 'mysql_port'),
            user = self.cfg.get_config('mysql', 'mysql_user'),
            database = self.cfg.get_config('mysql', 'mysql_database'),
            password = self.cfg.get_config('mysql', 'mysql_password')
        )

if __name__ == '__main__':
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    # tornado.options.parse_command_line()
    # http_server.listen(options.port)
    http_server.listen(9000)
    tornado.ioloop.IOLoop.instance().start()
