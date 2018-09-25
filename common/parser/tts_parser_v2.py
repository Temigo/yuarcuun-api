#!/usr/bin/python
# -*- coding:utf-8 -*-
# Author: cwtliu

# This function converts a word into its pronunciation syllables, including stress and gemination cases.

import argparse
from letters import *

def process_enclitics(word):
	"""
	Input: Word with dash and enclitic - only handles enclitics, not i-ii or a-ang
	Output: Concatenated word with enclitic and removal of dash
	"""
	items = word.split('-')
	if len(items) > 2:
		raise ValueError('not yet able to process more than one dash')
	if items[1] == '2u':
		word = items[0]+'2u'
	elif items[1] == 'qaa':
		word = items[0]+'qaa'
	else:
		raise ValueError('not yet on list of available enclitics')
	return(word)

def process_apostrophe_voicelessness(word):
	"""
	Input: apostrophe processing for c'v and c'c, but not v'c or v'v
	Output: 

	Extra notes: For now an example like atu'rtuq is not geminated at t so at first becomes a|tuurr|tuq, have to confirm if it would actually be at|tuurr|tuq, / means it will be removed by the end
	"""
	if word[0] == "'": #handle apostrophe at start and end of word
		return word.replace("'", "")
	if word[-1] == "'":
		return word.replace("'", "")
	if "'" in word:
		word = list(word)
		for i, letter in enumerate(word[:-1]):
			if letter == "'": #trying to seperate n and g from becoming ng
				if word[i-1]=='n' and word[i+1]=='g':
					word[i]='@' #@ will be removed later
				elif word[i-1] in c and word[i+1] in v: #just set the apostrophe to be the geminated consonant 
					word[i]=word[i-1]
		word = ''.join(word)
		word = word.replace("@","")
	word = automatic_devoicing(word)
	return(word)

def automatic_devoicing(word):
	word = list(word)
	if word[0] == 's':
		word[0]=voiced_converter['s']
	if word[-1] in voiced_fricatives:
		word[-1]=voiced_converter[word[-1]] #if end word is a voiced fricative, switch to voiceless
	for i, letter in enumerate(word[:-1]):
		if word[i] in voiced_fricatives and word[i+1] in stops: #voiced next to stop
			word[i]=voiced_converter[word[i]]
		elif word[i] in stops and word[i+1] in voiced_fricatives: #voiceless preceded by voiced
			word[i+1]=voiced_converter[word[i+1]]
		elif word[i] in voiceless_fricatives and word[i+1] in voiced_fricatives: #voiced preceded by voiceless
			word[i+1]=voiced_converter[word[i+1]]
		elif (word[i] in voiceless_fricatives or word[i] in stops) and word[i+1] in voiced_nasals: #nasal preceded by stop or voiceless
			word[i+1]=voiced_converter[word[i+1]]
	return(''.join(word))


def chunk_syllables(geminated_wordform):
	"""
	Input: list form with additional letters added for gemination case  (ex. ['t', 'u', 'm', 'E', 'm', 'm', 'i'])
	Output: preliminary syllable list form (ex. [['t', 'u'], ['m', 'E', 'm'], ['m', 'i']])

	This function starts from the end of a word and iterates backward forming syllables along the way. Can account for apostrophes.
	"""
	geminated_wordform = geminated_wordform[::-1] #process in reverse
	word_length = len(geminated_wordform)
	syllable_wordform = []
	last_index = 0
	skip = False
	containsapostrophe = False
	for i, letter in enumerate(geminated_wordform):
		if skip == True:
			skip = False
		elif word_length-i == 1: # if last character
			syllable_wordform.append(geminated_wordform[last_index:i+1][::-1])
		elif geminated_wordform[i] == "'":
			syllable_wordform.append("'")
			last_index = i+1
			containsapostrophe = True
		elif geminated_wordform[i+1] in c:
			syllable_wordform.append(geminated_wordform[last_index:i+2][::-1])
			skip = True
			last_index = i+2
		elif geminated_wordform[i+1] == "'":
			syllable_wordform.append(geminated_wordform[last_index:i+1][::-1])
			syllable_wordform.append("'")
			skip = True
			last_index = i+2
			containsapostrophe = True
		#If none of these are satisfied then it passes a vowel
	syllable_wordform = syllable_wordform[::-1]
	if containsapostrophe:
		shiftapostrophe = []
		doubleskip = False
		skip = False
		for i, chunk in enumerate(syllable_wordform):
			if doubleskip:
				skip = True
				doubleskip = False
			elif skip:
				skip = False
			elif len(syllable_wordform) == i+1 or len(syllable_wordform) == i:
				shiftapostrophe.append(chunk)
			elif syllable_wordform[i+1] == "'":
				if syllable_wordform[i][-1] in v or syllable_wordform[i+2][0] in v: #handle the v'v and the v'c modes by retaining the @
					shiftapostrophe.append(syllable_wordform[i]+syllable_wordform[i+2]+'@')
				else:
					shiftapostrophe.append(syllable_wordform[i])
					shiftapostrophe.append(syllable_wordform[i+2])
				doubleskip = True
			else:
				shiftapostrophe.append(chunk)
		syllable_wordform = shiftapostrophe
	return(syllable_wordform)

