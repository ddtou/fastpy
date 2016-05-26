import traceback
import sys
import re

def getTraceStackMsg():
    tb = sys.exc_info()[2]
    msg = ''
    for i in traceback.format_tb(tb):
        msg += i
    return msg

class Singleton(object):  
    def __new__(cls, *args, **kw):  
        if not hasattr(cls, '_instance'):  
            orig = super(Singleton, cls)  
            try:
                 cls._instance = orig.__new__(cls, *args, **kw)  
            except Exception,e:
                 pass
            try:
                 cls._instance = orig.__new__(cls)  
            except Exception,e:
                 pass
            method_name = "__single_init__"
            try:
                method = getattr(cls._instance, method_name)
            except Exception,e:
                print "metho %s not found" % method_name
            try:
                method(*args, **kw)
            except Exception,e:
                try:
                    method()
                except Exception,e:
                    print "method %s call fail" % method_name
                    print str(e) + getTraceStackMsg()
        return cls._instance
try:
    import gevent
    import gevent.monkey
    gevent.monkey.patch_socket()
    from gevent.queue import Queue
except Exception,e:
    print "not install gevent"
        
try:
    import pymysql
    class MysqlPool(Singleton):
        def __single_init__(self,pool_size=10,host='localhost',port=3306,user='root',passwd='123',db='ere',charset='utf8'):
            self.con_que=Queue()
            self.cur_que=Queue()
            try:
                for i in range(pool_size):
                    conn=pymysql.connect(host=host,port=port,user=user,passwd=passwd,db=db,charset=charset)
                    self.con_que.put(conn)
                    cursor = conn.cursor(pymysql.cursors.DictCursor)
                    cursor.execute("set names '%s'" % charset)
                    self.cur_que.put(conn.cursor(pymysql.cursors.DictCursor))
                print "inti mysql pool suc"
            except Exception,e:
                print str(e) + getTraceStackMsg()
    
        def empty(self):
            return self.cur_que.empty()
    
        def get(self):
            return self.cur_que.get()
    
        def put(self, obj):
            self.cur_que.put(obj)
except Exception,e:
    print "not install pymysql"

class FeimaTpl():
    def __init__(self,filepath=None,content=None):
        if filepath != None:
            content = open(filepath, "r").read() 
        if content == None:
            raise Exception("template content can not be null")
        indent_count = 0
        self.py_code = "__html_code__ = ''"
        self.param_dic = {}
        text_list = content.split("<%")
        for text in text_list:
            right = text.find("%>")
            if right == -1:
                self.py_code += "\n%s__html_code__ += '''%s'''" % (indent_count*"\t",text)
                continue
            elif text[0] == '=':
                self.py_code += "\n%s__html_code__ += str(%s)" % (indent_count*"\t",text[1:right])
            else: #change {} to py mode
                replace_reg = re.compile(r'\s*{\s*')
                py_text = replace_reg.sub("{", text[0:right].replace("\r","").replace("\n", "").strip())
                self.py_code += "\n"+indent_count*"\t"
                for sub in py_text:
                    if sub == '}':
                        self.py_code += '\n'
                        indent_count -= 1
                    elif sub == '{':
                        indent_count += 1
                        self.py_code += ":\n"+indent_count*"\t"
                    else:
                        self.py_code += sub
            self.py_code += "\n%s__html_code__ += '''%s'''\n" % (indent_count*"\t",text[right+2:])
    def assign(self, key, value):
        self.param_dic[key] = value
    def render(self):
        try:
            for k,v in self.param_dic.items():
                exec("%s=v" % k)
            exec(self.py_code)
            return __html_code__
        except Exception, e:
            return str(e)+getTraceStackMsg()

#use example
#import core
#tpl = core.FeimaTpl(filepath="./a.html")
#d = []
#d.append({"id":1,"name":"name1","array":[2,4,5,6]})
#d.append({"id":2,"name":"name2","array":[1,3,5,7,9]})
#
#tpl.assign("title", "my title")
#tpl.assign("data", d)
#
#print tpl.render()



