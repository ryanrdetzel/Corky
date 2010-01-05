import os
import json

class FileCount():
    ''' This plugin shows how to use local config files for plugins'''
    def __init__(self):
        print "Loading FileCount Plugin."

    def count(self,config,args):
        ''' Count the number of files in the directory listed in the config file'''

        local_config = open(config['corky_path'] + "/plugins/FileCount.json" ,"rb").read()
        local_config = json.loads(local_config)

        dir = '/tmp'
        if local_config.has_key('dir'):
            dir = local_config['dir']

        files = len(os.listdir(dir))
        
        return files
