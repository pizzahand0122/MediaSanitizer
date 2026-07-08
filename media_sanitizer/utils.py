LANGUAGE_NAMES = {
    "eng": "English",
    "jpn": "Japanese",
    "rus": "Russian",
    "spa": "Spanish",
    "fre": "French",
    "fra": "French",
    "ger": "German",
    "deu": "German",
    "ita": "Italian",
    "por": "Portuguese",
    "und": "Unknown",
}


def language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code.lower(), code.upper())