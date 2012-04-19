#!/usr/bin/python2
# -*- coding: utf8 -*- 

import cherrypy
import os

class MainApp(object):
    def __init__(self):
        pass

    @cherrypy.expose
    def index(self):
        return 'Hello World'

    @cherrypy.expose
    def method1(self):
        if not "value" in cherrypy.session:
            cherrypy.session["value"] = 'Hay Sesión'
        return 'method 1 - hola!'
    
    @cherrypy.expose
    def method2(self):
        value = None
        if "value" in cherrypy.session:
            value = cherrypy.session["value"]
        return 'method 2 - random_value = ' + str(value)
 

# determine the port and root path to use
in_heroku = os.environ.get('PORT') != None
port = 8080 if not in_heroku else int( os.environ.get('PORT') )
root = '/app' if in_heroku else '/home/brazzi/Development/cherrypy/jap-test'

cherrypy.config.update({'server.socket_port': port, 'tools.staticdir.root': root})
cherrypy.quickstart( MainApp(), "/", "cherrypy.config" )

