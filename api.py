# -*- coding:utf-8 -*-

from flask import Flask, send_file
from flask_restful import Resource, Api, reqparse
from flask_restful.utils import cors
import json
import os
from flask.json import jsonify
from pydub import AudioSegment
from common.parser.parser import Postbase, deconvert
from common.parser.tts_parser_v2 import parser
from urllib import unquote_plus

app = Flask(__name__)
api = Api(app)
api.decorators = [cors.crossdomain(origin='*', automatic_options=False)]
api.methods = ['GET', 'OPTIONS', 'POST', 'PUT']


# Define parser and request args
parser_api = reqparse.RequestParser()
parser_api.add_argument('root', type=str)
parser_api.add_argument('postbase', type=str, action='append')

# FIXME obsolete
# Takes a list of dict/json objects and add id field
def index(l):
    new_l = []
    for i in range(len(l)):
        new_x = l[i]
        new_x['id'] = i
        new_l.append(new_x)
    return new_l


nouns = index(json.load(open("assets/root_nouns_upd3-18.json")))
verbs = index(json.load(open("assets/root_verbs_upd3-18.json")))
postbases = index(json.load(open("assets/postbases_upd3-18.json")))
endings = index(json.load(open("assets/endings_upd3-18.json")))

new_dict0 = json.load(open("assets/dictionary_draft3_alphabetical_16.json"))
new_dict = []
for k, v in new_dict0.iteritems():
    definitions = [v[key]["definition"] for key in v]
    v["english"] = ' | '.join(definitions)
    v["yupik"] = k

    new_dict.append(v)


class Nouns(Resource):
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)

    @cors.crossdomain(origin='*')
    def get(self):
        return jsonify(nouns)


class Verbs(Resource):
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)

    @cors.crossdomain(origin='*')
    def get(self):
        return jsonify(verbs)


class Postbases(Resource):
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)

    @cors.crossdomain(origin='*')
    def get(self):
        return jsonify(postbases)


class Endings(Resource):
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)

    @cors.crossdomain(origin='*')
    def get(self):
        return jsonify(endings)


class Word(Resource):
    @cors.crossdomain(origin='*')
    def get(self, word):
        print(word)
        return jsonify(new_dict0[word])


class WordsList(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        return jsonify(new_dict)


class Concatenator(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        args = parser_api.parse_args()
        word = args['root']
        # FIXME is this conserving the order of parameters?
        print(args['postbase'])
        indexes = [0]
        breakdown = [word]
        for postbase in args['postbase']:
            p = Postbase(postbase)
            new_word = p.concat(word)
            # indexes.append(self.first_index(word, new_word))
            new_word = deconvert(new_word)
            breakdown.append(new_word)
            word = new_word
        for i in range(len(breakdown)-1):
            indexes.append(self.first_index(breakdown[i+1], breakdown[i]))

        word = p.post_apply(word)
        return jsonify({'concat': deconvert(word), 'indexes': indexes})

    def first_index(self, old_word, new_word):
        """
        Returns first index different between both words
        """
        for i in range(min(len(new_word), len(old_word))):
            if old_word[i] != new_word[i]:
                return i
        return i+1
        # If root is special or nrite in postbases list


class TTS(Resource):
    @cors.crossdomain(origin='*')
    def get(self, word):
        parsed_output = parser(word)
        print(parsed_output)
        final_audio = None
        for i, k in enumerate(parsed_output):
            filename = 'assets/audiofiles/'+k+'.wav'
            if not os.path.isfile(filename):
                print("ERROR %s audio file is missing!" % filename)
                return jsonify({})
            a = AudioSegment.from_wav(filename)
            if final_audio is None:
                final_audio = a
            else:
                final_audio = final_audio + a
        final_audio.export('/tmp/test.wav', format='wav')
        return send_file('/tmp/test.wav', mimetype='audio/wav')


api.add_resource(Word, '/word/<string:word>')
api.add_resource(WordsList, '/word/all', '/')

api.add_resource(Nouns, '/noun/all')
api.add_resource(Verbs, '/verb/all')
api.add_resource(Postbases, '/postbase/all')
api.add_resource(Endings, '/ending/all')
api.add_resource(Concatenator, '/concat')
api.add_resource(TTS, '/tts/<string:word>')

if __name__ == '__main__':
    app.run(debug=True)
