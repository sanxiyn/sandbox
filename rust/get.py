import StringIO
import tarfile

import requests

api_url = 'https://crates.io/api/v1'

def max_version(crate):
    url = '{}/crates/{}'.format(api_url, crate)
    response = requests.get(url)
    return response.json()['crate']['max_version']

def download(crate, version):
    url = '{}/crates/{}/{}/download'.format(api_url, crate, version)
    response = requests.get(url)
    fileobj = StringIO.StringIO(response.content)
    tar = tarfile.open(fileobj=fileobj)
    tar.extractall()

import sys
args = sys.argv[1:]
if len(args) not in (1, 2):
    print 'Usage: get.py crate [version]'
    sys.exit()

if len(args) == 1:
    crate, = args
    version = max_version(crate)
elif len(args) == 2:
    crate, version = args

download(crate, version)
print '{}-{}'.format(crate, version)
