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
		self.current_min_index = None
		self.current_max_index = None
		self.index_set = []
	
	@cherrypy.expose
	def random_kanji(self, amount = 1, min_index = -1, max_index = 99999):
		# parse arguments
		try:
			min_index = int(min_index)
			max_index = int(max_index)
			amount = int(amount)
		except ValueError:
			return "Error: invalid value in parameters 'amount', 'min_index' and/or 'max_index'."

		cherrypy.response.headers['Content-Type'] = "application/json"

		# sanitize parameters
		min_index = max(min_index, 1)
		max_index = min(max_index, self.max_key)
		amount = max(1, amount)

		pack = []
		for i in range(0, amount):
			info = self.get_random_kanji(min_index, max_index)
			pack.append(info)

		return json.dumps(pack)

	def get_random_kanji(self, min_index, max_index):
		kanji = 'NO KANJI'
		meaning = 'invalid data'
		
		if min_index != self.current_min_index or max_index != self.current_max_index:
			self.current_min_index = min_index
			self.current_max_index = max_index
			self.index_set = []

		if self.index_set == []:
			self.index_set = self.create_random_index_set()
		
		key = self.index_set.pop()
		if key in self.kanjis.keys():
			kanji = self.kanjis[key][0]
			meaning = self.kanjis[key][1]
		
		return {'index' : key, 'kanji' : kanji, 'meaning' : meaning}

	def create_random_index_set(self):
		base_set = [k for k in range(self.current_min_index, self.current_max_index + 1)]
		random_set = []
		while len(base_set) != 0:
			rand = random.randint(0, len(base_set) - 1)
			random_set.append(base_set.pop(rand))
		return random_set

