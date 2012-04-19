#!/usr/bin/python2
# -*- coding: utf8 -*- 

import os
import cherrypy
import kanji_review
import word_review
from cherrypy.process import servers

class MainApp(object):
	def __init__(self):
		self.kanji_review = kanji_review.KanjiReview()
		self.word_review = word_review.WordReview()

	@cherrypy.expose
	def index(self):
		f = open('root/index.html')
		return f.read()

# determine the port and root path to use
in_heroku = os.environ.get('PORT') != None
port = 8080 if not in_heroku else int( os.environ.get('PORT') )
root = '/app' if in_heroku else '/home/brazzi/Development/cherrypy/jap-test'

# fix for explosion in heroku
def fake_wait_for_occupied_port(host, port): return
servers.wait_for_occupied_port = fake_wait_for_occupied_port

cherrypy.config.update({'server.socket_port': port, 'tools.staticdir.root': root})
cherrypy.quickstart( MainApp(), "/", "cherrypy.config" )

