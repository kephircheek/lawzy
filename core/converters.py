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

    paragraphs = re.split(r'\n[ \n](?=[^\n])', content)
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

def compiler(struct, style, data, out_type='html'):

    def html_compiler(node):
        '''
        '''
        if isinstance(node, str):
            return correcting(style[node], data[node[1:]])

        id, next_nodes = node
        return wrapping(style[id], '\n'.join(map(html_compiler, next_nodes)))

    return html_compiler(struct)


