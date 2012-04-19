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


# fix for explosion in heroku
def fake_wait_for_occupied_port(host, port): return
servers.wait_for_occupied_port = fake_wait_for_occupied_port

cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', '8080'))})
cherrypy.quickstart( MainApp(), "/", "cherrypy.config" )

