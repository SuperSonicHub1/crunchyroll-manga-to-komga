"""
https://anansi-project.github.io/docs/comicinfo/schemas/v2.0
https://anansi-project.github.io/docs/comicinfo/schemas/v2.1
https://anansi-project.github.io/docs/comicinfo/documentation

AgeRating is an element, and there are various "rating_*" keys,
but the latter is just a bunch of numbers not even shown in the
UI anyway.
"""

from xml.dom.minidom import getDOMImplementation
from datetime import datetime
from .util import format_chapter_number
from crunchyroll_manga_to_komga import __version__

impl = getDOMImplementation()

def get_impl():
	if impl == None:
		raise Exception("Unable to retrieve DOM implementation.")
	return impl

def get_date(chapter_info: dict):
	try:
		return datetime.fromisoformat(chapter_info["published"])
	# "0000-00-00" -> ValueError: year 0 is out of range
	except ValueError:
		try:
			published = datetime.fromisoformat(chapter_info["updated"])
		except ValueError:
			try:
				return datetime.fromisoformat(chapter_info["availability_start"])
			# Can't be too paranoid
			except:
				return None

def create_comic_info(chapter_info: dict, series_info: dict):
	doc = get_impl().createDocument(None, "ComicInfo", None)
	comic_info = doc.documentElement
	
	def create_element(name, content=None):
		element = doc.createElement(name)
		if content != None:
			text = doc.createTextNode(str(content))
			element.appendChild(text)
		
		return element
	
	chapter_locale = chapter_info["locale"]["enUS"]
	series_locale = series_info["locale"]["enUS"]

	series_name = series_locale["name"]
	comic_info.appendChild(create_element("Title", chapter_locale["name"]))
	comic_info.appendChild(create_element("Series", series_name))

	formatted_chapter_number = format_chapter_number(chapter_info["number"])
	comic_info.appendChild(create_element("Number", formatted_chapter_number))
	# If a series has no volumes, volume_number is set to "0"
	volume_number = chapter_info["volume_number"]
	if volume_number != "0":
		comic_info.appendChild(create_element("Volume", chapter_info["volume_number"]))
		# Use SeriesGroup to group by volume
		# https://komga.org/guides/scan-analysis-refresh.html#import-metadata-for-cbr-cbz-containing-a-comicinfo-xml-file
		comic_info.appendChild(create_element("SeriesGroup", f"{series_name} Volume {chapter_info['volume_number']}"))


	description = chapter_locale["description"]
	if description:
		comic_info.appendChild(create_element("Summary", description))
	
	comic_info.appendChild(create_element("Notes", f"crunchyroll-manga-to-komga/v{__version__}"))

	date = get_date(chapter_info)
	if date != None:
		comic_info.appendChild(create_element("Year", date.year))
		comic_info.appendChild(create_element("Month", date.month))
		comic_info.appendChild(create_element("Day", date.day))

	authors = series_info["authors"] or series_info.get("artist")
	if authors:
		comic_info.appendChild(create_element("Writer", authors))
	letterer = series_info["letterer"]
	if letterer:
		comic_info.appendChild(create_element("Letterer", letterer))
	editor = series_info["editor"]
	if editor:
		comic_info.appendChild(create_element("Editor", editor))
	translator = series_info["translator"]
	if translator:
		comic_info.appendChild(create_element("Translator", translator))
	comic_info.appendChild(create_element("Publisher", series_info["name"]))
	
	genres = series_info["genres"]
	if genres:
		comic_info.appendChild(create_element("Genre", ",".join(genres)))

	url = f"https://www.crunchyroll.com/manga{series_info['url']}/read/{formatted_chapter_number}"
	comic_info.appendChild(create_element("Web", url))

	comic_info.appendChild(create_element("LanguageISO", "en"))

	comic_info.appendChild(create_element("Manga", "YesAndRightToLeft" if chapter_info["reading_direction"] == "right_to_left" else "Yes"))

	return doc.toxml()

if __name__ == "__main__":
	chapter_info = {
				"chapter_id": "19674",
				"number": "58.00",
				"volume_id": "2182",
				"volume_number": "0",
				"credits": "0",
				"published": "0000-00-00",
				"availability_start": "2022-05-24 17:00:00",
				"updated": "0000-00-00 00:00:00",
				"series_id": "556",
				"disable_whole_image": False,
				"locale": {
					"enUS": {
						"name": "Chapter 58",
						"description": ""
					}
				},
				"reading_direction": "right_to_left",
				"viewable": False,
				"is_new": False
			}

	series_info = {
			"series_id": "556",
			"group_id": "0",
			"joint_promo_id": "0",
			"more_info_id": "0",
			"publisher_slug": "square-enix",
			"name": "Square Enix",
			"published": "0000-00-00",
			"url": "/the-strongest-sage-with-the-weakest-crest",
			"created": "2022-05-12 02:16:28",
			"paid_content": True,
			"total_chapters": 0,
			"content_type": "1",
			"rating_sex": "0",
			"rating_violence": "0",
			"rating_crime": "0",
			"rating_language": "0",
			"genres": [
				"action",
				"comedy",
				"fantasy",
				"jp_manga",
				"shonen"
			],
			"authors": "",
			"translator": "Caleb Cook",
			"editor": "Thalia Sutton",
			"letterer": "Kaitlyn Wiley",
			"new_chapter": False,
			"featured": False,
			"locale": {
				"enUS": {
					"name": "The Strongest Sage With the Weakest Crest",
					"description": None,
					"copyright": None,
					"full_image_url": "https://api-manga.crunchyroll.com/i/croll_manga/ffd65388973529545029d438b19480e6_1653365447_full_3842222493ab7965eac25f63c3d4cd4f.jpg",
					"thumb_url": "https://api-manga.crunchyroll.com/i/croll_manga/ffd65388973529545029d438b19480e6_1653365447_large.jpg",
					"landscape_image_url": "https://api-manga.crunchyroll.com/i/croll_manga/dd16130222bf6237832020248a5d9409_1653365447_landscape_3842222493ab7965eac25f63c3d4cd4f.jpg"
				}
			}
		}

	print(create_comic_info(chapter_info, series_info))
