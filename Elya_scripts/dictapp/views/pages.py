# -*- coding: utf-8 -*-
from django.shortcuts import render
from dictapp.models import DictFile
from dictapp.es import ESClient
import json
import re


def index(request):
    esdb = ESClient()
    if request.GET.get('q'):
        w = request.GET['q']
        hits = esdb.get_by_query({"match": {"entry.content.sense.cit.quote": w}})
        # hits = esdb.search_query(w)
        total = hits['total']
        print(total)
        words = [{'word': headword(i['_source']['entry']), 'content': re.sub('\\b([{}{}]{})\\b'.format(w[0].lower(), w[0].upper(), ''.join(w[1:])), '<span class="w3-text-cyan"><i>\\1</i></span>', content(i['_source']['entry']))} for i in hits['hits']]
        return render(request, 'index.html', {'words': words, 'total': total, 'q': w})
    else:
        return render(request, 'index.html', {'words': []})


def headword(entry):
    if 'content' in entry:
        entry = entry['content']
    if isinstance(entry, list):
        word = [i['form']['orth'] for i in entry if 'form' in i if 'orth' in i['form']]
    else:
        word = [entry['form']['orth']]
    return word[0]


def content(entry):
    if 'content' in entry:
        entry = entry['content']
    if isinstance(entry, list):
        form = [i['form'] for i in entry if 'form' in i]
    else:
        form = [entry['form']['orth']]
    fs = '<br>'.join([read_form(i) for i in form])
    if isinstance(entry, list):
        s = [i['sense'] for i in entry if 'sense' in i]
    else:
        s = [entry['sense']]
    ss = '<br>'.join([read_sense(i) for i in s])
    return fs + '<br>' + ss


def read_form(form):
    res = ''
    if 'orth' in form:
        res += '<b>{}</b>'.format(form['orth'])
    if 'lbl' in form:
        res += '<br>'
        if 'text' in form['lbl']:
            res += form['lbl']['text'] + ' '
        if 'type' in form['lbl']:
            res += '<small>[{}]</small>'.format(form['lbl']['type'])
        res += '<br>'
    if 'usg' in form:
        res += '<br><small>[{}], [{}]</small>'.format(form['usg']['type'], form['usg']['text'])
    return res


def read_sense(s):
    if not isinstance(s, list):
        s = [s]
    res = []
    for v in s:
        if 'cit' in v:
            res.append(v['cit']['quote'])
    return ', '.join(res)



def about(request):
    files = DictFile.objects.all()
    return render(request, 'about.html', {'files': files})

def help(request):
    return render(request, 'help.html')
