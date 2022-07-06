def format_chapter_number(number: str):
	floating = float(number)
	integer = int(floating)
	if integer == floating:
		return str(integer)
	else:
		return str(floating)
