import json

with open('items.json') as f:
    items = json.load(f)

for item in items:
    print '{}\n{}\n'.format(
        item['title'],
        item['description'])
