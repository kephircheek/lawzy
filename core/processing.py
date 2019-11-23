import re

from sklearn.feature_extraction.text import TfidfVectorizer as tfv
from sklearn.cluster import DBSCAN

def split(entries, data):
    id_generator = iter(map(str, range(100_000)))

    pattern = pattern or "Документ предоставлен КонсультантПлюс"
    pass

def flag(pattern):
    pass

def group(data):

    def tokenizer(sentence):
        words = re.split(r"\W", sentence)
        return [word for word in words if not word.isnumeric() and len(word)>2]

    ids, sentences = zip(*data.items())
    vectorizer = tfv(tokenizer=tokenizer, max_df=0.8)
    db = DBSCAN(eps=0.4, min_samples=2, metric="cosine")

    X = vectorizer.fit_transform(sentences)
    db.fit(X)
    return {id: int(label) for id, label in zip(ids, db.labels_)}

def dublicates(labels):
    added = set()
    dubs = dict()
    for id in labels:
        if labels[id] == -1 or labels[id] not in added:
            added.add(labels[id])
            dubs[id] = False
        else:
            dubs[id] = True

    return dubs

def mute(blocks, style):
    for id in blocks:
        style[id].append(['div', {'style': 'color: #AAAAAA'}])

    return style

def unmute(blocks, style):
    for id in blocks:
        style[id] = [s for s in style[id] if s[0] != 'div']

    return style

def search(patterns, data) -> dict:
    '''finds all match of pattern

    Args:
        patterns - list of tag-word
        data - dict like {id:sentence} or list [id, sentence]
    Return:
        dict of entries {pattern: [id, span, match]}
    '''
    if isinstance(data, dict):
        data = data.items()

    united_pattern = '(' + '|'.join(patterns) + ')'

    entries = {pattern: [] for pattern in patterns}
    for id, sentence in data:
        for match in re.finditer(united_pattern, sentence.casefold()):
            tag, span = match.group(0), match.span()
            tag_pattern = [pattern for pattern in patterns if re.search(pattern, tag)][0]
            entries[tag_pattern].append([id, span, tag])

    return entries


def highlight(entries, style, colors=None):
    '''add highlight of tag in style
    '''

    for tag in entries:
        for entrie in entries[tag]:
            id, span, _ = entrie
            style['>' + id].append(['span',
                                    {'style': 'background-color: #FF0000'},
                                    tag,
                                    span])
            style['>' + id].sort()

    return style

def mutelight(entries, style):
    """
    """
    for tag in entries:
        for entrie in entries[tag]:
            id = entrie[0]
            style['>' + id] = [style for style in style['>' + id] if style[2] != tag]

    return style

