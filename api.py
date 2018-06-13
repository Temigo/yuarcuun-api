from flask import Flask, send_file
from flask_restful import Resource, Api, reqparse
from flask_restful.utils import cors
import json, sox, os
from flask.json import jsonify

from common.parser.parser import Postbase
from common.tts.tts_parser import parser

app = Flask(__name__)
api = Api(app)
api.decorators=[cors.crossdomain(origin='*', automatic_options=False)]
api.methods = ['GET', 'OPTIONS', 'POST', 'PUT']


# Define parser and request args
parser_api = reqparse.RequestParser()
parser_api.add_argument('root', type=str)
parser_api.add_argument('postbase', type=str)

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
        return {'english': 'mother', 'yupik': 'aakaq'}

class Concatenator(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        args = parser_api.parse_args()
        p = Postbase(args['postbase'])
        return jsonify({'concat': p.concat(args['root'])})

class TTS(Resource):
    @cors.crossdomain(origin='*')
    def get(self, word):
        parsed_output = parser(word)
        po = range(len(parsed_output))
        for i,k in enumerate(parsed_output):
            po[i] = 'assets/audiofiles/'+k+'.wav'
            if not os.path.isfile(po[i]):
                print("ERROR %s audio file is missing!" % po[i])
                return jsonify({'url': ''})
        print(po)
        cbn = sox.Combiner()
        cbn.build(po, 'temp/test.wav', 'concatenate')
        #return jsonify({'url': 'test.wav'})
        return send_file('temp/test.wav', mimetype='audio/wav')


api.add_resource(Word, '/word/<string:word>')
api.add_resource(Nouns, '/noun/all')
api.add_resource(Verbs, '/verb/all')
api.add_resource(Postbases, '/postbase/all')
api.add_resource(Endings, '/ending/all')
api.add_resource(Concatenator, '/concat')
api.add_resource(TTS, '/tts/<string:word>')

if __name__ == '__main__':
    app.run(debug=True)
