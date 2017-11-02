from dictapp.es import ESClient
from dictapp.views.validate import load

import json


esdb = ESClient()


def add_to_index(fname):
    k = load(fname)
    for el in k['html']['body']['tei']['text']:
        if 'entry' in el:
            el['entry']['dict_name'] = 'Japanese-English Dictionary'
            if 'content' in el['entry']:
                for i in el['entry']['content']:
                    if 'sense' in i:
                        for t in i['sense']:
                            if 'ref' in t:
                                if 'type' not in t['ref']:
                                    t['ref']['type'] = 'syn'
            esdb.create(json.dumps(el))