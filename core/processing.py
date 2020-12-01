import re
from collections import Counter, OrderedDict
import itertools

from sklearn.feature_extraction.text import TfidfVectorizer as tfv
from sklearn.metrics.pairwise import cosine_distances
from sklearn.cluster import DBSCAN, OPTICS

def split(entries, data):
    id_generator = iter(map(str, range(100_000)))

    pattern = pattern or "Документ предоставлен КонсультантПлюс"
    pass

def flag(pattern):
    pass


class OrderedCounter(Counter, OrderedDict):
    'Counter that remembers the order elements are first encountered'


def group(data, min_samples=3, eps=0.07):

    # data = {id:item if len(item) > 10 else '' for id, item in data.items()}
    def tokenizer(sentence):
        words = re.split(r"\W", sentence)
        return [word for word in words
                if not word.isnumeric() and len(word) > 2]

    vectorizer = tfv(tokenizer=tokenizer, max_df=0.6, max_features=5000)
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric="precomputed")
    train_sentences = OrderedCounter(data.values())
    vec_data = vectorizer.fit_transform(train_sentences)

    distance_matrix = cosine_distances(vec_data)
    print('DEBUG: vectorized and shape: %s' % str(vec_data.shape))
    dbscan_labels = dbscan.fit_predict(distance_matrix)
    print('DEBUG: dbscan clustering is done!')

    sentence_labels = {}
    dbscan2squash = {}
    label_gen = itertools.count()
    for sentence, n_samples, dbscan_label in zip(train_sentences,
                                                 train_sentences.values(),
                                                 dbscan_labels):
        if dbscan_label > 0:
            if dbscan_label not in dbscan2squash:
                dbscan2squash[dbscan_label] = next(label_gen)
            sentence_labels[sentence] = dbscan2squash[dbscan_label]

        elif len(sentence) > 10 and n_samples >= min_samples:
            sentence_labels[sentence] = next(label_gen)

        else:
            pass

    print('DEBUG: labels collection is done!')
    return {id: sentence_labels.get(sentence, -1)
            for id, sentence in data.items()}

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
            style['>' + id].sort(key=lambda x: x[3][0] if len(x) > 2 else x)

    return style

def mutelight(entries, style):
    """
    """
    for tag in entries:
        for entrie in entries[tag]:
            id = entrie[0]
            style['>' + id] = [style for style in style['>' + id] if style[2] != tag]

    return style

