#!/usr/bin/env python
#-*-coding:utf-8-*-

#Version:1.0.0
#Author: Jiwei.Zhang <jiwei.zjw@alibaba-inc.com>
#License:Copyright(c) 2016 Jiwei.Zhang


class ErrorCtrl(object):
    """docstring for ErrorCtrl"""
    
    @classmethod
    def get_error(cls,error_num):

        res = {
            'errno' : error_num
        }
        return res
