#!/usr/bin/python2
# -*- coding: utf8 -*- 

import cherrypy
import gdata.spreadsheet.service
import string
import random
import json
import sys
import re

class WordReview(object):
	def __init__(self):
		print 'Initializing...'	
		self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
		self.spreadsheet_key = '0Ai5r-hNfp2fzdHlJV3B3NWphc3h1cFFOS1UzVXNlRmc'
		self.cells_feed = None
		self.top_row = 2
		self.bottom_row = 241
		self.column_labels = {}
		self.cell_hash = {}
		self.word_hash = {}
		
		self.LoadData()
	
	def LoadData(self):
		print 'Loading spreadsheet data...',
		sys.stdout.flush()
		
		# create the cell query
		query = gdata.spreadsheet.service.CellQuery()
		query.range = 'B%d:F%d' % (self.top_row, self.bottom_row)
		self.cells_feed = self.gd_client.GetCellsFeed(self.spreadsheet_key, visibility='public', projection='values', query=query)
		print 'Done.'
		print 'Creating structures...',
		sys.stdout.flush()
		
		headers = [ 'palabra', "pronunciacion", 'tipo', 'significado', 'jisho' ]
		self.column_labels = dict( (h, chr(ord('B') + i)) for i, h in enumerate(headers) )
		
		# store the information in a more convenient structure
		for e in self.cells_feed.entry:
			# the string is a str object but encoded as utf8,
			# so we decode it and convert it to an unicode object.
			self.cell_hash[e.title.text] = e.content.text.decode('utf8') if e.content.text != None else ''
		
		# create word dictionary, "word : info"
		for i in range(self.top_row, self.bottom_row):
			word = self.cell_hash[self.column_labels['palabra'] + str(i)]
			info = dict( (h, self.cell_hash[self.column_labels[h] + str(i)]) for h in self.column_labels.keys() )
			
			# add additional fields
			info['uwuka'] = False if info['tipo'].find('UWUKA') == -1 else True
			
			self.word_hash[word] = info
		
		# create kanji dictionary, "kanji : words"
		self.kanji_dict = {}
		for word in self.word_hash.keys():
			for char in word:
				# check if it's in the range of the basic
				# block of CJK Unified Ideographs (0x4E00 - 0x9FFF)
				if self.is_kanji(char):
					if not char in self.kanji_dict.keys():
						self.kanji_dict[char] = []
					self.kanji_dict[char].append(word)
					
		# add kanji_maps to the info structs, now that the kanji dictionary is built
		for word in self.word_hash.keys():
			info = self.word_hash[word]
			info['kanji_map'] = self.build_kanji_map(word)
			info['kanji_pronunciations'] = self.build_kanji_pronunciation_map(word, info['pronunciacion'])
			info['pronunciacion'] = info['pronunciacion'].replace(' ', '') # delete spaces in pronunciation
		
		print 'Done.'
				
	def build_kanji_map(self, word):
		kanji_map = {}
		for kanji in (char for char in word if self.is_kanji(char)):
			if kanji in self.kanji_dict.keys():
				kanji_map[kanji] = list(self.kanji_dict[kanji])
				kanji_map[kanji].remove(word)
		return kanji_map
		
	def build_kanji_pronunciation_map(self, word, pronunciation):
		pronunciation_map = {}
		kanji_list = list(x for x in word if self.is_kanji(x))
		
		if len(kanji_list) != 0:
			# build regular expression
			replace = lambda x: '([^ ]*)' if self.is_kanji(x) else x
			regexp_str = "".join(replace(i) for i in word)
			regexp_str = regexp_str.replace(")(", ") (")
			
			# match pronunciation against it		
			match = re.match(regexp_str, pronunciation)
			if match != None:
				for i, kanji in enumerate(kanji_list):
					pronunciation_map[kanji] = match.group(i + 1) # groups start in 1
					if pronunciation_map[kanji] == None:
						return {} # no resoluble sin implentar pipes |		
			else:
				#print "Error: word '%s' doesn't match pronunciation '%s' with '%s'" % (word, pronunciation, regexp_str)
				pass
		return pronunciation_map
	
	def is_kanji(self, char):
		return ord(char) > 0x4E00 and ord(char) < 0x9FFF
	
	@cherrypy.expose
	def random_row(self):
		cherrypy.response.headers['Content-Type'] = "application/json"
		
		index = random.randint(0, len(self.word_hash.keys()) - 1)
		info = self.word_hash[self.word_hash.keys()[index]]
		
		return json.dumps(info)
		
	@cherrypy.expose	
	def load_word(self, word = None):
		if word == None:
			return "Error: parameter [word] not specified."
		if not word in self.word_hash.keys():
			return "Error: word '%s' not found." % word
			
		cherrypy.response.headers['Content-Type'] = "application/json"
				
		info = self.word_hash[word]
		
		return json.dumps(info)

