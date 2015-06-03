import json

with open('items.json') as f:
    items = json.load(f)

d = {}
for item in items:
    url = item['url']
    language = item['language']
    title = item['title']
    if url not in d:
        d[url] = {}
    d[url][language] = title

for url in sorted(d):
    print url
    for language in sorted(d[url]):
        title = d[url][language]
        title = title.encode('utf-8')
        print language, title
    print
