# !/usr/bin/python
# -*- coding:utf-8 -*-
# Authors: cwtliu, Temigo

#ASSUMING THAT INPUT IS IN CONVERTED FORM (ng is represented by a number)
import re
from constants import *
from tts_parser import *
from tts_parser_v2 import *

def convert(word):
    word = word.replace('vv','1')
    word = word.replace('ll','2')
    word = word.replace('ss','3')
    word = word.replace('gg','4')
    word = word.replace('rr','5')
    word = word.replace('ng','6')
    word = word.replace('μ','7')
    word = word.replace('ń','8')
    word = word.replace('TMg','9')
    word = word.replace('¥r','j')
    word = word.replace('¥rr','z')
    word = word.replace('¥g','x')
    word = word.replace('¥k','h')
    word = word.replace('¥q','d')
    return word

def deconvert(word):
    word = word.replace('1','vv')
    word = word.replace('2','ll')
    word = word.replace('3','ss')
    word = word.replace('4','gg')
    word = word.replace('5','rr')
    word = word.replace('6','ng')
    word = word.replace('7','μ')
    word = word.replace('8','ń')
    word = word.replace('9','TMg')
    word = word.replace('j','¥r')
    word = word.replace('z','¥rr')
    word = word.replace('x','¥g')
    word = word.replace('h','¥k')
    word = word.replace('d','¥q')
    return word

