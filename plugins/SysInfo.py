import re
import string


class SysInfo():
    def __init__(self):
    	print "Loading SysInfo Plugin."

    def sysload(self,config):
        load = open("/proc/loadavg","rb").read()
        load = string.split(load,' ')
        return { 'one' : load[0], 'five' : load[1], 'fifteen' : load[2] }

    def memory(self,config):
        mem_info = {}
        memory = open("/proc/meminfo","rb").read()
        memory = string.split(memory,"\n")
        for val in memory:
            m = re.search('^(\w+):\s+(\d+)\s',val)
            if m is not None:
                mem_info[m.group(1)] = int(m.group(2))

        mem_total = mem_info['MemTotal'] / 1024
        mem_free = (mem_info['MemFree'] + mem_info['Buffers'] + mem_info['Cached']) / 1024
        mem_used = mem_total - mem_free
        mem_percent_used = "%.2f" % (mem_used / float(mem_total) * 100)

        return { 'total' : mem_total, 'free' : mem_free, 'used' : mem_used, 'used_percent' : mem_percent_used }
