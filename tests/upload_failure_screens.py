#!/usr/bin/env python

import os
import sys

from imgurpython import ImgurClient

BASE_PATH = os.path.join(os.path.dirname(__file__), 'tests-output')

if not os.path.exists(BASE_PATH):
    sys.exit(0)

CLIENT_ID = os.environ.get('IMGUR_CLIENT_ID')
CLIENT_SECRET = os.environ.get('IMGUR_CLIENT_SECRET')

client = ImgurClient(CLIENT_ID, CLIENT_SECRET)

for file_name in os.listdir(BASE_PATH):
    if not file_name.endswith('.png'):
        continue

    file_path = os.path.join(BASE_PATH, file_name)

    if os.path.isdir(file_path):
        continue

    r = client.upload_from_path(file_path)
    print "wget -O '%s' '%s'" % (file_name, r['link'])
