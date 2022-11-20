from mimetypes import guess_extension
from netrc import netrc
from os.path import splitext
from pathlib import Path
from sys import argv
from time import sleep
from traceback import print_exception
from typing import Optional
from zipfile import ZipFile
from pathvalidate import sanitize_filename
from requests import Response
from .api import CRMangaAPI, CruncyrollError
from .comic_info import create_comic_info
from .util import format_chapter_number

def get_auth(passwords: netrc):
	info = passwords.authenticators("crunchyroll.com")
	if info:
		return info
	else:
		raise KeyError("Host 'crunchyroll.com' not found.")

account, _, password = get_auth(netrc())
crunchyroll = CRMangaAPI()
crunchyroll.login(account, password)
session = crunchyroll.session

def get_image(page: dict) -> Optional[Response]:
	"""Downloading images is suprisingly complex.
	This function helps encapsulate the necessary logic for attempting to
	download in image in various ways."""

	# Why?!
	if page['locale'] != []:
		page_locale = page["locale"]["enUS"]

		try:
			page_res = session.get(page_locale.get("encrypted_mobile_image_url"))
			page_res.raise_for_status()
			return page_res
		except:
			print('==', 'page_locale.get("encrypted_mobile_image_url") failed')

	try:
		page_res = session.get(page.get('image_url'))
		page_res.raise_for_status()
		return page_res
	except:
		print('==', 'page.get("image_url") failed')

	return None


base = Path(argv[1]) if len(argv) >= 2 else Path.home() / "Documents" / "Crunchyroll"
base.mkdir(parents=True, exist_ok=True)

for series_info in crunchyroll.list_series():
	series_locale = series_info["locale"]["enUS"]
	series_name = series_locale["name"]

	print(f"Downloading series {series_name!r}.")

	series_folder = base / sanitize_filename(series_name)
	series_folder.mkdir(parents=True, exist_ok=True)

	chapters = crunchyroll.list_chapters(series_info["series_id"])
	chapter_infos = chapters["chapters"]

	# + 1 is for the cover
	# NOTE: Assumes everything downloaded successfully
	if len(tuple(series_folder.iterdir())) == len(chapter_infos) + 1:
		print(f"Series already downloaded.")
		continue


	print("=", "Downloading cover.")
	# Cover art
	# https://komga.org/guides/local-artwork-assets.html#poster-artwork
	cover = series_folder / "cover.jpg"

	if not cover.exists():
		# If this has taught me one thing, it's that Crunchyroll Manga
		# is a horribly engineered piece of software.
		# Why do *covers* give 404s!?
		try:
			cover_res = session.get(series_locale["full_image_url"])
			cover_res.raise_for_status()
		except:
			cover_res = session.get(series_locale["thumb_url"])
			cover_res.raise_for_status()
		cover.touch()
		cover.write_bytes(cover_res.content)
		print("=", "Cover downloaded.")
	else:
		print("=", "Cover already downloaded.")

	for chapter_info in chapter_infos:
		chapter_locale = chapter_info["locale"]["enUS"]
		chapter_name = chapter_locale["name"]
		chapter_number = chapter_info["number"]
		chapter_number_formatted = format_chapter_number(chapter_number)

		print("=", f"Downloading chapter {chapter_name!r}.")
		
		chapter_file = series_folder / f"{chapter_number_formatted.zfill(5)} - {sanitize_filename(chapter_name)}.cbz"
		
		# Avoid redownloading chapters
		# NOTE: Somewhat naively assumes that nothing went wrong
		# dowmloading a chapter
		if chapter_file.exists() and chapter_file.stat().st_size > 0:
			print("=", f"Chapter already downloaded.")
			continue

		chapter_file.touch()
		chapter = crunchyroll.list_chapter(chapter_info["chapter_id"])

		with ZipFile(chapter_file, 'w') as archive:
			print("==", f"Writing metadata.")
			archive.writestr(f"ComicInfo.xml", create_comic_info(chapter_info, series_info))
			print("==", f"Metadata written.")

			# TODO: If download fails in middle of chapter,
			# either delete archive or implement page resumption
			for page in chapter["pages"]:
				page_number = page['number']

				print("==", f"Downloading and writing page {page_number}.")
				
				page_res = get_image(page)

				if page_res == None:
					print("!!", f"Page {page_number} could not be found.")
					print("!!", page)
					continue

				page_blob = crunchyroll.decrypt_image(page_res.content)
				archive.writestr(f"{page_number.zfill(5)}{guess_extension(page_res.headers['content-type']) or splitext(page_res.url)[1] or '.jpg'}", page_blob)
				print("==", f"Page written.")
		# Avoid 'bad_request' errors due to logging in too much?
		sleep(2)
		print("=", "Chapter downloaded.")
	print(f"Series downloaded.")
