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

def download_all(path):
    f = open(path)
    for line in f:
        args = line.split()
        if len(args) == 1:
            crate, = args
            version = max_version(crate)
        elif len(args) == 2:
            crate, version = args
        download(crate, version)
        print '{}-{}'.format(crate, version)
    f.close()

import sys
args = sys.argv[1:]
if len(args) != 1:
    print 'Usage: get.py crates'
    sys.exit()
path, = args

download_all(path)
