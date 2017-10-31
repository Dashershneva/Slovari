from lxml import etree
from vd.settings import SCHEME_FILE
import traceback
import re

with open(SCHEME_FILE) as xsd:
    xmlschema_doc = etree.parse(xsd)
xmlschema = etree.XMLSchema(xmlschema_doc)


def validate_it(fname):
    is_valid = False
    error = []
    name = ''
    try:
        with open(fname, encoding='utf-8') as valid:
            doc = etree.parse(valid)
        xmlschema.assert_(doc)
        is_valid = xmlschema.validate(doc)
        if is_valid:
            name = doc.getroot()[1][0][0].text
    except Exception as e:
        error = traceback.format_exception_only(type(e), e)
        error = re.sub(r'File "(.*)/(.*?)"', 'File "\\2"', ''.join(error))
    return is_valid, error, name



def serialize_one(element, d):
    if not d:
        if element.text:
            tag_content = element.text.strip()
            if tag_content:
                d[str(element.tag)] = tag_content
        return d
    else:
        if element.text:
            tag_content = element.text.strip()
            if tag_content:
                d['text'] = tag_content
        return {str(element.tag): d}


def serialize(element):
    d = {}
    for k in element.attrib:
        d[str(k)] = str(element.attrib[k])
    if len(element) == 0 and element.tag not in ['ref', 'note']:
        return serialize_one(element, d)
    if element.text:
        tag_content = element.text.strip()
        if tag_content:
            d['text'] = tag_content
    tags = [el.tag for el in element]
    if len(tags) == len(set(tags)) and element.tag != 'sense':
        for el in element:
            d.update(serialize(el))
    else:
        d['content'] = []
        for el in element:
            d['content'].append(serialize(el))
    if len(d) == 1 and 'content' in d:
        return {str(element.tag) : d['content']}
    return {str(element.tag) : d}


def load(fname):
    with open(fname, 'rb') as f:
        root = etree.HTML(f.read())
    d = serialize(root)
    return d