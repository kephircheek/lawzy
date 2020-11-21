import re
import operator
import json

def html_extractor(doc):
    pass

def sorter(struct):
    """return sorted list of sentence-id

    Args:
        struct - struct of doc
    Return:
        list
    """

def txt_extractor(content, split_sentence_pattern):
    id_generator = iter(map(str, range(100_000)))

    styles = {'origin': []}
    data = dict()
    struct = ['origin', []]

    paragraphs = re.split(r'\n[ \n]*(?=[^ \n])', content)
    for par in paragraphs:
        par_id = next(id_generator)
        struct[-1].append([par_id, []])
        styles[par_id] = [['p', {}], ]
        sentences = re.split(split_sentence_pattern, par)
        for sentence in sentences:
            blanklines = re.findall(r'\n+$', sentence)

            id = next(id_generator)
            struct[1][-1][1].append([id, ['>' + id]])
            styles[id] = []
            styles['>' + id] = []
            data[id] = sentence.rstrip('\n')

            if blanklines:
                for blankline in blanklines[0]:
                    id = next(id_generator)
                    struct[1][-1][1].append([id, ['>' + id]])
                    styles[id] = []
                    styles['>' + id] = [['']]
                    data[id] = ''

    return struct, styles, data


################################################################################

def correcting(styles, data):
    if not styles:
        return data

    if styles[-1][0] == '':
        return '<br /><br />'

    elif styles[-1][0] in {'span', 'mark'}:
        start, end = styles[-1][-1]
        data = (correcting(styles[:-1], data[:start]) +
                wrapping([styles[-1]], data[start:end]) + data[end:])
    else:
        pass

    return data


def tag(style):
    return style[0]


def attributes(style):
    attr = ' '.join([f'{k}="{v}"' for k, v in style[1].items()])
    if attr:
        return ' ' + attr
    return ''


def make_wrap(style):
    return ('<' + tag(style) + attributes(style) + '>',
            '</' + tag(style) + '>')

def wrapping(styles, data):
    wrap = list(zip(*map(make_wrap, styles)))
    if wrap:
        return '\n'.join(wrap[0]) + data + '\n'.join(wrap[1][-1::-1])
    else:
        return data

def compiler(struct, style, data,
             out_type='html',
             labels=None,
             mute=None,
             path=None,
             limit=None):
    # print('LABELS:', labels)
    checked_labels = set()

    def html_compiler(node):
        '''
        '''
        mute_style = []
        if isinstance(node, str):
            appendix = ''
            if mute and labels:
                label = labels[node[1:]]
                if label >= 0:
                    appendix = (
                        '<sup class="badge badge-secondary" style="font-size:8px;">'
                        + str(labels[node[1:]])
                        + '</sup>'
                    )
                    if label in checked_labels:
                        mute_style.append(['div', {'style': 'color: #AAAAAA'}])

                    else:
                        checked_labels.add(label)

            return wrapping(
                mute_style,
                correcting(style[node], data[node[1:]]) + appendix
            )

        id, next_nodes = node
        return wrapping(style[id], '\n'.join(map(html_compiler, next_nodes)))

    if out_type == 'html':
        return html_compiler(struct)

    def compile_txt(node):
        if isinstance(node, str):
            sentence = data[node[1:]]
            len_sentence = len(sentence)
            if len_sentence > 80:
                label = '!'
            else:
                label = None
            if labels and labels[node[1:]] >= 0:
                label = str(labels[node[1:]])

                if label in checked_labels:
                    if len(sentence) > limit:
                        sentence = sentence[:limit] + '  <<<<<<<<'
                    else:
                        return None
                else:
                    checked_labels.add(label)

            prefix = '[%s]' % label if label else ""
            return prefix + sentence

        id, next_nodes = node
        return '\n'.join(s for s in map(compile_txt, next_nodes) if s)

    if out_type == 'txt':
        return compile_txt(struct)
