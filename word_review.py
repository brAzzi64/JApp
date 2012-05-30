#!/usr/bin/python2
# -*- coding: utf8 -*- 

import cherrypy
import gdata.spreadsheet.service
import string
import random
import json
import sys
import re
from datetime import datetime


# Filter Functions to be used by Jinja2
def get_month_name(month_number):
	return datetime(2012, month_number, 1).strftime('%B')

def get_weekday_name(date):
	return date.strftime('%A')

from jinja2 import Environment, FileSystemLoader
# specify the path from where to load the templates
env = Environment(loader=FileSystemLoader('templates'))
env.filters['weekday_name'] = get_weekday_name
env.filters['month_name'] = get_month_name


class WordReview(object):
	def __init__(self):
		print 'Initializing...'	
		self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
		self.spreadsheet_key = '0Ai5r-hNfp2fzdHlJV3B3NWphc3h1cFFOS1UzVXNlRmc'
		self.cells_feed = None
		self.top_row = 2
		self.column_labels = {}
		self.cell_hash = {}
		self.word_hash = {}
		self.date_hash = {}
		
		self.LoadData()
	
	def LoadData(self):
		print 'Loading spreadsheet data...',
		sys.stdout.flush()
		
		# create the cell query
		self.cells_feed = self.gd_client.GetCellsFeed(self.spreadsheet_key, visibility='public', projection='values')
		print 'Done.'
		print 'Creating structures...',
		sys.stdout.flush()
		
		headers = [ 'fecha', 'palabra', "pronunciacion", 'tipo', 'significado', 'jisho' ]
		self.column_labels = dict( (h, chr(ord('A') + i)) for i, h in enumerate(headers) )
		
		# store the information in a more convenient structure
		for e in self.cells_feed.entry:
			# the string is a str object but encoded as utf8,
			# so we decode it and convert it to a unicode object.
			self.cell_hash[e.title.text] = e.content.text.decode('utf8') if e.content.text != None else ''
		
		last_row = int(self.cells_feed.row_count.text)

		# create word dictionary, "word : info"
		for i in range(self.top_row, last_row):
			cell_index = self.column_labels['palabra'] + str(i)
			
			# skip rows with empty word field
			if cell_index not in self.cell_hash.keys():
				continue

			word = self.cell_hash[cell_index]
			info = dict( (h, self.cell_hash[self.column_labels[h] + str(i)]) for h in self.column_labels.keys() )
			
			# add additional fields
			info['uwuka'] = False if info['tipo'].find('UWUKA') == -1 else True
			
			self.word_hash[word] = info

			# index it in the date_hash
			fecha = info['fecha'].split(' ')[0] # the date sometimes arrives as 'DATE HOUR', so we discard the hour
			fecha = datetime.strptime(fecha, '%m/%d/%Y') # .strftime("%Y/%m/%d")
			if not fecha in self.date_hash.keys():
				self.date_hash[fecha] = []
			self.date_hash[fecha].append(word)

			# we don't need id in the info dic
			del info['fecha']
	
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
	def random_row(self, date = None):
		cherrypy.response.headers['Content-Type'] = "application/json"

		if date != None:
			# convert string date into datetime obj
			date = datetime.strptime(date, '%Y/%m/%d')
			if date in self.date_hash.keys():
				index = random.randint(0, len(self.date_hash[date]) - 1)
				info = dict( self.word_hash[self.date_hash[date][index]] ) # we're creating a copy, let's try not to, later
			else:
				date = None
		
		if date == None:
			index = random.randint(0, len(self.word_hash.keys()) - 1)
			info = dict( self.word_hash[self.word_hash.keys()[index]] ) # we're creating a copy, let's try not to, later
		
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

	def get_dates(self):
		sorted_dates = list( self.date_hash.keys() )
		sorted_dates.sort()
		ordered_dates = list( { 'date' : date, 'word_count' : len( self.date_hash[date] ) } for date in sorted_dates )
		
		result = {}
		current_year = None
		current_month = None
		current_year_col = None
		current_month_col = None
		for date_info in ordered_dates:
			date = date_info['date']
			word_count = date_info['word_count']

			if date.year != current_year:
				current_year_col = {}
				result[date.year] = current_year_col
				current_year = date.year

			if date.month != current_month:
				current_month_col = []
				result[current_year][date.month] = current_month_col
				current_month = date.month

			current_month_col.append( {'day' : date.day, 'word_count' : word_count, 'full_date' : date} )
					
		return result

	@cherrypy.expose
	def reload(self):
		self.__init__()
		return "Done"
			
	@cherrypy.expose
	def main(self):
		tmpl = env.get_template('word_review.html')
		ordered_dates = self.get_dates()
		return tmpl.render(dates = ordered_dates)
			
