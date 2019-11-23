from flask import Blueprint, render_template, session, redirect, url_for, request
from uuid import uuid4
from datetime import datetime
import json
from app.models import Struct, Style, KeywordEntries, Data
import core
import os

INDENT = 2
# Define the blueprint: 'auth', set its url prefix: app.url/auth
aggregator = Blueprint('aggregator', __name__, url_prefix='/aggregator')

# Set the route and accepted methods
@aggregator.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        token = uuid4()
        session['token'] = str(token)
        session['toggle:reduce'] = False
        session['reduced'] = False
        os.makedirs(f'app/storage/{token}')

        f = request.files['file']
        _, extention = os.path.splitext(os.path.basename(f.filename))
        f.save(f'app/storage/{token}/source{extention}')

        config =\
            {
                'EXTENTION': extention,
                'DATE_CREATED': str(datetime.now()),
                'SPLIT_SENTENCE_PATTERN': r"(?<=[^( г| N| ном)]\.)\s+(?=[^\Wа-яa-z0-9])",
                'SPLIT_CASE_PATTERN': "Документ предоставлен КонсультантПлюс",
                'CASE_NUMBER_PATTERN': r"(?<=по делу\s)[^\n]+",
            }

        with open(f'app/storage/{token}/config.json', 'w') as f:
            json.dump(config, f, indent=INDENT)

        with open(f'app/storage/{token}/source{config["EXTENTION"]}') as f:
            struct, style, data = core.txt_extractor(f.read(),
                                                     config['SPLIT_SENTENCE_PATTERN'])

        Struct(token).post(struct)
        Style(token).post(style)
        Data(token).post({id: [item] for id, item in data.items()})
        KeywordEntries(token).post(dict())


        return redirect(url_for('aggregator.document'))


@aggregator.route('/', methods=['GET', 'POST'])
def document():
    if 'token' not in session:
        return redirect(url_for('hello'))

    token = session['token']
    if 'toggle:reduce' not in session:
        session['toggle:reduce'] = False

    checked = 'checked' if session['toggle:reduce'] else ''

    struct = Struct(token).get()
    style = Style(token).get()
    data = Data(token).sentences
    keywords = KeywordEntries(token).get().keys()
    content = core.compiler(struct, style, data)
    return render_template("aggregator/document.html",
                           content=content,
                           keywords=keywords,
                           checked=checked)

@aggregator.route('/reduce', methods = ['GET'])
def reduce():
    token = session['token']

    if not session['reduced']:
        labels = core.group(Data(token).sentences)
        Data(token).add(labels)
        dubs = core.dublicates(labels)
        Data(token).add(dubs)
        session['reduced'] = True

    dubs = {id for id, bool in Data(token).dublicates.items() if bool == True}
    print(dubs)
    if session['toggle:reduce']:
        style = core.unmute(dubs,
                            Style(token).get())

    else:
        style = core.mute(dubs,
                          Style(token).get())


    Style(token).post(style)

    session['toggle:reduce'] = not session['toggle:reduce']

    return redirect(url_for('aggregator.document'))

@aggregator.route('/keywords', methods = ['POST'])
def add_keywords():
    token = session['token']

    new_keywords = {item.strip() for item in request.form['text'].split(',')}


    keywords = KeywordEntries(token).get()
    data = Data(token).sentences
    style =  Style(token).get()

    new_keyword_entries = core.search(new_keywords - keywords.keys(), data)
    style =  core.highlight(new_keyword_entries, style)

    Style(token).post(style)
    KeywordEntries(token).add(new_keyword_entries)

    return redirect(url_for('aggregator.document'))


@aggregator.route('/keywords/<string:keyword>', methods = ['GET'])
def delete_tag(keyword):
    token = session['token']

    keyword_entries = {keyword: KeywordEntries(token).pop(keyword)}

    style = Style(token).get()
    style = core.mutelight(keyword_entries, style)

    Style(token).post(style)

    return redirect(url_for('aggregator.document'))