class Postbase(object):
    def __init__(self, formula, isEnding=False, debug=0):
        self.formula = formula
        self.final = not "\\" in formula
        self.debug = debug
        self.token = []
        self.tokens = self.tokenize(self.formula) # meaningful tokens
        self.isEnding = isEnding
        if not self.matched() and self.debug>=2: print("Warning: %s has non-matching parenthesis." % formula)
        self.reappend = False

    def __repr__(self):
        return self.formula

    # Check that simple parenthesis are matched in string
    def matched(self):
        count = 0
        for i in self.formula:
            if i == "(":
                count += 1
            elif i == ")":
                count -= 1
            if count < 0:
                return False
        return count == 0

    def tokenize(self, formula):
        """
        Tokenize postbase formula.

        >>> p = Postbase("+'(g/t)u:6a")
        >>> p.tokens
        ['+', "'", '(g/t)', 'u', ':6', 'a']
        """
        return filter(None, re.split(re.compile("(\([\w|/]+\))|(:[\w|\d]|:\(6\)|:\(e\)|:\(u\))|([\w|+|@|'|-|%|~|.|?|—])"), formula))

    def concat(self, word):
        new_word = word
        if self.formula == "$": #this is the optative 2nd person singular subject intransitive
            if word[-2]=='t' and word[-1]=='e':
                self.tokens = ["'",'e','n']
            elif (word[-1] in vowels and word[-2] in vowels) or word[-1]=='e':
                self.tokens = ['(g)','i']
            elif word[-1] in prime_vowels:
                self.tokens = []
            elif word[-1] in consonants:
                self.tokens = [':','a']
        elif self.formula == "&": #this is the optative 2nd person singular subject 3rd person singular transitive
            if word[-2]=='t' and word[-1]=='e':
                self.tokens = ['@','g','u']
            elif (word[-1] in vowels and word[-2] in vowels) or word[-1]=='e':
                self.tokens = ['(g)','i','u']
            elif word[-1] in prime_vowels:
                self.tokens = ['u']
            elif word[-1] in consonants:
                self.tokens = ['-','g','u','u']
        for i, token in enumerate(self.tokens):
            new_word = self.apply(token, new_word, word, i)
            print(token, new_word)
            if self.debug>=2: print(token, new_word)
        return new_word

    def begins_with(self, token):
        """
        Check whether postbase begins with token.

        >>> p = Postbase("+'(g/t)u:6a")
        >>> p.begins_with("(g/t)")
        True
        >>> p.begins_with("n")
        False
        """
        # FIXME what if there is (6) or :6 in the suffix? Does it count as beginning with 6 ?
        return next(token for token in self.tokens if re.search("[\w|\d]", token)) == token

    def apply(self, token, root, original_root, counter):
        """
        token and word are (properly encoded) strings.
        Apply token to word. Modify word in place.
        Assuming root does not have any dash at the end.

        >>> p1 = Postbase("-nrite")
        >>> p1.apply("-", "pissur")
        'pissu'
        >>> p2 = Postbase("~+miu")
        >>> p2.apply("~", "nere")
        'ner'
        >>> p3 = Postbase("%lu")
        >>> p3.apply("%","imir")
        'imi'
        >>> p3.apply("%","pag")
        'pag'
        >>> p3.apply("%","iqaar")
        'iqaar'
        >>> p4 = Postbase("%(e)nka")
        >>> p4.apply("%","qimugte")
        'qimugte'
        >>> p5 = Postbase(":6a")
        >>> p5.apply(":6","pitu")
        'pitu'
        >>> p5.apply(":6","ner'u")
        "ner'u"
        >>> p6 = Postbase(":guq")
        >>> p6.apply(":g","pai")
        'paig'
        >>> p7 = Postbase(":ruluku")
        >>> p7.apply(":r","paa")
        'paar'
        >>> p7.apply(":r","pa")
        'pa'
        >>> p8 = Postbase("-qatar-")
        >>> p8.apply("q","ayag")
        'ayak'
        >>> p9 = Postbase("'(g/t)uq")
        >>> p9.apply("'","ner")
        'ner'
        >>> p9.apply("'","qaner")
        'qaner'
        >>> p10 = Postbase("@~+ni-")
        >>> p10.apply("@","kipute")
        'kiput'
        >>> p10.apply("@","apte")
        'ap'
        >>> p11 = Postbase("@~+6aite-")
        >>> p11.apply("@","kipute")
        'kipus'
        >>> p12 = Postbase("@~+6aite-")
        >>> p12.apply("@","maan(e)te")
        'maan(e)l'
        >>> p13 = Postbase("@~:(u)ciq")
        >>> p13.apply("@","kipute")
        'kipus'
        >>> p14 = Postbase("@~:(u)ciq")
        >>> p14.apply("@","kit'e")
        "kis'u"
        >>> p15 = Postbase("@~:(u)ciq")
        >>> p15.apply("@","ce8irte")
        'ce8iru'
        >>> p16 = Postbase("@~+yug-")
        >>> p16.apply("@","kipute")
        'kipus'
        >>> p17 = Postbase("@~+6aite-")
        >>> p17.apply("@","kipute")
        'kipuc'
        >>> p18 = Postbase("@~+6aite-")
        >>> p18.apply("@","kit'e")
        'kic'
        """
        asterisk = False
        if len(root) == 0:
            return root
        if root[-1:] == '*':
            root = root[:-1]
            original_root = original_root[:-1]
            asterisk = True
        if len(root) > 3:
            if root[-3:] == '2er':
                asterisk = True
            elif len(root) > 4:
                if root[-4:] == '(ar)' and self.tokens.index(token) == 0:
                    if '+' in self.tokens:
                        root = root[:-4]
                    else:
                        root = root[:-4]+'ar'
                        original_root = root[:-4]+'ar'
                if root[-4:] == 'yaar':
                    asterisk = True          
                elif len(root) > 5:
                    if root[-5:] == 'yagar':
                        asterisk = True       
                    elif root[-5:] == '2erar':
                        asterisk = True    
                    elif len(root) > 7:
                        if root[-7:] == 'kegtaar':
                                asterisk = True

        if root[-1] == "-":
            print("Root should not have a dash at the end.")
            return root
            #raise Exception("Root should not have a dash at the end.")

        #if self.reappend:
        #    self.tokens[self.tokens.index(token)] = ':' + token
        #    token = ':' + token
        #    self.reappend = False

        # Return the first alpha item in tokens list
        first_letter=''
        first_letter_index = -1
        for l in self.tokens:
            if l.isalnum():
                first_letter = l
                first_letter_index = self.tokens.index(l)
                break
        # print(first_letter)
        flag = False
        if '(ar)' in root and self.tokens.index(token) == 0:
            root = root.replace('(ar)','')

        if token == '=':
            root = root+'='
        elif token == '~':
            if root[-1] == 'e':
                root = root[:-1]
        elif token == "+":
            pass
        elif token == 's' and root[-1] == 't' and root[-2] in consonants:
            root = root[:-1]+'c'
        elif token == "(ar)":
            root = root+'(ar)'
        elif token == "-":
            if root[-1] in consonants and root[-1] != 't':
                root = root[:-1]
        elif token == "%":
            if len(root) > 3: #not sure where this came from
                if root[-1] == 'r' and root[-2] in vowels and root[-3] in vowels and root[-4] in consonants:
                    flag = True
            if flag:
                pass
            elif root[-1] == 'g' or (len(root) >= 2 and root[-2:] == 'er') or asterisk:
                pass
            elif root[-1] in ["g", "r"]:
                root = root[:-1]
            flag = False
        elif token in [":(e)", ":(u)", "(e)", "(te)"]:
            if token == ':(u)':
                if root[-1] == 't' and root[-2] in vowels: #non-special te
                    root = root[:-1]+'yu'
                #elif nonspecial te and root[-3] in vowels, then add l
                if root[-1] == "'":
                    root = root[:-2]+"s'u"
                elif root[-1] == 't' and root[-2] in fricatives:
                    root = root[:-1]+'u'
                elif root[-1] == 't' and (root[-2] in nasals or root[-2] in stops):
                    root = root[:-1]+'elu'
                elif root[-1] in consonants:
                    root = root+':u'
                #if : is appended it means that is subject to velar droppint if the first vowel is long
            if token == ':(e)':
                if root[-1] in ['g','r','6']:
                    if root[-2] == 'e' and root[-3] not in vowels and root[-1] == 'r': #ere case -> aa
                        root = root+'aa'
                    elif root[-2] == 'a' and root[-3] not in vowels and root[-1] == 'r': #ere case -> aa
                        root = root[:-1]+'a'
                    elif root[-2] == 'u' and root[-3] not in vowels: #doesn't handle ega case
                        root = root[:-1]+'u'
                    elif root[-2] == 'i' and root[-3] not in vowels: #doesn't handle ega case
                        root = root[:-1]+'i'
                    elif root[-2] == 'a' and root[-3] not in vowels: #doesn't handle ega case
                        root = root[:-2]+'ii'
                    elif root[-2] in prime_vowels and root[-3] not in vowels:
                        root = root[:-1]+'e'
                    else:
                        root = root + 'e'
                elif root[-1] == 'e':
                    pass
                elif root[-1] in vowels and root[-2] not in vowels:
                    root = root+'a'
            #ADD OTHER CONDITIONS
        elif token == ":6" or token == ":(6)":
            position = self.tokens.index(token)
            if root[-1] in ['g','r','6'] and len(root) > 3: #velar case for g r or ng
        #                 if 'age' in string_word:
        #     word2 = word2.replace('age','ii')
        #                            enga 'ii'
        #     word2 = word2.replace('ige','ii')
                                    # egi 'ii'
                                    # enga ii
        #     word2 = word2.replace('are','aa')    

        #                            engi 'ai'
                                    # iga 'ia'                                   
        #     word2 = word2.replace('uge','uu')                                
                if position+2 == len(self.tokens):
                    if len(root) >= 2 and self.tokens[position+1] == 'i' and root[-2] == 'e' and root[-3] not in vowels: #doesn't handle ega case
                        root = root[:-2]+'i'
                        self.tokens[position+1] = 'i'
                    elif len(root) >= 2 and self.tokens[position+1] == 'a' and (root[-2] == 'e' or root[-2] == 'a') and root[-3] not in vowels: # root[-1] == 'a' according to nuna and :(ng)at, nuniit, may not be true only applying to end of word aa, nunii
                        root = root[:-2]+'i'
                        self.tokens[position+1] = 'i'
                    elif len(root) >= 2 and self.tokens[position+1] == 'u' and root[-2] == 'e' and root[-3] not in vowels:
                        root = root[:-2]+'u'
                        self.tokens[position+1] = 'u'
                    elif len(root) >= 2 and self.tokens[position+1] in vowels and root[-2] in prime_vowels and root[-3] not in vowels:
                        root = root[:-1]
                elif position+2 < len(self.tokens):
                    # print(root)
                    # print(self.tokens[position+1])
                    if len(root) >= 2 and self.tokens[position+1] == 'i' and self.tokens[position+2] not in vowels and root[-2] == 'e' and root[-3] not in vowels:
                        root = root[:-2]+'i'
                        self.tokens[position+1] = 'i'
                    elif len(root) >= 2 and self.tokens[position+1] == 'a' and self.tokens[position+2] not in vowels  and root[-2] == 'e' and root[-3] not in vowels:  # root[-1] == 'a' according to nuna and :(ng)at, nuniit, may not be true using nunaat but not nunii
                        root = root[:-2]+'i'
                        self.tokens[position+1] = 'i'
                    elif len(root) >= 2 and self.tokens[position+1] == 'e' and self.tokens[position+2] not in vowels and root[-2] == 'u' and root[-3] not in vowels:
                        root = root[:-2]+'u'
                        self.tokens[position+1] = 'u'
                    elif len(root) >= 2 and self.tokens[position+1] in vowels and self.tokens[position+2] not in vowels and root[-2] in prime_vowels and root[-3] not in vowels:
                        root = root[:-1]
            elif position+2 == len(self.tokens):
                if len(root) >= 2 and self.tokens[position+1] == 'i' and root[-1] == 'e' and root[-2] not in vowels:
                    root = root[:-1]+'a'
                    self.tokens[position+1] = 'i'
                elif len(root) >= 2 and self.tokens[position+1] == 'a' and (root[-1] == 'e' or root[-1] == 'a') and root[-2] not in vowels:
                    root = root[:-1]+'i'
                    self.tokens[position+1] = 'i'
                elif len(root) >= 2 and self.tokens[position+1] == 'u' and root[-1] == 'e' and root[-2] not in vowels:
                    root = root[:-1]+'u'
                    self.tokens[position+1] = 'u'
                elif len(root) >= 2 and self.tokens[position+1] in vowels and root[-1] in prime_vowels and root[-2] not in vowels:
                    root = root #+''.join(self.tokens[:position])
                else:
                    if root[-1] in vowels:
                        root = root+'6'
                    # elif root[-1] == 't':
                    #     root = root[:-1]+'s6'#+''.join(self.tokens[:position])+'6' #not sure about this
                    else:
                        root = root+'6'
            elif position+2 < len(self.tokens):
                if len(root) >= 2 and self.tokens[position+1] == 'i' and self.tokens[position+2] not in vowels  and root[-1] == 'e' and root[-2] not in vowels:
                    root = root[:-1]+'a'
                    self.tokens[position+1] = 'i'
                elif len(root) >= 2 and self.tokens[position+1] == 'a' and self.tokens[position+2] not in vowels  and root[-1] == 'e' and root[-2] not in vowels: # root[-1] == 'a' according to nuna and :(ng)at, nuniit, may not be true
                    root = root[:-1]+'i'
                    self.tokens[position+1] = 'i'
                elif len(root) >= 2 and self.tokens[position+1] == 'u' and self.tokens[position+2] not in vowels  and root[-1] == 'e' and root[-2] not in vowels:
                    root = root[:-1]+'u'
                    self.tokens[position+1] = 'u'
                elif len(root) >= 2 and self.tokens[position+1] in vowels and self.tokens[position+2] not in vowels  and root[-1] in prime_vowels and root[-2] not in vowels:
                    root = root #+''.join(self.tokens[:position])
                else:
                    if root[-1] in vowels:
                        root = root+'6'
                    # elif root[-1] == 't':
                    #     root = root[:-1]+'s6'#+''.join(self.tokens[:position])+'6' #not sure about this
                    else:
                        root = root+'6'
        elif token == ":g":
            position = self.tokens.index(token)
            #print(self.tokens.index(token))
            #print(self.tokens)
            if position+2 == len(self.tokens):
                #print('yes')
                if len(root) >= 2 and self.tokens[position+1] in vowels and root[-1] in vowels and root[-2] not in vowels:
                    root = root #+''.join(self.tokens[:position])
                else:
                    root = root+'g'#+''.join(self.tokens[:position])+'6'
            elif position+2 < len(self.tokens):
                if len(root) >= 2 and self.tokens[position+1] in vowels and self.tokens[position+2] not in vowels and root[-1] in vowels and root[-2] not in vowels:
                    root = root #+''.join(self.tokens[:position])
                else:
                    root = root+'g'#+''.join(self.tokens[:position])+'6'
        elif token == ":r":
            position = self.tokens.index(token)
            #print(self.tokens.index(token))
            #print(self.tokens)
            if position+2 == len(self.tokens):
                #print('yes')
                if len(root) >= 2 and self.tokens[position+1] in vowels and root[-1] in vowels and root[-2] not in vowels:
                    root = root #+''.join(self.tokens[:position])
                else:
                    root = root+'r'#+''.join(self.tokens[:position])+'6'
            elif position+2 < len(self.tokens):
                if len(root) >= 2 and self.tokens[position+1] in vowels and self.tokens[position+2] not in vowels and root[-1] in vowels and root[-2] not in vowels:
                    root = root #+''.join(self.tokens[:position])
                else:
                    root = root+'r'#+''.join(self.tokens[:position])+'6'
        elif token == ":a": #A BIT TENTATIVE IF IT'S TRUE THAT E SHOULD BE DROPPED IN THE ELSE: IF: BELOW
            if root[-1] in vowels:
                root = root[:-1]+'a'
            else:
                if root[-1] in velars and root[-2] =='e' and root[-3] in consonants:
                    root = root[:-2]+root[-1]+'a'
                elif root[-1] in velars and root[-2] in vowels and root[-3] in consonants:
                    root = root[:-1]+'a'
                else:
                    root = root + 'a'
        elif self.tokens.index(token) == first_letter_index and token in ['g', 'k', '4', 'q', 'r', '5'] + vowels and counter < 2 and root[-1] in consonants:
            if token == 'g':
                if original_root[-1] == 'q' or original_root[-1] == 'r' or original_root[-1] == '5':
                    root = original_root[:-1]+'r'
                else:
                    root = root + 'g'
            elif token == 'k':
                if original_root[-1] == 'q' or original_root[-1] == 'r' or original_root[-1] == '5':
                    root = original_root[:-1]+'q'
                else:
                    root = root + 'k'
            elif token == '4':
                if original_root[-1] == 'q' or original_root[-1] == 'r' or original_root[-1] == '5':
                    root = original_root[:-1]+'5'
                else:
                    root = root + '4'
            elif token == 'q':
                if original_root[-1] == 'g' or original_root[-1] == 'k' or original_root[-1] == '4':
                    root = original_root[:-1]+'k'
                else:
                    root = root + 'q'
            elif token == 'r':
                if original_root[-1] == 'g' or original_root[-1] == 'k' or original_root[-1] == '4':
                    root = original_root[:-1]+'g'
                else:
                    root = root + 'r'
            elif token == '5':
                if original_root[-1] == 'g' or original_root[-1] == 'k' or original_root[-1] == '4':
                    root = original_root[:-1]+'4'
                else:
                    root = root + '5'
        elif self.tokens.index(token) == first_letter_index and token in vowels:
            if len(root) >= 2 and (root[-2:] == 'er' or root[-2:] == 'eg'):
                root = root[:-2]+root[-1]+token
            # elif len(root) >= 2 and (root[-2:] == 'e4' or root[-2:] == 'e5'):
            #     root = root[:-2]+root[-1]+token
            else:
                if root[-1] == 'e':
                    root = root[:-1] + token
                else:
                    root = root + token
        elif token == "'":
            replace = False
            if '[e]' in root:
                root = root.replace('[e]','e')
                replace = True
            if len(root) == 3:
                if root[-1] == 'e' and root[-2] in consonants and root[-3] in vowels:
                    root = root[:-1] + "'"
            elif len(root) == 4:
                if root[-1] == 'e' and root[-2] in consonants and root[-3] in vowels and root[-4] in consonants:
                    root = root[:-1] + "'"
            elif len(root) == 5:
                if root[-1] == 'e' and root[-2] in consonants and root[-3] in vowels and root[-4] in consonants and root[-5] == 'e':
                    root = root
            if replace:
                root = '[e]'+root[1:]
        elif token == ".":
            pass
        elif token == "@":
            # THIS IS ALL @ N RULE
            if len(root) >= 2 and root[-2:] == "te": # assuming an e deletion has already occurred...
                root = root[:-1]
            #print(first_letter)
            #print(self.tokens)
            if first_letter == "n":
                if len(root) >= 2 and root[-1] == "t" and (root[-2] in voiced_fricatives \
                                    or root[-2] in voiceless_fricatives \
                                    or root[-2] in voiced_nasals \
                                    or root[-2] in voiceless_nasals \
                                    or root[-2] in stops):
                    root = root[:-1]
                else:
                    pass
            elif first_letter == 'c' and root[-1] == 't': #if firstletter is c then remove te altogether
                root = root[:-1]
            # UNSURE OF HOW THIS WORKED, SO REPLACED WITH FUNCTION BELOW
            # elif self.tokens.index(token) == first_letter_index and token in ['l','g','k','6'] and self.isEnding:
            #     if token == 'l':
            #         if root[-1] == 't':
            #             root = root[:-1] + '2'
            #         else:
            #             root = root + 'l'
            #     else:
            #         if root[-1] == 't' and '(e)' in self.tokens:
            #             root = root[:-2] + 'es' #assuming that the (e) is a single index and removed
            #         elif root[-1] == 't':
            #             root = root[:-1] + 's'
            #         else:
            #             root = root + token
            elif first_letter == 't' and root[-1] == 't':
                root = root[:-1]
            elif first_letter in ['l','g','k','6']:
                if first_letter == 'l':
                    if root[-1] == 't':
                        root = root[:-1] + 'l'
                else:
                    if root[-1] == 't' and '(e)' in self.tokens:
                        root = root[:-2] + 'es' #assuming that the (e) is a single index and removed
                    elif root[-1] == 't' and root[-2] in consonants and first_letter == '6' and self.tokens[self.tokens.index('6')+1] in consonants:
                        root = root + 'e'                    
                    elif root[-1] == 't' and root[-2] in consonants:
                        root = root[:-1] + 'es'
                    elif root[-1] == 't' and first_letter == '6':
                        if self.tokens[self.tokens.index('6')+1] in consonants:
                            root = root+'e'
                    elif root[-1] == 't':
                        root = root[:-1] + 's'
                    #elif root[-1] == 't' and special te, then append 'l'
            # elif first_letter == 't':
            #     if root[-1] == 't':
            #         root = root[:-1]+'l'
            elif (first_letter == "6" or first_letter == "m" or first_letter == "v") \
                                    and len(root) >= 2 \
                                    and root[-1] == "t" \
                                    and not self.isEnding \
                                    and (root[-2] in voiced_fricatives \
                                        or root[-2] in voiceless_fricatives \
                                        or root[-2] in voiced_nasals \
                                        or root[-2] in voiceless_nasals \
                                        or root[-2] in stops):
                #print('yes')
                if root[-2] in stops:
                    root = root[:-1]
                elif root[-2] == 'm':
                    root = root[:-2]+'7'
                elif root[-2] == 'n':
                    root = root[:-2]+'8'
                elif root[-2] == '6':
                    root = root[:-2]+'9'
                elif root[-2] == 'v':
                    root = root[:-2]+'1'
                elif root[-2] == 'l':
                    root = root[:-2]+'2'
                elif root[-2] == 's':
                    root = root[:-2]+'3'
                elif root[-2] == 'g':
                    root = root[:-2]+'4'
                elif root[-2] == 'r':
                    root = root[:-2]+'5'

            elif (first_letter == "6" or first_letter == "m" or first_letter == "v") \
                                    and root[-1] == "t" \
                                    and '(e)' in root:
                root = root[:-1]+'l'
            elif (first_letter == "6" or first_letter == "m" or first_letter == "v") \
                                    and len(root) >= 2 \
                                    and root[-1] == "t" \
                                    and root[-2] in vowels:
                root = root[:-1]+'s' #IT MAY BE EASIER TO HAVE CODE THAT REPRESENTS (E) as a single token
        elif token == "(u)" and self.begins_with("(u)") and not self.isEnding:
            if len(root) >= 2 and root[-1] == "t" and root[-2] in vowels:
                root = root[:-1] + "y"
            elif len(root) >= 6 and root[-6:] == "(e)te":
                root = root[:-2] + "l"
        elif first_letter == "y" and not self.isEnding and self.tokens.index(token) == first_letter_index:
            if len(root) >= 2 and root[-1] == "t":
                root = root[:-1] + "c" #NEEDS A WAY TO REMEMBER NOT TO ADD THE Y of 'yug', BECAUSE OTHERWISE KIPUCU is KIPUCYU
            elif len(root) >= 2 and root[-1] in voiceless_fricatives or root[-1] in stops:
                if root[-1] not in vowels and root[-2] not in vowels:
                    root = root+'es'
                else:
                    root = root + "s"
            else:
                root = root + "y"
        elif token == "?": # TODO
            pass
        # elif token in consonants and root[-1] == 'r' and root[-2] == '6':
        #     root = root[:-1]+'e'+root[-1]+token
        elif re.search(re.compile("\("), token): # All the (g), (g/t), etc
            letters = [x for x in re.split(re.compile("\(|\)|\/"), token) if len(x) > 0]
            conditions = {
                "i": len(root) >= 2 and root[-2:] == "te",
                "6": root[-1] in vowels,
                "r": len(root) >= 2 and root[-2:] == "te",
                "s": root[-1] in vowels,
                "t": original_root[-1] in consonants or root[-1] in consonants,
                "u": root[-1] in consonants or original_root[-1] == "e",
                "g": len(root) >= 2 and root[-2] in vowels and root[-1] in vowels,
                # FIXME (q)must be used with demonstrative adverb bases,
                # but is optional with positional bases (p.179)
                "q": False,
                "ar": False,
                "aq": False,
                "ur": False,
            }
            for letter in letters:
                if conditions[letter]:
                    if token == '(6)':
                        if root[-1] == 'e' and root[-2] == 't' and root[-3] not in vowels:
                            root += '9'
                        else:
                            root += '6' 
                    else:
                        root += letter
        elif token == 's' and root[-1] == 't':
            root = root[:-1]+'c'
        elif token == 'v':
            if root[-1] == 't':
                root = root[:-1]+'p'
            else:
                root = root + 'v'
        elif token == "\\" or token == ":":
            pass # not an ending
        elif token in vowels or token in consonants:
            if self.debug>=2: print("Default token", token)
            if token in vowels and root[-1] == 'e':
                root = root[:-1] + token
            else:
                root = root + token
        #elif token[0] == ':':
        #    if len(token[1:]):
        #        self.tokens[self.tokens.index(token)] = token[1:]
        #        root = self.apply(token[1:], root)
        #    self.reappend = True
        else:
            print("Unknown token: %s (in postbase %s decomposed as %s)" % (token, self.formula, self.tokens))
            #raise Exception("Unknown token: %s (in postbase %s decomposed as %s)" % (token, self.formula, self.tokens))
        return root

    def post_apply(self, word):
        skip = False
        word = convert(word)
        # if '(ar)' in word:
        #     word = word.replace('(ar)','')
        word1 = ''
        # print(word)
        if word:
            word_list = process_apostrophe_voicelessness(word)
            word_list = chunk_syllables(word_list)
            word_list = assign_stress(word_list)
            removedindex = -1
            print(word_list)
            for i, entry in enumerate(word_list):
                if 'e' in entry and '$' in entry and '%' not in entry and i != 0 and entry[2] not in ['7','8','9']:
                    if not (entry[0]==entry[2] or (entry[0]=='c' and (entry[2]=='n' or entry[2]=='t')) or ((entry[0]=='n' or entry[2]=='t') and entry[2]=='c')):
                        if entry[-2] == word_list[i+1][0] and entry[-2] != '9':
                            if word_list[i-1][-1] != '$':
                                word = word.replace(entry[:-1],entry[0]+'^'+entry[2])
                                for i, letter in enumerate(word):
                                    if letter == '^':
                                        removedindex = i
                                word = word.replace('^','')
            for i, letter in enumerate(word[1:-1]):
                if word[i+1] in voiced_fricatives and word[i+2] in voiceless_fricatives:  #accordance rules on page 732 rll becomes rrl
                    letter=voiced_converter[letter]
                word1 = word1+letter
            word = word[0]+word1+word[-1]
            word1 = ''
            for i, letter in enumerate(word[1:-1]):
                if letter in voiceless_fricatives:
                    if (word[i] in stops or word[i+2] in stops) or word[i] in voiceless_fricatives: #apply voiceless fricative removal if next to stop or other vf
                        letter=voiceless_converter[letter]
                word1 = word1+letter
            word = word[0]+word1+word[-1]
            word1 = ''
            for i, letter in enumerate(word[1:-1]):
                if word[i] in vowels and word[i+1] in vowels and word[i+2] in vowels:  #three vowel cluster
                    letter=''
                word1 = word1+letter
            word = word[0]+word1+word[-1]
            word1 = ''
            for i, letter in enumerate(word[1:-1]): #three consonant cluster for t only
                if skip:
                    skip = False
                    letter = ''
                else:
                    if word[i] in consonants and word[i+1] =='t' and word[i+2] in consonants:  #three vowel cluster
                        if word[i+2] in fricatives or word[i+2] in nasals:
                            letter='te'+voiced_converter[word[i+2]]
                        else:
                            letter='te'+word[i+2]
                        skip = True
                word1 = word1+letter
            word = word[0]+word1+word[-1]

            word1 = ''
            if len(word) > 4: #make sure word is long enough and doesn't get truncated
                for i, letter in enumerate(word[2:-2]): #removal of apostrophe if in geminated form
                    if word[i] in vowels and word[i+1] in consonants and word[i+2] == "'" and word[i+3] in vowels and word[i+4] in vowels:
                        letter = ''
                    else:
                        letter = word[i+2]
                    word1 = word1+letter
                word1 = word[0]+word[1]+word1+word[-2]+word[-1]
            else:
                word1 = word
            if 'erar' in word1:
                word1 = word1.replace('erar','er')
            if 'eraqa' in word1:
                word1 = word1.replace('eraqa','erqa')
            #COMPLETE IN POSTBASES e drop? tangrrutuk
            #COMPLETE IN POSTBASES yaqulegit -> yaqulgit -- e preceding g or r endings and suffix has initial vowel
            stressed_vowels = assign_stressed_vowels(word1)
            string_word = ''.join(stressed_vowels)
            if '6rp' in string_word:
                string_list = string_word.split('6rp')
                if string_list[0][-1].isupper() or string_list[0][-1] in consonants:
                    string_word = string_word.replace("6rp","6erp")
                else:
                    string_word = string_word.replace("6rp","6'erp")
            if '6rm' in string_word:
                string_list = string_word.split('6rm')
                if string_list[0][-1].isupper() or string_list[0][-1] in consonants:
                    string_word = string_word.replace("6rm","6erm")
                else:
                    string_word = string_word.replace("6rm","6'erm")
            # if 'age' in string_word:
            #     word2 = word2.replace('age','ii')
            # if 'uge' in string_word:
            #     word2 = word2.replace('uge','uu')
            # if 'ige' in string_word:
            #     word2 = word2.replace('ige','ii')
            # if 'are' in string_word:
            #     word2 = word2.replace('are','aa')   
            stressed_vowels = list(string_word)
            word2=''.join(stressed_vowels)
            if len(word) > 3:
                if word[-3:] == '2er':
                    if not word2[-4].isupper():
                        word2 = word2[:-2]+"'er"
            if len(word) > 5:
                if word[-5:] == 'yagaq':
                    if word2[-4].islower():
                        word2 = word2[:-3]+"ar"
            # print(stressed_vowels)
            stressed_vowels = list(word2)
            # if 'E' in stressed_vowels:  #removes stressed e unless it is surrounded by similar letters or c and n/t (chapter 1 from grammar book)
                # chunked = chunk_syllables(stressed_vowels)
                # # print(chunked)
                # for i, group in enumerate(chunked):
                #     chunked[i]=''.join(group)
                #     # if chunked[i][-1] != 'E':
                #     #     chunked[i]=chunked[i].lower()
                # print(chunked)
                # stressed_vowels = list(''.join(chunked))
                # print(stressed_vowels)
                # result = [i for i, x in enumerate(stressed_vowels) if x == 'E']
                # # print(result)
                # for index in result:
                #     if not (stressed_vowels[index-1]==stressed_vowels[index+1] or (stressed_vowels[index-1]=='c' and (stressed_vowels[index+1]=='n' or stressed_vowels[index+1]=='t')) or ((stressed_vowels[index-1]=='n' or stressed_vowels[index+1]=='t') and stressed_vowels[index+1]=='c')):# or ():
                #         stressed_vowels[index]=''
                #     if index > 2:
                #         if stressed_vowels[index-2] in vowels:
                #             if stressed_vowels[index-2].isupper():
                #                 stressed_vowels[index] = 'E'
                #         if stressed_vowels[index-3] in vowels:
                #             if stressed_vowels[index-3].isupper():
                #                 stressed_vowels[index] = 'E'
            # print(stressed_vowels)
            # switch to voiced/voiceless? gg to rr
            word1=''.join(stressed_vowels).lower()
        return word1, removedindex

# antislash means something comes after
postbases = [
    "-llru\\",
    "-lli\\",
    "-nrite\\",
    "@~+yug\\",
    "-qatar\\",
    "+'(g/t)uq"
    ]

if __name__== '__main__':
    p1 = Postbase("-llru\\")
    p2 = Postbase("-nrite\\")
    p3 = Postbase("+'(g/t)ur:6ag")
    w = "nerenrituq"
    #p2.tokens = [':6','a']
    # Check in dictionary
    print p1.concat("pissur")
    #print(p2.apply("~", "nere"))
    #print(p2.apply("-", "pissur"))
    #print(p2.apply(":6", "pissuru"))
    #print(p2.apply(":g", "pissur"))
    #print(p2.tokens)
    #print(p2.concat("nere"))
    #print(p3.tokens)
    #print(p3.concat("nere"))
    #p4 = Postbase("@~+yug\\", debug=2)
    #print(p4.concat("ce8irte"))
    # Run docstring tests
    #import doctest
    #doctest.testmod()
