stops = ['p','t','c','k','q']
voiced_fricatives = ['v','l','s','g','r'] #removed y condition here
voiceless_fricatives = ['vv','ll','ss','gg','rr','1','2','3','4','5']
voiced_converter = {'v':'1','l':'2','s':'3','g':'4','r':'5','n':'8','m':'7','6':'9'}
voiced_nasals = ['m','n','ng','6']
voiceless_nasals = ['hm','hn','hng','7','8','9']
c = ['p','t','c','k','q','v','l','s','y','g','r','vv','ll','ss','gg','rr','m','n','ng','hm','hn','hng', '1', '2', '3', '4', '5', '6', '7', '8', '9']
v = ['a','e','i','u', 'A','E','I','U']
prime_v = ['a','i','u', 'A','I','U']

def isHeavy(word):
    for i, letter in enumerate(word[:-1]):
        if word[i] in v and word[i+1] in v:
            return True
    return False

def isClosed(word):
    if word[-1] == '@':
        if word[-2] in c:
            return True
        else:
            return False
    elif word[-1] in c:
        return True
    else:
        return False

def convert(word):
    word = word.replace('vv','1')
    word = word.replace('ll','2')
    word = word.replace('ss','3')
    word = word.replace('gg','4')
    word = word.replace('rr','5')
    word = word.replace('ng','6')
    word = word.replace('hm','7')
    word = word.replace('hn','8')
    word = word.replace('hng','9')
    return word

def deconvert(word):
    word = word.replace('1','vv')
    word = word.replace('2','ll')
    word = word.replace('3','ss')
    word = word.replace('4','gg')
    word = word.replace('5','rr')
    word = word.replace('6','ng')
    word = word.replace('7','hm')
    word = word.replace('8','hn')
    word = word.replace('9','hng')
    return word