import re
import string

class SysInfo():
    def __init__(self):
    	print "Loading SysInfo Plugin."

    def load(self):
        load = open("/proc/loadavg","rb").read()
        load = string.split(load,' ')
        return { 'one' : load[0], 'five' : load[1], 'fifteen' : load[2] }
