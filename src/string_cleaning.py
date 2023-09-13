import re
import string
import unicodedata


def lower_string(s: str):
    return s.lower()


def strip_string(s: str):
    return s.strip()


def keep_separators(s: str):
    separators_list = ["-", "'"]
    sep_str = "".join(separators_list)
    return re.sub(f"[{sep_str}]", " ", s)


def remove_accents(s: str):
    nfkd_form = unicodedata.normalize("NFKD", s)
    string_no_diacritics = nfkd_form.encode("ASCII", "ignore").decode("utf8")
    return string_no_diacritics


def remove_control_characters(s: str):
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")


def remove_punct_control_spaces(s: str):
    s = s.translate(str.maketrans("", "", string.punctuation))
    s = remove_control_characters(s)
    s = re.sub(" +", " ", s)
    return s


def translate_characters(s: str):
    # Translating badly handled characters into ascii characters
    in_char_set = "ø"
    out_char_set = "o"
    translation_list = s.maketrans(in_char_set, out_char_set)
    s = s.translate(translation_list)
    return s


def clean_string(s: str) -> str:
    s = lower_string(s)
    s = strip_string(s)
    s = keep_separators(s)
    s = translate_characters(s)
    s = remove_punct_control_spaces(s)
    s = remove_accents(s)

    return s
