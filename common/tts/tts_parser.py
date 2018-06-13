#!/usr/bin/python
# -*- coding:utf-8 -*-
# Author: cwtliu

# This function converts a word into its pronunciation syllables, including stress and gemination cases.

import argparse
from letters import *

def process_enclitics(word):
	"""
	Not yet able to process enclitics
	"""
	word = word.split('-')
	#print(word)
	return(''.join(word[0]))


def assign_stressed_vowels(single_word):
	"""
	Input: converted string of full word (ex. 'aya2ruuk')
	Output: list form with stressed vowels in upper case (ex. ['a','y','A','2','r','u','u','k'])

	The rules for determining stress were followed according to Ch. 1 appendix of "A Practical Grammar of the Alaskan Central Yup'ik Eskimo Language"
	"""

	if "'" in single_word: # more complex case of words containing apostrophes like apa'urluq this one should accent a without moving it
		single_word = list(single_word)
		vowel_count = 0
		letter_count = 0
		last_vowel_index = 0
		first_vowel = True
		stress_next_vowel = False
		word_length = len(single_word)
		for i, letter in enumerate(single_word):
			if letter in v:
				if first_vowel: #rhythmic stress rule 1
					if word_length-i > 2 and single_word[i+1] in c and (single_word[i+2] in c or single_word[i+2] == "'"):
						single_word[i] = letter.upper()
						stress_next_vowel = False
					elif (word_length-i > 3 and single_word[i+1] in c and single_word[i+2] in v and single_word[i+3] in v) or (word_length-i > 3 and single_word[i+1] in c and single_word[i+2] == "'" and single_word[i+3] in v): # geminated
						single_word[i] = single_word[i].upper()
						stress_next_vowel = False
					else:
						stress_next_vowel = True
					first_vowel = False
				elif stress_next_vowel == True and word_length-i > 1 and single_word[i+1] in v: #rhythmic stress rule 2
					single_word[last_vowel_index] = single_word[last_vowel_index].upper()
				elif stress_next_vowel == True and i > 2 and word_length-i > 2 and single_word[i-3] in v and single_word[i-2] in c and single_word[i-1] in c and single_word[i+1] in c and single_word[i+2] in v: #rhythmic stress rule 3
					single_word[last_vowel_index] = single_word[last_vowel_index].upper()
				elif stress_next_vowel == True:
					single_word[i] = single_word[i].upper()
					stress_next_vowel = False
				else:
					stress_next_vowel = True
				last_vowel_index = i
		single_word[last_vowel_index] = single_word[last_vowel_index].lower() #removes stress from last vowel
	else:
		single_word = list(single_word)
		vowel_count = 0
		letter_count = 0
		last_vowel_index = 0
		first_vowel = True
		stress_next_vowel = False
		word_length = len(single_word)
		for i, letter in enumerate(single_word):
			if letter in v:
				if first_vowel: #rhythmic stress rule 1
					if word_length-i > 2 and single_word[i+1] in c and single_word[i+2] in c:
						single_word[i] = letter.upper()
						stress_next_vowel = False
					elif word_length-i > 3 and single_word[i+1] in c and single_word[i+2] in v  and single_word[i+3] in v: # geminated
						single_word[i] = single_word[i].upper()
						stress_next_vowel = False
					else:
						stress_next_vowel = True
					first_vowel = False
				elif stress_next_vowel == True and word_length-i > 1 and single_word[i+1] in v: #rhythmic stress rule 2
					single_word[last_vowel_index] = single_word[last_vowel_index].upper()
				elif stress_next_vowel == True and i > 2 and word_length-i > 2 and single_word[i-3] in v and single_word[i-2] in c and single_word[i-1] in c and single_word[i+1] in c and single_word[i+2] in v: #rhythmic stress rule 3
					single_word[last_vowel_index] = single_word[last_vowel_index].upper()
				elif stress_next_vowel == True:
					single_word[i] = single_word[i].upper()
					stress_next_vowel = False
				else:
					stress_next_vowel = True
				last_vowel_index = i
		single_word[last_vowel_index] = single_word[last_vowel_index].lower() #removes stress from last vowel
	return(single_word)

