# -*- coding:utf-8 -*-

from flask import Flask, send_file
from flask_restful import Resource, Api, reqparse
from flask_restful.utils import cors
import json
import os
import sox
from flask.json import jsonify
from pydub import AudioSegment
from common.parser.parser import Postbase, deconvert, convert
from common.parser.tts_parser_v2 import parser
import urllib
from io import BytesIO
from flask_compress import Compress
#from whitenoise import WhiteNoise
from flask_s3 import FlaskS3, url_for
import hfst
from common.retrieveEndings import moodEndings, demonstratives, personalPronouns
from common.endingRules import endingRules
import resource
import enchant

app = Flask(__name__)
# app.wsgi_app = WhiteNoise(app.wsgi_app)
# app.wsgi_app.add_files('static/')
# app.config['COMPRESS_LEVEL'] = 9
app.config['FLASKS3_BUCKET_NAME'] = 'yugtun-static'
# app.config['FLASKS3_REGION'] = 'DEFAULT'
app.config['FLASKS3_DEBUG'] = True
app.config['FLASKS3_HEADERS'] = {
    'Cache-Control': 'max-age=86400',
}
app.config['FLASKS3_ONLY_MODIFIED'] = True
app.config['FLASKS3_GZIP'] = True
Compress(app)
s3 = FlaskS3(app)
api = Api(app)
api.decorators = [cors.crossdomain(origin='*', automatic_options=False)]
api.methods = ['GET', 'OPTIONS', 'POST', 'PUT']

# Define parser and request args
parser_api = reqparse.RequestParser()
parser_api.add_argument('root', type=str)
parser_api.add_argument('postbase', type=str, action='append')

parser_generator = reqparse.RequestParser()
parser_generator.add_argument('underlying_form', type=unicode)
parser_generator.add_argument('mood', type=str)

english_dict = enchant.Dict("en_US")

# FIXME obsolete
# Takes a list of dict/json objects and add id field
# def index(l):
#     new_l = []
#     for i in range(len(l)):
#         new_x = l[i]
#         new_x['id'] = i
#         new_l.append(new_x)
#     return new_l

nouns = json.load(open("static/root_nouns_upd3-18.json"))
verbs = json.load(open("static/root_verbs_upd3-18.json"))
postbases = json.load(open("static/postbases_upd3-18.json"))
endings = json.load(open("static/endings_upd3-18.json"))
# FIXME index needed only for elasticlunr.js?
# nouns = index(json.load(open("static/root_nouns_upd3-18.json")))
# verbs = index(json.load(open("static/root_verbs_upd3-18.json")))
# postbases = index(json.load(open("static/postbases_upd3-18.json")))
# endings = index(json.load(open("static/endings_upd3-18.json")))
new_dict0 = json.load(open("static/dictionary_draft3_alphabetical_21.json"))
# new_dict = []
new_dict_light = []
for k, v in new_dict0.iteritems():
    definitions = [v[key]["definition"] for key in v]
    v["english"] = ' OR '.join(definitions)
    v["yupik"] = k
    # new_dict.append(v)
    v2 = {"english": v["english"], "yupik": v["yupik"]}
    for key in v:
        if key != "english" and key != "yupik":
            v2[key] = {}
            for key2 in ["properties", "descriptor"]:
                v2[key][key2] = v[key][key2]
    new_dict_light.append(v2)


class Nouns(Resource):
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        # print("Nouns init")

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
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)

    @cors.crossdomain(origin='*')
    def get(self, word):
        #print(word)
        return jsonify(new_dict0[word])


class WordsList(Resource):
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        # print("WordsList init")

    @cors.crossdomain(origin='*')
    def get(self):
        return jsonify(new_dict_light)


