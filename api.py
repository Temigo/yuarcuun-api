from flask import Flask
from flask_restful import Resource, Api
import json

app = Flask(__name__)
api = Api(app)

class Nouns(Resource):
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        self.nouns = json.load(open("assets/root_nouns_upd3-18.json"))

    def get(self):
        return self.nouns

class Verbs(Resource):
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        self.verbs = json.load(open("assets/root_verbs_upd3-18.json"))

    def get(self):
        return self.verbs

class Postbases(Resource):
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        self.postbases = json.load(open("assets/postbases_upd3-18.json"))

    def get(self):
        return self.postbases

class Endings(Resource):
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        self.endings = json.load(open("assets/endings_upd3-18.json"))

    def get(self):
        return self.endings

class Word(Resource):
    def get(self, word):
        print(word)
        return {'english': 'mother', 'yupik': 'aakaq'}

api.add_resource(Word, '/word/<string:word>')
api.add_resource(Nouns, '/noun/all')
api.add_resource(Verbs, '/verb/all')
api.add_resource(Postbases, '/postbase/all')
api.add_resource(Endings, '/ending/all')

if __name__ == '__main__':
    app.run(debug=True)
