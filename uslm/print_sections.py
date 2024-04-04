import argparse

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

# See https://uscode.house.gov/download/resources/USLM-User-Guide.pdf
USLM_NS = 'http://xml.house.gov/schemas/uslm/1.0'

def match_ns(ns, tag):
    index = tag.find('}')
    if index == -1:
        return
    tag_ns = tag[1:index]
    name = tag[index+1:]
    if tag_ns != ns:
        return
    return name

def match_uslm(tag):
    return match_ns(USLM_NS, tag)

def print_sections(filename):
    parents = []
    for event, elem in etree.iterparse(filename, events=('start', 'end')):
        if event == 'start':
            parents.append(elem)
        elif event == 'end':
            parents.pop()
            if match_uslm(elem.tag) != 'heading':
                continue
            parent = parents[-1]
            if match_uslm(parent.tag) != 'section':
                continue
            identifier = parent.get('identifier')
            if identifier is None:
                continue
            status = parent.get('status')
            if status in ('renumbered', 'repealed'):
                continue
            print(identifier, elem.text.strip())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    print_sections(args.filename)
