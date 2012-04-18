#!/usr/bin/python2
# -*- coding: utf8 -*- 

import cherrypy
import random
import json

class KanjiReview(object):
	def __init__(self):
		self.kanjis = {}
		f = open('RememberingTheKanji-SortedList.txt')
		f.read(3) # discard 3 first characters
		for line in f:
			line = line.split('\t')
			number = int(line[0])
			kanji = line[1]
			meaning = line[2].rstrip()
			if meaning != '':
				self.kanjis[number] = ( kanji, meaning )
		self.max_key = max (self.kanjis.keys() )
	
	@cherrypy.expose
	def random_kanji(self, min_index = -1, max_index = 99999):
		# parse arguments
		try:
			min_index = int(min_index)
			max_index = int(max_index)
		except ValueError:
			return "Error: invalid value in parameters 'min_index' and 'max_index'."

		cherrypy.response.headers['Content-Type'] = "application/json"

		min_index = max(min_index, 1)
		max_index = min(max_index, self.max_key)
		key = -1
		# since not all key values may be present:
		while True:
			key = random.randint(min_index, max_index)
			if key in self.kanjis.keys():
				break
		# return the info
		info = {'index' : key, 'kanji' : self.kanjis[key][0], 'meaning' : self.kanjis[key][1]}
		return json.dumps(info)

