import argparse
import asyncio
import json

import aiohttp
from tqdm import tqdm

# https://github.com/HackerNews/API
api_url = 'https://hacker-news.firebaseio.com/v0'

async def get_item(session, item):
    url = f'{api_url}/item/{item}.json'
    async with session.get(url) as response:
        item = await response.json()
        return item

async def get_items(session, user):
    url = f'{api_url}/user/{user}.json'
    async with session.get(url) as response:
        user = await response.json()
        return user['submitted']

async def main(user):
    with open('items.json', 'w') as f:
        async with aiohttp.ClientSession() as session:
            items = await get_items(session, user)
            aws = [get_item(session, item) for item in items]
            aws_as_completed = asyncio.as_completed(aws)
            progress = tqdm(aws_as_completed, total=len(items))
            for aw in progress:
                item = await aw
                s = json.dumps(item)
                print(s, file=f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('user', metavar='ID')
    args = parser.parse_args()
    user = args.user
    asyncio.run(main(user))