def add_gemination(single_word):
	"""
	Input: list form with stressed vowels in upper case (ex. ['t','u','m','E','m','i'])
	Output: list form with additional letters added for gemination case (ex. ['t','u','m','E','m','m','i'])

	Add additional character of geminated letter which is needed for chunk_syllables function
	"""
	word_length = len(single_word)
	geminated_wordform = []
	geminate_next_letter = False
	for i, letter in enumerate(single_word):
		if geminate_next_letter: # if the letter should be geminated according to next condition
			geminated_wordform.append(letter)
			geminated_wordform.append(letter)
			geminate_next_letter = False
		elif letter in v: #set the next consonant to be geminated if satisfied
			if single_word[i] == 'E':
				if i > 0 and word_length-i > 1 and (single_word[i-1] == single_word[i+1] or (single_word[i-1] == 'c' and single_word[i+1] == 'n') or (single_word[i-1] == 'n' and single_word[i+1] == 'c') or (single_word[i-1] == 'c' and single_word[i+1] == 't') or (single_word[i-1] == 't' and single_word[i+1] == 'c')):
					geminate_next_letter = True
					geminated_wordform.append(letter)
			elif word_length-i > 3 and single_word[i+1] in c and single_word[i+2] in v and single_word[i+3] in v:
				geminate_next_letter = True
				geminated_wordform.append(letter)
			else:
				geminated_wordform.append(letter)
		else: # no gemination, normal condition
			geminated_wordform.append(letter)
	return(geminated_wordform)

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
	for i, letter in enumerate(geminated_wordform):
		if skip == True:
			skip = False
		elif word_length-i == 1: # if last character
			syllable_wordform.append(geminated_wordform[last_index:i+1][::-1])
		elif geminated_wordform[i] == "'":
			syllable_wordform.append("'")
			last_index = i+1
		elif geminated_wordform[i+1] in c:
			syllable_wordform.append(geminated_wordform[last_index:i+2][::-1])
			skip = True
			last_index = i+2
		elif geminated_wordform[i+1] == "'":
			syllable_wordform.append(geminated_wordform[last_index:i+1][::-1])
			syllable_wordform.append("'")
			skip = True
			last_index = i+2
		#If none of these are satisfied then it passes a vowel
	syllable_wordform = syllable_wordform[::-1]
	return(syllable_wordform)

