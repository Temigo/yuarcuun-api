# *-* encoding: utf-8 *-*

import sys
import json

with open(sys.argv[1], 'r') as f_ypk:
    with open(sys.argv[2], 'r') as f_en:
        lines_ypk = f_ypk.readlines()
        lines_en = f_en.readlines()

assert len(lines_ypk) == len(lines_en)
dictionary = []
for i in range(len(lines_ypk)):
    d = {}
    d['yupik'] = lines_ypk[i].strip()
    d['english'] = lines_en[i].strip()
    dictionary.append(d)

with open(sys.argv[3], 'w') as final:
    json.dump(dictionary, final)
