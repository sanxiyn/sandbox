import json

sites = {
    'anastasiadate': 'http://www.anastasiadate.com/pages/lady/profile/profilepreview.aspx?LadyID={}',
    'asiandate': 'http://www.asiandate.com/pages/lady/profile/profilepreview.aspx?LadyID={}',
    'charmdate': 'http://www.charmdate.com/photogallery/woman.php?womanid=C{}',
    'behappy2day': 'https://www.behappy2day.com/girls_info.php?i={}',
}

def read(filename):
    result = []
    with open(filename) as f:
        for line in f:
            item = json.loads(line)
            result.append(item)
    return result

def write(items, kind, filename):
    with open(filename, 'w') as f:
        for item in items:
            site, id, item_kind = item['id'].split('-')
            if item_kind != kind:
                continue
            link = sites[site].format(id)
            url = item['url']
            f.write('<a href="{}"><img src="{}"></a>\n'.format(link, url))

import sys
args = sys.argv[1:]
if len(args) != 3:
    print 'Usage: build_html.py input kind output'
    sys.exit()
input, kind, output = args

items = read(input)
write(items, kind, output)
