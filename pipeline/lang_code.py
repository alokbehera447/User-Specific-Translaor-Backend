def nllb_to_whisper_lang_code(nllb_code: str) -> str | None:
    """
    Converts an NLLB 3-letter ISO 639-3 language code (e.g., 'ben') to a
    Whisper-compatible 2-letter ISO 639-1 language code (e.g., 'bn').

    Args:
        nllb_code (str): ISO 639-3 language code used by NLLB.

    Returns:
        str: Whisper-compatible 2-letter language code, or None if not found.
    """
    nllb_to_whisper_map = {
        "afr": "af", "amh": "am", "arb": "ar", "asm": "as", "azj": "az",
        "bel": "be", "bul": "bg", "ben": "bn", "bod": "bo", "bre": "br",
        "bos": "bs", "cat": "ca", "ces": "cs", "cym": "cy", "dan": "da",
        "deu": "de", "ell": "el", "eng": "en", "spa": "es", "est": "et",
        "eus": "eu", "pes": "fa", "fin": "fi", "fao": "fo", "fra": "fr",
        "glg": "gl", "guj": "gu", "hau": "ha", "heb": "he", "hin": "hi",
        "hrv": "hr", "hat": "ht", "hun": "hu", "hye": "hy", "ind": "id",
        "isl": "is", "ita": "it", "jpn": "ja", "jav": "jw", "kat": "ka",
        "kaz": "kk", "khm": "km", "kan": "kn", "kor": "ko", "lao": "lo",
        "lit": "lt", "lav": "lv", "mkd": "mk", "mal": "ml", "mon": "mn",
        "mar": "mr", "msa": "ms", "mya": "my", "nep": "ne", "nld": "nl",
        "nor": "no", "oci": "oc", "pan": "pa", "pol": "pl", "por": "pt",
        "ron": "ro", "rus": "ru", "srp": "sr", "slk": "sk", "slv": "sl",
        "swe": "sv", "swh": "sw", "tam": "ta", "tel": "te", "tha": "th",
        "tgl": "tl", "tur": "tr", "ukr": "uk", "urd": "ur", "vie": "vi"
    }

    return nllb_to_whisper_map.get(nllb_code)
