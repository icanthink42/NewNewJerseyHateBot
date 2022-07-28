import os
import random
from typing import List


def contains_nj(text: str) -> bool:
    return "newjersey" in text.lower().replace(" ", "")


def contains_civ_e(text: str) -> bool:
    return "civile" in text.lower().replace(" ", "") or "civil engineering" in text.lower().replace(" ", "")


# Returns the index after "I'm" or "Im", or -1 if not found
def im_index(text: str) -> int:
    # "Im"
    index = text.lower().find("im ")
    if index == 0 or (index > 0 and text[index - 1].isspace()):
        return index + 3
    # "I'm"
    index = text.lower().find("i'm ")
    if index == 0 or (index > 0 and text[index - 1].isspace()):
        return index + 4
    # Not found
    return -1


def random_file(directory: str) -> str:
    file_names: List[str] = os.listdir(directory)
    return f"{directory}/{random.choice(file_names)}"
