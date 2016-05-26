#-*- coding:utf-8 -*-
import os
import imp
import sys
import time
#from Cheetah.Template import Template
import json
#import redis
import logging
import traceback
import urllib
import urllib2
import httplib
import gevent
import gevent.monkey
gevent.monkey.patch_socket()
from gevent.queue import Queue
#from common import base

reload(sys)
sys.setdefaultencoding('utf8')
FastpyAutoUpdate = True

#rlog = base.FeimatLog("logs/sample.log")

def fetch(pid, url, request):
    print('Process %s: %s start work' % (pid, url))
    flag = None
    status = None
    error_msg = None

    conn = httplib.HTTPConnection("127.0.0.1:8998")
    headers = {
    }

    body_str = ""
    print('start post %s: %s start work' % (pid, url))
    conn.request("POST", "/sample.test_alive", body_str, headers)

    res = conn.getresponse()
    print('response %s: %s start work' % (pid, url))
    conn.close()

    data = res.read()

    print('finish %s: %s %s' % (pid, url, res.status))
    return "suc"

class ResPool():
    def __init__(self):
        self.que=Queue() #资源池 数据库连接池可参考这样使用
        for i in range(0,2):
            self.que.put(i)

    def empty(self):
        return self.que.empty()

    def get(self):
        return self.que.get()

    def put(self, obj):
        self.que.put(obj)


class sample():
    def __init__(self):
        # init here
        #self.up_t = Template(file="templates/upload.html")
        self.content = 1
        self.id = 1
        self.resPool = ResPool()
        pass

    def test_alive(self, request, response_head):
        #response_head["Connection"] = "close"
        return "aaa"
        res = ""
        for i in range(1, 10):
            res += str(self.content)
        self.content += 1
        return res

    def web(self, request, response_head):
        url = 'http://127.0.0.1:8998/sample.test_alive'
        self.id += 1
        return fetch(self.id, url, request)

    def test_yield(self, request, response_head):
        self.id += 1
        id = self.id
        is_yield = False
        if self.resPool.empty():
            print "yield",id
            is_yield = True
        i = self.resPool.get()
        if is_yield:
            print "resume",id # 走到这一步说明之前放权了但现在又被唤醒了
        url = 'http://127.0.0.1:8998/sample.test_alive'
        fetch(id, url, request)
        self.resPool.put(i)
        print "finish",id
        return "suc"

    def test_print_chunk(self, request, response_head):
        for i in range(0, 4):
            request.printChunk("print %s <br\>" % i)
            gevent.sleep(1)
        request.printChunk("aaaa")
        request.printChunk("")
        gevent.sleep(1)
        request.flushChunk()

