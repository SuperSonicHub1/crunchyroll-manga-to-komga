#!/usr/bin/env python
"""
Easily decode and display pages from Crunchyroll Manga
for debugging purposes.
"""

from ..api import CRMangaAPI
from pprint import pprint
# from netrc import netrc
from sys import argv
from PIL import Image
from tempfile import NamedTemporaryFile

page_urk = argv[1]
from os.path import splitext
from mimetypes import guess_extension

# def get_auth(passwords: netrc):
# 	info = passwords.authenticators("crunchyroll.com")
# 	if info:
# 		return info
# 	else:
# 		raise KeyError("Host 'crunchyroll.com' not found.")

# account, _, password = get_auth(netrc())
crunchyroll = CRMangaAPI()
# crunchyroll.login(account, password)
session = crunchyroll.session


page_url = argv[1]
page_res = session.get(page_url)
page_blob = crunchyroll.decrypt_image(page_res.content)

with NamedTemporaryFile(
		suffix=guess_extension(page_res.headers['content-type']) or splitext(page_url)[1] or '.jpg',
		delete=False
	) as f:
	f.write(page_blob)
	with Image.open(f.name) as im:
		im.show()