class Concatenator(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        args = parser_api.parse_args()
        word = args['root']
        # FIXME is this conserving the order of parameters?
        # print(args['postbase'])
        indexes = [0]
        breakdown = [word]
        word = convert(word)
        for postbase in args['postbase']:
            p = Postbase(postbase)
            new_word = p.concat(word)
            # indexes.append(self.first_index(word, new_word))
            new_word = deconvert(new_word)
            breakdown.append(new_word)
            word = convert(new_word)
        for i in range(len(breakdown)-1):
            indexes.append(self.first_index(breakdown[i+1], breakdown[i]))
        word, removedindex = p.post_apply(word)
        if removedindex != -1:
            for k, values in enumerate(indexes):
                if removedindex < values:
                    indexes[k] -= 1
        return jsonify({'concat': deconvert(word), 'indexes': indexes})

    def first_index(self, new_word, old_word):
        """
        Returns first index different between both words
        """
        for i in range(min(len(new_word), len(old_word))):
            if old_word[i] != new_word[i] or (len(old_word) == i+1 and old_word[-1] == 'r' and 'rpag' in new_word):
                return i
        return i+1
        # If root is special or nrite in postbases list


class TTS(Resource):
    # @cors.crossdomain(origin='*')
    # def get(self, word):
    #     parsed_output = parser(word)
    #     po = range(len(parsed_output))
    #     for i,k in enumerate(parsed_output):
    #         po[i] = 'assets/audiofiles_mp3_all/'+k+'.mp3'
    #         if not os.path.isfile(po[i]):
    #             print("ERROR %s audio file is missing!" % po[i])
    #             return jsonify({'url': ''})
    #     print(po)
    #     cbn = sox.Combiner()
    #     cbn.build(po, '/tmp/test.mp3', 'concatenate')
    #     #return jsonify({'url': 'test.mp3'})
    #     return send_file('/tmp/test.mp3', mimetype='audio/mp3')

    @cors.crossdomain(origin='*')
    def get(self, word):
        parsed_output = parser(word)
        # po = range(len(parsed_output))
        # for i,k in enumerate(parsed_output):
        #     po[i] = 'static/audiofiles_mp3_all/'+k+'.mp3'
        #     if not os.path.isfile(po[i]):
        #         print("ERROR %s audio file is missing!" % po[i])
        #         return jsonify({'url': ''})
        # print(po)
        # cbn = sox.Combiner()
        # cbn.build(po, '/tmp/test.mp3', 'concatenate')
        # #return jsonify({'url': 'test.mp3'})
        # return send_file('/tmp/test.mp3', mimetype='audio/mp3')

        # print(parsed_output)
        final_audio = None
        for i, k in enumerate(parsed_output):
            filename = url_for('static', filename='audiofiles_mp3_all_1/'+k+'.mp3')
            # print(filename)
            mp3 = urllib.urlopen(filename).read()
            # 'https://github.com/Temigo/yuarcuun-api/blob/master/static/audiofiles_mp3_all/'+k+'.mp3'
            # if not os.path.isfile(filename):
            #     print("ERROR %s audio file is missing!" % filename)
            #     return jsonify({})
            a = AudioSegment.from_mp3(BytesIO(mp3))
            if final_audio is None:
                final_audio = a
            else:
                final_audio = final_audio + a
        # FIXME use other filename than test.mp3
        final_audio.export('/tmp/test.mp3', format='mp3')
        return send_file('/tmp/test.mp3', mimetype='audio/mp3')


class Verification(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        return app.send_static_file('verification.txt')


input_stream = hfst.HfstInputStream('./static/esu.ana.hfstol')
transducer_ana = input_stream.read()
input_stream.close()
input_stream2 = hfst.HfstInputStream('./static/esu.seg.gen.hfstol')
transducer_seg_gen = input_stream2.read()
input_stream2.close()


class Parser(Resource):
    def __init__(self, *args, **kwargs):
        super(Parser, self).__init__(*args, **kwargs)

    @cors.crossdomain(origin='*')
    def get(self, word):
        # self.input_stream = hfst.HfstInputStream('./static/esu.ana.hfstol')
        # self.transducer_ana = self.input_stream.read()
        # self.input_stream.close()
        # self.input_stream2 = hfst.HfstInputStream('./static/esu.seg.gen.hfstol')
        # self.transducer_seg_gen = self.input_stream2.read()
        # self.input_stream2.close()
        word_utf8 = word.encode("utf-8")    #convert to bytestring for analyzer lookup
        list_results = transducer_ana.lookup(word_utf8, time_cutoff=10.0)
        parses = [x[0].replace("@%:","@:") for x in list_results]
        # print(parses)

        # parses sort algorithm
        parses.sort(key=len)                                # shortest to longest string length
        parses = [x.split('-') for x in parses]             # split into morphemes
        parses.sort(key=lambda x: len(x[0]), reverse=True)  # longest length of base
        parses.sort(key=len)                                # least number of morphemes
        parses = sorted(parses, key=lambda x: False if "[NonYupik]" not in x[0] else ( False if english_dict.check(x[0].split("[NonYupik]")[0]) else True )) # push non-English [NonYupik] words to the end of the list
        parses = parses[0:10]                               # get top 10
        parses = ['-'.join(x) for x in parses]
        # print(parses)

        # segments that match word
        segments_all = [list(transducer_seg_gen.lookup(x.replace("@:","@%:"))) for x in parses]
        # print(segments_all)
        # print(word.replace("-",""))
        # print(segments[0][0][0].replace(">",""))
        # segments = [x for seg in segments for x,weight in seg if]
        segments = []
        for seg in segments_all:
            seg_out = ""
            if len(seg) == 1:
                seg_out = seg[0][0]
            else:
                for x, weight in seg:
                    # print(str(type(x))+" "+x+"\t"+str(type(word))+" "+word)
                    if x.replace(">","").decode('utf-8').replace(u"\u0361","").replace(u"\u0304","").replace(u"\u035E","") == word.replace(u"\u0361","").replace(u"\u0304","").replace(u"\u035E",""):
                        seg_out = x
                if seg_out == "":
                    seg_out = seg[0][0]
            segments.append(seg_out)
        # print(segments)

        # ending rules
        endings = []
        for parse in parses:
            endRule = [""]
            for index, x in enumerate(parse.split("-")):
                if x in endingRules:
                    endRule = (index, endingRules[x])
            endings.append(endRule)
        # print(endings)

        return jsonify({'parses': parses, 'segments': segments,'endingrule':endings})


class Segmenter(Resource):
    def __init__(self, *args, **kwargs):
        super(Segmenter, self).__init__(*args, **kwargs)
        # self.input_stream = hfst.HfstInputStream('./static/esu.seg.gen.hfstol')
        # self.transducer_ana = self.input_stream.read()
        # self.input_stream.close()

    @cors.crossdomain(origin='*')
    def get(self, form):
        list_results = transducer_seg_gen.lookup(form)
        return jsonify({'words': [x[0] for x in list_results]})


class MoodSegmenter(Resource):
    def __init__(self, *args, **kwargs):
        super(MoodSegmenter, self).__init__(*args, **kwargs)
        # self.input_stream = hfst.HfstInputStream('./static/esu.seg.gen.hfstol')
        # self.transducer_ana = self.input_stream.read()
        # self.input_stream.close()

    @cors.crossdomain(origin='*')
    def get(self):
        args = parser_generator.parse_args()
        #print(args)
        if "[V]" in args['underlying_form']:
            if "@+paa|~vaa[V][XCLM]" in args['underlying_form'] or "@+pag|~vag[V][XCLM]" in args['underlying_form']:
                underlying_form = args['underlying_form'].encode('utf-8').split("@+paa", 1)[0] + "[V]"
            else:
                underlying_form = args['underlying_form'].encode('utf-8').split("[V]", 1)[0] + "[V]"
        elif "[N]" in args['underlying_form']:
            underlying_form = args['underlying_form'].encode('utf-8').split("[N]", 1)[0] + "[N]"
        elif "[Quant_Qual]" in args['underlying_form']:
            underlying_form = args['underlying_form'].encode('utf-8').split("[Quant_Qual]", 1)[0]
        elif "[DemPro]" in args['underlying_form'] or "[DemAdv]" in args['underlying_form']:
            return jsonify({'results': demonstratives})
        elif "[PerPro]" in args['underlying_form']:
            return jsonify({'results': personalPronouns})

        mood = args['mood']
        if mood not in moodEndings:
            raise Exception("Unknown mood %s" % mood)
        underlying_form += mood
        # print("Underlying form = ", underlying_form)
        # Compute all moods
        results = {}
        for ending in moodEndings[mood]:
            list_results = transducer_seg_gen.lookup(underlying_form.replace("@:","@%:") + ending)
            results[ending] = [x[0] for x in list_results]
        return jsonify({'results': results})


api.add_resource(Word, '/word/<string:word>'.encode('utf-8'))
api.add_resource(WordsList, '/word/all', '/')

api.add_resource(Nouns, '/noun/all')
api.add_resource(Verbs, '/verb/all')
api.add_resource(Postbases, '/postbase/all')
api.add_resource(Endings, '/ending/all')
api.add_resource(Concatenator, '/concat')
api.add_resource(TTS, '/tts/<string:word>'.encode('utf-8'))
api.add_resource(Verification, '/loaderio-a0a6b59c23ca05a56ff044a189dd143a')

api.add_resource(Parser, '/parse/<string:word>'.encode('utf-8'))
api.add_resource(Segmenter, '/segment/<string:form>'.encode('utf-8'))
api.add_resource(MoodSegmenter, '/mood')


@app.after_request
def add_header(response):
    response.cache_control.max_age = 86400  # 1 day
    return response


if __name__ == '__main__':
    app.run(debug=False)
