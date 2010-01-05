import os

class Plugins():
    def __init__(self):
        print "Loading Plugins Plugin."

    def installed(self,config,args):
        plugins = os.listdir(config['corky_path'] + "/plugins")

        installed = []

        for plugin in plugins:
            if plugin.endswith(".py"):
                plugin = plugin.replace(".py","")
                installed.append(plugin)
                  
        return installed                    
