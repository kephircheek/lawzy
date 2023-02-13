import collections
import itertools
import re

from . import style
from .config import PATTERN_SENTENCE_SPLIT


def parse_txt(content, split_sentence_pattern):
    """
    Extract structure, style and data from text document.
    Double new line expected as a paragraph separator.
    """
    styles = collections.defaultdict(list)
    data = dict()
    struct = ["origin", []]

    # paragraphs = content.split("\n\n")
    paragraphs = re.split("\n[ \t\r\f\v]*\n", content)
    par_offset = 0
    par_counter = itertools.count()
    for par in paragraphs:
        if par.strip() == "":
            par_offset += 1
            continue

        par_number = next(par_counter)
        par_id = f"p{par_number}"
        struct[-1].append([par_id, []])

        if re.search(r"^[ \t\r\f\v]*\n", par):
            par_offset += 1

        styles[par_id].append(style.MarginTop(par_offset))

        if par_number == 0:
            styles[par_id].append(style.FirstParagraph())

        if re.search(r"\n[ \t\r\f\v]*$", par):
            styles[par_id].append(style.FinalNewline())

        sentences = re.split(split_sentence_pattern, par.strip())
        for sentence_i, sentence in enumerate(sentences):
            sentence_id = f"{par_id}s{sentence_i}"
            struct[1][-1][1].append([sentence_id, [">" + sentence_id]])
            if sentence_i == 0:
                indent = re.search(r"^\s+", sentence)
                indent_len = abs(int.__sub__(*indent.span())) if indent is not None else 0
                styles[sentence_id].append(style.ParagraphIndent(indent_len))

            data[sentence_id] = sentence.strip().replace("\n", " ")

        par_offset = 0

    return struct, styles, data


def parse_docx(doc, pattern_split_sentence):
    text = "\n\n".join(par.text for par in doc.paragraphs)
    return parse_txt(text, pattern_split_sentence)
