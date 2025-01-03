import itertools
import re
from collections import Counter, OrderedDict
from typing import Union, Dict, List, Tuple

from sklearn.cluster import DBSCAN, OPTICS
from sklearn.feature_extraction.text import TfidfVectorizer as tfv
from sklearn.metrics.pairwise import cosine_distances

from . import style


def split(entries, data):
    id_generator = iter(map(str, range(100_000)))

    pattern = pattern or "Документ предоставлен КонсультантПлюс"
    pass


def flag(pattern):
    pass


class OrderedCounter(Counter, OrderedDict):
    "Counter that remembers the order elements are first encountered"


def group(data, min_samples=3, eps=0.07):
    # data = {id:item if len(item) > 10 else '' for id, item in data.items()}
    def tokenizer(sentence):
        words = re.split(r"\W", sentence)
        return [word for word in words if not word.isnumeric() and len(word) > 2]

    vectorizer = tfv(tokenizer=tokenizer, max_df=0.6, max_features=5000)
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric="precomputed")
    train_sentences = OrderedCounter(data.values())
    vec_data = vectorizer.fit_transform(train_sentences)

    distance_matrix = cosine_distances(vec_data)
    print("DEBUG: vectorized and shape: %s" % str(vec_data.shape))
    dbscan_labels = dbscan.fit_predict(distance_matrix)
    print("DEBUG: dbscan clustering is done!")

    sentence_labels = {}
    dbscan2squash = {}
    label_gen = itertools.count()
    for sentence, n_samples, dbscan_label in zip(
        train_sentences, train_sentences.values(), dbscan_labels
    ):
        if dbscan_label > 0:
            if dbscan_label not in dbscan2squash:
                dbscan2squash[dbscan_label] = next(label_gen)
            sentence_labels[sentence] = dbscan2squash[dbscan_label]

        elif len(sentence) > 10 and n_samples >= min_samples:
            sentence_labels[sentence] = next(label_gen)

        else:
            pass

    print("DEBUG: labels collection is done!")
    return {id: sentence_labels.get(sentence, -1) for id, sentence in data.items()}


def duplicates(labels):
    added = set()
    dubs = dict()
    for id in labels:
        if labels[id] == -1 or labels[id] not in added:
            added.add(labels[id])
            dubs[id] = False
        else:
            dubs[id] = True

    return dubs


def mute(blocks, styles):
    for id in blocks:
        styles[id].append(["div", {"style": "color: #AAAAAA"}])

    return styles


def unmute(blocks, styles):
    for id in blocks:
        styles[id] = [s for s in styles[id] if s[0] != "div"]

    return styles


def search(patterns, data) -> dict:
    """finds all match of pattern

    Args:
        patterns - list of tag-word
        data - dict like {id:sentence} or list [id, sentence]
    Return:
        dict of entries {pattern: [id, span, match]}
    """
    if isinstance(data, dict):
        data = data.items()

    united_pattern = "(" + "|".join(patterns) + ")"

    entries: dict[str, list] = {pattern: [] for pattern in patterns}
    for id, sentence in data:
        for match in re.finditer(united_pattern, sentence.casefold()):
            tag, span = match.group(0), match.span()
            tag_pattern = [pattern for pattern in patterns if re.search(pattern, tag)][0]
            entries[tag_pattern].append([id, span, tag])

    return entries


def highlight(entries, styles, stylist):
    """add highlight of tag in style"""

    for tag in entries:
        for entrie in entries[tag]:
            sentence_id, span, _ = entrie
            in_sentence_id = f">{sentence_id}"
            styles[in_sentence_id].append(
                style.Highlight(stylist, start=span[0], end=span[1], label=tag)
            )
            par_id, _ = sentence_id.split("s")
            styles[par_id] = [
                s
                for s in styles[par_id]
                if not (
                    isinstance(s, style.Hide)
                    and (True if stylist is None else s.stylist == stylist)
                )
            ]

    return styles


def mutelight(entries, styles, stylist, hide_not_matched=False):
    """ """
    for tag in entries:
        for entrie in entries[tag]:
            sentence_id = entrie[0]
            in_sentence_id = f">{sentence_id}"
            styles[in_sentence_id] = [
                s
                for s in styles[in_sentence_id]
                if not isinstance(s, style.Highlight) or s.label != tag
            ]
            if hide_not_matched:
                par_id, _ = sentence_id.split("s")
                styles[par_id].append(style.Hide(stylist))

    return styles


def hide(styles, node_ids, stylist):
    for node_id in node_ids:
        styles[node_id].append(style.Hide(stylist))

    return styles


def unhide(styles, stylist=None):
    for node_id in styles:
        styles[node_id] = [
            s
            for s in styles[node_id]
            if not (
                isinstance(s, style.Hide)
                and (True if stylist is None else s.stylist == stylist)
            )
        ]
    return styles


def stylize_duplicates(styles, labels, limit=None):
    """Stylize duplicates"""
    stylist = style.Stylist.REDUCER
    labels_counter = Counter(labels.values())

    def id_as_tuple(id_str):
        return tuple(map(int, re.findall(r"\d+", id_str)))

    labels = sorted(list(labels.items()), key=lambda x: id_as_tuple(x[0]))
    labels_occurrene = {label: 0 for label in labels_counter}
    for sentence_id, label in labels:
        if label < 0:
            styles[sentence_id].append(style.Exclusive(stylist))
            continue

        label_occurrene = labels_occurrene[label]
        label_count = labels_counter[label]
        styles[sentence_id].append(
            style.Repetition(stylist, label=label, i=label_occurrene, n=label_count)
        )

        if label_occurrene >= limit:
            styles[sentence_id].append(style.Hide(stylist))

        elif label_occurrene > 0:
            styles[sentence_id].append(style.FontColor(stylist, style.Color.GRAY))

        labels_occurrene[label] += 1

    return styles


def remove_reducer_styles(styles):
    """Remove styles of REDUCER stylist."""
    return {
        id: s_
        for id, styles_ in styles.items()
        if len(s_ := [s for s in styles_ if s.stylist != style.Stylist.REDUCER]) > 0
    }