def voiceless_shift(syllable_wordform):
	"""
	Input: preliminary syllable list form (ex. [['t', 'u'], ['m', 'E', 'm'], ['m', 'i']])
	Output: preliminary syllable list form (ex. ['tu', 'mEm', 'mi'])

	Adds voiceless shifts. Starts by processing cases around apostrophes. Then handles neighboring voiced fricatives. Can account for apostrophes.
	"""
	syllable_lookup_format = []
	if syllable_wordform[0] == "'":
		del syllable_wordform[0]
	if syllable_wordform[-1] == "'":
		del syllable_wordform[-1]

	syllable_length = len(syllable_wordform)
	if syllable_wordform[0] != "'" and syllable_wordform[-1] != "'": #just a double check in case there are multiple apostrophes at the ends
		#proceed
		if syllable_wordform[0][0] == 's':
			syllable_wordform[0][0] = voiced_converter['s'] #handle the s at beginning and r at end cases
		if syllable_wordform[-1][-1] == 'r':
			syllable_wordform[-1][-1] = voiced_converter['r']

		if "'" in syllable_wordform: #condition if there is an apostrophe within the word
			double_skip = False
			skip = False
			for i, syllable in enumerate(syllable_wordform):

				if syllable_length-i == 1: #if last entry
					syllable_lookup_format.append(''.join(syllable_wordform[i]))
				elif double_skip: #assuming the v ' v condition was called
					double_skip = False
					skip = True
				else:
					if skip:
						skip = False
					else:
						if syllable_wordform[i+1] == "'":
							if syllable_wordform[i][-1] in v and syllable_wordform[i+2][0] in v: #if v ' v  then append surrounding syllables
								syllable_lookup_format.append(''.join(syllable_wordform[i]+syllable_wordform[i+2]))
								double_skip = True
							elif syllable_wordform[i][-1] in c and syllable_wordform[i+2][0] in v: # if c ' v gemination, add the consonant to the right side
								syllable_lookup_format.append(''.join(syllable_wordform[i]))
								syllable_wordform[i+2] = [syllable_wordform[i][-1]]+syllable_wordform[i+2]
								skip = True
							elif syllable_wordform[i][-1] in c and syllable_wordform[i+2][0] in c: # if c ' c gemination, no effect
								syllable_lookup_format.append(''.join(syllable_wordform[i]))
								skip = True
							else:
								raise ValueError('this is a rogue apostrophe that doesn\'t follow conventions')
						else: #if next entry exists and is not an apostrophe, do the fricative analysis
							if (syllable_wordform[i][-1] in voiced_fricatives and syllable_wordform[i+1][0] in stops) or (syllable_wordform[i][-1] in voiced_fricatives and syllable_wordform[i+1][0] in voiceless_fricatives):
								syllable_wordform[i][-1] = voiced_converter[syllable_wordform[i][-1]]
							elif syllable_wordform[i][-1] in stops and syllable_wordform[i+1][0] in voiced_fricatives:
								syllable_wordform[i+1][0] = voiced_converter[syllable_wordform[i+1][0]]
							elif (syllable_wordform[i][-1] in voiced_fricatives and syllable_wordform[i+1][0] in voiced_nasals) or (syllable_wordform[i][-1] in stops and syllable_wordform[i+1][0] in voiced_nasals):
								syllable_wordform[i+1][0] = voiced_converter[syllable_wordform[i+1][0]]
							syllable_lookup_format.append(''.join(syllable_wordform[i]))

		else: #if no apostrophe in the word, doesn't use extra computing to check for apostrophes each loop
			for i, syllable in enumerate(syllable_wordform):
				if syllable_length-i == 1: #if last entry
					syllable_lookup_format.append(''.join(syllable_wordform[i]))
				else:
					if (syllable_wordform[i][-1] in voiced_fricatives and syllable_wordform[i+1][0] in stops) or (syllable_wordform[i][-1] in voiced_fricatives and syllable_wordform[i+1][0] in voiceless_fricatives):
						syllable_wordform[i][-1] = voiced_converter[syllable_wordform[i][-1]]
					elif syllable_wordform[i][-1] in stops and syllable_wordform[i+1][0] in voiced_fricatives:
						syllable_wordform[i+1][0] = voiced_converter[syllable_wordform[i+1][0]]
					elif (syllable_wordform[i][-1] in voiced_fricatives and syllable_wordform[i+1][0] in voiced_nasals) or (syllable_wordform[i][-1] in stops and syllable_wordform[i+1][0] in voiced_nasals):
						syllable_wordform[i+1][0] = voiced_converter[syllable_wordform[i+1][0]]
					syllable_lookup_format.append(''.join(syllable_wordform[i]))
	else:
		raise ValueError('remove additional apostrophe from ends')
	return(syllable_lookup_format)

def parser(word):
	#doesn't account for nasal voiceless or apostrophe for beginning function case or hyphens!!!
	single_word = convert(word)
	#single_word = ['c', 'e', '8', 'I', 'r', 't', 'u', 'q']
	if "-" in single_word:
		single_word = process_enclitics(single_word)
	#print(single_word)
	single_word = assign_stressed_vowels(single_word)
	#print(single_word)
	geminated_wordform = add_gemination(single_word)
	#geminated_wordform = ['a','p','A',"'",'u','r','l','u','q']
	#print(geminated_wordform)
	syllable_wordform = chunk_syllables(geminated_wordform)
	#print(syllable_wordform)
	#print('mark')
	syllable_lookup_format = voiceless_shift(syllable_wordform)
	#print(syllable_lookup_format)
	return(syllable_lookup_format)

if __name__ == "__main__":
	s = argparse.ArgumentParser(description='parse a given word into separate units.')
	s.add_argument('file', help='yup\'ik string to be parsed')
	args = s.parse_args()
	print(parser(args.file))
