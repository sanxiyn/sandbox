import json

sites = {
    'anastasiadate': 'http://www.anastasiadate.com/pages/lady/profile/profilepreview.aspx?LadyID={}',
    'asiandate': 'http://www.asiandate.com/pages/lady/profile/profilepreview.aspx?LadyID={}',
    'behappy2day': 'https://www.behappy2day.com/girls_info.php?i={}',
}

def read(filename):
    result = []
    with open(filename) as f:
        for line in f:
            image = json.loads(line)
            result.append(image)
    return result

def write(images, kind, filename):
    with open(filename, 'w') as f:
        for image in images:
            site, id, image_kind = image['id'].split('-')
            if image_kind != kind:
                continue
            link = sites[site].format(id)
            url = image['url']
            f.write('<a href="{}"><img src="{}"></a>\n'.format(link, url))

import sys
args = sys.argv[1:]
if len(args) != 3:
    print 'Usage: build_html.py input kind output'
    sys.exit()
input, kind, output = args

images = read(input)
write(images, kind, output)
