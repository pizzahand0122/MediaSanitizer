LANGUAGE_NAMES = {
    "eng": "English",
    "spa": "Spanish",
    "jpn": "Japanese",
    "fre": "French",
    "fra": "French",
    "ger": "German",
    "deu": "German",
    "ita": "Italian",
    "por": "Portuguese",
    "rus": "Russian",
    "kor": "Korean",
    "chi": "Chinese",
    "zho": "Chinese",
    "und": "Unknown",
}


def language_name(code: str) -> str:
    """Convert an ISO language code into a friendly name."""
    return LANGUAGE_NAMES.get(code.lower(), code)