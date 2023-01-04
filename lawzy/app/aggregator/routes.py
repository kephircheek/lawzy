import collections
import json
import os
from datetime import datetime
from uuid import uuid4

import docx
from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from lawzy import core
from lawzy.app.models import Data, KeywordEntries, Struct, Style
from lawzy.config import UPLOAD_FOLDER

INDENT = 2
# Define the blueprint: 'auth', set its url prefix: app.url/auth
aggregator = Blueprint("aggregator", __name__, url_prefix="/aggregator")

# Set the route and accepted methods
@aggregator.route("/uploader", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":

        token = uuid4()
        session["token"] = str(token)
        session["toggle:reduce"] = False
        session["reduced"] = False
        os.makedirs(f"{UPLOAD_FOLDER}/{token}")

        f = request.files["file"]
        filename, extention = os.path.splitext(os.path.basename(f.filename))
        f.save(f"{UPLOAD_FOLDER}/{token}/source{extention}")

        config = {
            "FILENAME": filename,
            "EXTENTION": extention,
            "DATE_CREATED": str(datetime.now()),
            "SPLIT_SENTENCE_PATTERN": r"(?<=[^( г| N| ном)]\.)\s+(?=[^\Wа-яa-z0-9])",
            "SPLIT_CASE_PATTERN": "Документ предоставлен КонсультантПлюс",
            "CASE_NUMBER_PATTERN": r"(?<=по делу\s)[^\n]+",
        }

        with open(f"{UPLOAD_FOLDER}/{token}/config.json", "w") as f:
            json.dump(config, f, indent=INDENT)

        with open(f'{UPLOAD_FOLDER}/{token}/source{config["EXTENTION"]}', "rb") as f:
            if config["EXTENTION"] == ".docx":
                content = "\n".join(par.text for par in docx.Document(f).paragraphs)
            else:
                content = f.read().decode("utf-8")
            struct, style, data = core.txt_extractor(
                content, config["SPLIT_SENTENCE_PATTERN"]
            )

        Struct(token).post(struct)
        Style(token).post(style)
        Data(token).post({id: [item] for id, item in data.items()})
        KeywordEntries(token).post(dict())

        return redirect(url_for("aggregator.document"))


@aggregator.route("/", methods=["GET", "POST"])
def document():
    if "token" not in session:
        return redirect(url_for("hello"))

    token = session["token"]
    if "toggle:reduce" not in session:
        session["toggle:reduce"] = False

    checked = "checked" if session["toggle:reduce"] else ""

    struct = Struct(token).get()
    style = Style(token).get()
    data = Data(token).sentences
    profit = ""
    if session["toggle:reduce"] == True:
        labels = Data(token).labels
        number_all = len(labels)
        number_of_group = len(set(labels.values())) - 1
        number_non_grouped = len(list(filter(lambda x: x == -1, labels.values())))
        remain = (number_non_grouped + number_of_group) / number_all
        profit = "-%s%%" % round(100 * (1 - remain))

    else:
        labels = None
    keywords = KeywordEntries(token).get().keys()
    content = core.compiler(
        struct, style, data, labels=labels, mute=session["toggle:reduce"], limit=80
    )
    return render_template(
        "aggregator/document.html",
        content=content,
        keywords=keywords,
        checked=checked,
        profit=profit,
        reduced=session["reduced"],
    )


@aggregator.route("/reduce", methods=["GET"])
def reduce():
    token = session["token"]

    if not session["reduced"]:
        labels = core.group(Data(token).sentences)
        Data(token).add(labels)
        dubs = core.dublicates(labels)
        Data(token).add(dubs)
        session["reduced"] = True

    dubs = {id for id, bool in Data(token).dublicates.items() if bool == True}
    session["toggle:reduce"] = not session["toggle:reduce"]

    return redirect(url_for("aggregator.document"))


@aggregator.route("/rating", methods=["GET"])
def rating():

    token = session["token"]
    path = os.path.abspath(f"{UPLOAD_FOLDER}/{token}/rating.txt")

    if not os.path.isfile(path):
        data = Data(token)
        label_counter = collections.Counter(data.labels.values())
        label_counter.pop(-1)
        sentences_by_label = collections.defaultdict(
            lambda: collections.defaultdict(lambda: 0)
        )
        for item in data.get().values():
            sentence = item[0]
            label = item[1]
            sentences_by_label[label][sentence] += 1

        doc = docx.Document()
        for label, freq in label_counter.most_common():
            doc.add_paragraph(
                "Номер группы: %s     Количество предложений: %s" % (label, freq)
            )
            for sentence, freq in sentences_by_label[label].items():
                doc.add_paragraph("(%s) %s" % (freq, sentence))
            doc.add_paragraph("-" * 80)

        doc.save(path)

    return send_file(
        path,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        download_name="rating.docx",
    )


@aggregator.route("/download", methods=["GET"])
def download():
    token = session["token"]
    struct = Struct(token).get()
    style = Style(token).get()
    data = Data(token).sentences
    if session["toggle:reduce"] is True:
        labels = Data(token).labels
    else:
        labels = None
    content = core.compiler(
        struct,
        style,
        data,
        labels=labels,
        mute=session["toggle:reduce"],
        out_type="txt",
        limit=40,
    )

    path = os.path.abspath(f"{UPLOAD_FOLDER}/{token}/result.docx")
    doc = docx.Document()
    for par in content.split("\n"):
        doc.add_paragraph(par)
    doc.save(path)

    with open(f"{UPLOAD_FOLDER}/{token}/config.json") as f:
        config = json.load(f)
    filename = config["FILENAME"]
    return send_file(
        path,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        download_name=f"{filename}.docx",
    )


@aggregator.route("/keywords", methods=["POST"])
def add_keywords():
    token = session["token"]

    new_keywords = {item.strip().casefold() for item in request.form["text"].split(",")}

    keywords = KeywordEntries(token).get()
    data = Data(token).sentences
    style = Style(token).get()

    new_keyword_entries = core.search(new_keywords - keywords.keys(), data)
    style = core.highlight(new_keyword_entries, style)

    Style(token).post(style)
    KeywordEntries(token).add(new_keyword_entries)

    return redirect(url_for("aggregator.document"))


@aggregator.route("/keywords/<string:keyword>", methods=["GET"])
def delete_tag(keyword):
    token = session["token"]

    keyword_entries = {keyword: KeywordEntries(token).pop(keyword)}

    style = Style(token).get()
    style = core.mutelight(keyword_entries, style)

    Style(token).post(style)

    return redirect(url_for("aggregator.document"))
