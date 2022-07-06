from requests import Session
from typing import Optional

DEFAULT_USER_DATA = {
	'device_type': 'com.crunchyroll.manga.android',
	# Use `random` and `string`?
	"device_id": "63ydixvzubzftvtv",
	'access_token': 'FLpcfZH4CbW4muO',
	'api_ver': '1.0'
}

class CruncyrollError(Exception):
	pass

class CRMangaAPI:
	"""A small implementation of the Cruncyroll Manga API.
	Not including logging stuff for obvious reasons."""
	session: Session
	user_data: dict
	_series_cache: Optional[list] = None

	def __init__(self, session: Session=Session()):
		self.session = session
		self.user_data = dict(DEFAULT_USER_DATA)

	def decrypt_image(self, image: bytes):
		key = ord('B')
		return bytes([x ^ key for x in image])

	def make_request(self, path: str, params: dict = {}, data: dict = {}):
		url = f"https://api-manga.crunchyroll.com/{path}"
		if data:
			res = self.session.post(url, params=params, data={**self.user_data, **data})
		else:
			res = self.session.get(url, params=params)
		try:
			res.raise_for_status()
		except Exception as e:
			raise CruncyrollError(res.text) from e
		
		body = res.json()
		if type(body) == dict and body.get("error") == True:
			raise CruncyrollError(body)
		
		return body

	def list_series(self, content_type: str = "jp_manga", filter: Optional[str] = None, cache: bool = True):
		"""You can't request info on a specific series, so we should cache the response for further use like the app."""
		if self._series_cache and cache:
			return self._series_cache
		else:
			res = self.make_request("list_series", data={"content_type": content_type, "filter": filter,})
			self._series_cache = res
			return res
	
	def list_filters(self):
		return self.make_request("list_filters")

	def login(self, account: str, password: str):
		self.cr_login(account, password)
		self.cr_start_session()
		self.cr_authenticate()

	def cr_login(self, account: str, password: str):
		res = self.make_request("cr_login", data={"account": account, "password": password,})
		auth = res["data"]["auth"]
		self.user_data.update({"auth": auth})
		return res
	
	def cr_start_session(self):
		# Hack to force sending a POST request
		res = self.make_request("cr_start_session", data={"_": None})

		data = res["data"]
		auth = data["auth"]
		croll_manga_sess_id = data.get("croll_manga_sess_id")
		session_id = data.get("session_id")
		self.user_data.update({"auth": auth, "croll_manga_sess_id": croll_manga_sess_id, "session_id": session_id})
		return res

	def cr_authenticate(self):
		res = self.make_request("cr_authenticate", data={"_": None})
		auth = res["data"]["auth"]
		self.user_data.update({"auth": auth})
		return res

	def list_chapters(self, series_id: int):
		# Did include user_data values + user_id in params, but is unnecessary
		return self.make_request("list_chapters", params={"series_id": series_id})

	def list_chapter(self, chapter_id: int):
		return self.make_request("list_chapter", data={"chapter_id": chapter_id})
	
	def favorite(self, content_type: str = "jp_manga", method: str = "get", series_id: Optional[int] = None):
		"""`method` can be get, set or remove."""
		return self.make_request("favorite", data={"content_type": content_type, "method": method, "series_id": series_id})
	
	def bookmark(self, method: str = "get", chapter_id: Optional[int] = None, page_id: Optional[int] = None):
		"""`method` can be get, set or remove."""
		return self.make_request("bookmark", data={"method": method, "chapter_id": chapter_id, "page_id": page_id})
