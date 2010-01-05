import re
import string
import subprocess
import commands

class ProcessWatch():
    def __init__(self):
        print "Loading ProcessWatch Plugin."

    def __process_num(self,process):
        return commands.getoutput('pidof %s |wc -w' % process)

    def running(self,config,args):
        output = 0
        if args.has_key('process'):
            output = self.__process_num(str(args['process'][0]))

        return "{ 'running': %d }" % int(output)
