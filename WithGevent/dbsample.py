#-*- coding:utf-8 -*-
import os
import imp
import sys
import time
import json
import logging
import traceback
import urllib
import urllib2
import httplib
import gevent
import gevent.monkey
gevent.monkey.patch_socket()
from gevent.queue import Queue

from common import core

reload(sys)
sys.setdefaultencoding('utf8')
FastpyAutoUpdate = True





class dbsample():
    def __init__(self):
        # init here
        self.mysqlPool = core.MysqlPool(pool_size=2,host='10.66.126.57',port=3306,user='root',passwd='gcloud@2015',db='gcloud',charset='utf8')
        pass

    def test_mysql_pool(self, request, response_head):
        cursor = self.mysqlPool.get()

        sql = "select * from t_dir_platform_list limit 5"
        cursor.execute(sql)
        rows = cursor.fetchall()


        self.mysqlPool.put(cursor)
        res = json.dumps(rows, ensure_ascii=False).encode('utf8')

        return res

