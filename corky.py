import string,cgi,time,sys,imp
import os
import json

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from daemon import Daemon

config = {}

class BasicWeb(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print format % args
        # Should we log to a file?

    def do_GET(self):
        ## Check auth
        allowed = False
        if config.has_key('auth'):
            auth = config['auth']
            if auth.has_key('ip'):
                for ip in auth['ip']:
                    if ip == self.client_address[0]:
                        allowed = True
            else:
                pass
        else:
            allowed = True
                    
        if allowed == False:
            self.send_error(403,'')
            return
        try:
            if self.path.endswith(".html"):
                if os.path.isfile("static" + self.path):
                    f = open("static" + self.path)
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                elif self.path == "/info.html":
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                    self.wfile.write(self.client_address)
                else:
                    self.send_error(404,'File not found')
                return
            else:
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                
                parts = string.split(self.path,"/")
                
                valid_plugins = config['valid_plugins']

                if valid_plugins.has_key(parts[1]):
                    try:
                        func = getattr(valid_plugins[parts[1]], parts[2])
                        result = func(config)
                        if result is not None:
                            self.wfile.write(json.dumps(result))
                    except AttributeError:
                        self.wfile.write("{ 'error' : 'function %s does not have method %s' }" % (parts[1],parts[2]))
                else:
                    self.wfile.write("{ 'error': 'function %s not found'}" % parts[1])

                return
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

def import_module(path,name,unique_name, globals=None, locals=None, fromlist=None):
    try:
        return sys.modules[unique_name]
    except KeyError:
        pass

    sys.path.append(path)
    fp, pathname, description = imp.find_module(name)
    sys.path.pop(-1)

    try:
        return imp.load_module(unique_name,fp, pathname, description)
    finally:
        if fp:
            fp.close()

def main():
    try:
        port = 8000
        if config.has_key('port'):
            port = int(config['port'])

        server = HTTPServer(('', port), BasicWeb)
        print 'started httpserver...'

        ## Load plugins
        plugins = os.listdir(config['corky_path'] + "/plugins")
        valid_plugins = {}

        for plugin in plugins:
            if plugin.endswith(".py"):
                try:
                    plugin = plugin.replace(".py","")
                    exec "from %s import %s" % (plugin,plugin)
                    exec "lp = %s()" % plugin
                    valid_plugins[plugin.lower()] = lp
                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    raise

        config['valid_plugins'] = valid_plugins
    	
        server.serve_forever()	
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

class SDaemon(Daemon):
    def run(self):
        main()

	
if __name__ == '__main__':
    corky_path = os.path.dirname(os.path.dirname( os.path.realpath( __file__ )) + "/")
    sys.path.append(corky_path + "/plugins")

    ## Read config
    cconfig = open(corky_path + "/config.json","rb").read()
    if cconfig is not None:
        config = json.loads(cconfig)

    config['corky_path'] = corky_path;

    log = '/var/log/corky.log'
    if config.has_key('log'):
        log = config['log']

    if not os.path.exists(log): 
        open(log,'w').close()

    daemon = SDaemon('/tmp/daemon-example.pid',log,log,log)
    if len(sys.argv) == 2:
        if 'debug' == sys.argv[1]:
            main()
        elif 'start' == sys.argv[1]:
			daemon.start()
        elif 'stop' == sys.argv[1]:
 			daemon.stop()
        elif 'restart' == sys.argv[1]:
			daemon.restart()
        else:
			print "Unknown command"
 			sys.exit(2)
        sys.exit(0)
    else:
		print "usage: %s start|stop|restart" % sys.argv[0]
 		sys.exit(2)

