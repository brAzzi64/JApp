#!/usr/bin/python2
# -*- coding: utf8 -*- 

import cherrypy
import kanji_review
import word_review

class MainApp(object):
	def __init__(self):
		self.kanji_review = kanji_review.KanjiReview()
		self.word_review = word_review.WordReview()

	@cherrypy.expose
	def index(self):
		f = open('root/index.html')
		return f.read()

				
cherrypy.quickstart( MainApp(), "/", "cherrypy.config" )