def automatic_gemination(word_list,stress_list):
	for i, chunk in enumerate(word_list[:-1]):
		if '@' in word_list[i]: # if the u'v case, add an extra vowel in place of apostrophe
			if len(word_list[i]) == 4:
				word_list[i] = word_list[i][0]+word_list[i][1]+word_list[i][1]+word_list[i][2]
				stress_list[i] = True
			else:
				word_list[i] = word_list[i].replace('@','') #u'u case so just remove the apostrophe and process normally
		if stress_list[i] == False and not isClosed(word_list[i]) and not isHeavy(word_list[i]) and isHeavy(word_list[i+1]) and '@' not in word_list[i+1]: #automatic gemination
			word_list[i] = word_list[i]+word_list[i+1][0]
			stress_list[i] = True
		if stress_list[i] == True and word_list[i][-1] == 'e' and '@' not in word_list[i+1]: #tumemi
			word_list[i] = word_list[i]+word_list[i+1][0]
	return(word_list, stress_list)

def assign_stress(word_list):
	stress_list = [False] * len(word_list)
	stress_repelling_base = False
	skipped = False
	for i, chunk in enumerate(word_list):
		if i == 0 and not stress_repelling_base and isClosed(chunk):
			stress_list[i]=True
		elif isHeavy(chunk):
			stress_list[i]=True
	if len(stress_list) > 1:
		stress_list[-1] = False
	for i, chunk in enumerate(word_list[:-1]):
		if stress_list[i] == True:
			skipped = False
		elif stress_list[i] == False and skipped:
			stress_list[i]=True
			skipped = False
		else:
			if stress_list[i+1]==False and isClosed(word_list[i]) and not isClosed(word_list[i+1]):
			 	stress_list[i]=True
			else:
				skipped = True
 	word_list, stress_list = automatic_gemination(word_list,stress_list)
 	for i, chunk in enumerate(word_list[:-1]): #secondary stress
		if i != 0 and stress_list[i] == False and isHeavy(word_list[i+1]):
			stress_list[i] = True
	if word_list:
		if word_list[0] == 'e':
			if word_list[1][0] in c and word_list[1][1] in prime_v:
				word_list = word_list[1:]
				stress_list = stress_list[1:]
	#print(stress_list)
	for i, chunk in enumerate(word_list):
		if stress_list[i]:
			word_list[i]=word_list[i]+'$'
	if word_list:
	 	word_list[-1] = word_list[-1]+'%'
 	return(word_list)

def parser(word):
	single_word = convert(word)
	if "-" in single_word:
		single_word = single_word.split('-')[0]
		print('Not setup to process hyphen cases yet, returned word only')
		#single_word = process_enclitics(single_word)
	word_list = process_apostrophe_voicelessness(single_word)
	print(word_list)
	word_list = chunk_syllables(word_list)
	print(word_list)
	word_list = assign_stress(word_list)
	print(word_list)
	return(word_list)		

if __name__ == "__main__":
	s = argparse.ArgumentParser(description='parse a given word into separate units.')
	s.add_argument('file', help='yup\'ik string to be parsed')
	args = s.parse_args()
	print(parser(args.file))
