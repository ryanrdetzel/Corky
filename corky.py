#!/usr/bin/python

import string,cgi,time,sys,imp
import os
import json

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from daemon import Daemon

valid_plugins = {}

class BasicWeb(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print format % args
        # Should we log to a file?

    def do_GET(self):
        try:
            if self.path.endswith(".html"):
                if os.path.isfile("static" + self.path):
                    f = open("static" + self.path)
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                else:
                    self.send_error(404,'File not found')
                return
            else:
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                
                parts = string.split(self.path,"/")

                if valid_plugins.has_key(parts[1]):
                    try:
                        func = getattr(valid_plugins[parts[1]], parts[2])
                        result = func()
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
        server = HTTPServer(('', 8000), BasicWeb)
        print 'started httpserver...'

        ## Load plugins
        plugins = os.listdir(os.path.realpath(os.path.dirname(sys.argv[0])) + "/plugins")
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
    	
        server.serve_forever()	
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

class SDaemon(Daemon):
    def run(self):
        main()

	
if __name__ == '__main__':
    sys.path.append(os.path.realpath(os.path.dirname(sys.argv[0])) + "/plugins")

    daemon = SDaemon('/tmp/daemon-example.pid','/tmp/log','/tmp/log', '/tmp/log')
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

