import collections

from . import style


def correcting(styles, data):
    if not styles:
        return data

    elif isinstance(s := styles[-1], style.InPlaceStyle):
        data = (
            correcting(styles[:-1], data[: s.start])
            + wrapping([styles[-1]], data[s.start : s.end])
            + data[s.end :]
        )

    return data


def tag(s):
    return s[0]


def attributes(s):
    attr = " ".join([f'{k}="{v}"' for k, v in s[1].items()])
    if attr:
        return " " + attr
    return ""


def make_wrap(s):
    if not isinstance(s, style.Style):
        return ("<" + tag(s) + attributes(s) + ">", "</" + tag(s) + ">")

    if isinstance(s, style.MarginTop):
        return f'<div style="margin-top: {s.lines}em;">', "</div>"

    if isinstance(s, style.Highlight):
        return f'<span style="background-color: {s.color}">', "</span>"

    if isinstance(s, style.Hide):
        return f'<div style="display: none">', "</div>"

    return "", ""


def wrapping(styles, data):
    wrap = list(zip(*map(make_wrap, styles)))
    if len(wrap) > 0:
        return "\n".join(wrap[0]) + data + "\n".join(wrap[1][-1::-1])
    else:
        return data


def is_paragraph_id(id):
    return id != "origin" and len(id.split("s")) == 1 and len(id.split("p")) == 2


def assemble(
    struct, styles, data, out_type="html", labels=None, mute=None, path=None, limit=None
):
    # print('LABELS:', labels)
    checked_labels = dict()
    if labels:
        labels_counter = collections.Counter(labels.values())

    def html_compiler(node):
        """ """
        mute_style = []
        if isinstance(node, str):
            appendix = ""
            if mute and labels:
                label = labels[node[1:]]
                sentence_id = "sentence:%s" % label
                if label >= 0:
                    n_entrie = checked_labels.get(label, 0)
                    checked_labels[label] = n_entrie + 1
                    appendix = (
                        '<sup class="badge badge-secondary" style="font-size:8px;">'
                        + str(labels[node[1:]])
                        + ("(%s:%s)" % (str(n_entrie + 1), str(labels_counter[label])))
                        + "</sup>"
                    )
                    if n_entrie > 20:
                        return (
                            wrapping([["a", {"href": "#%s" % sentence_id}]], "[...]")
                            + appendix
                        )

                    elif n_entrie > 0:
                        text = data[node[1:]][:limit] + "..."
                        return (
                            wrapping([["a", {"href": "#%s" % sentence_id}]], text)
                            + appendix
                        )

                    else:
                        mute_style.append(["div", {"id": sentence_id}])

            return wrapping(
                mute_style, correcting(styles.get(node, []), data[node[1:]]) + appendix
            )

        id, next_nodes = node

        if is_paragraph_id(id):
            return (
                "<p>"
                + wrapping(styles.get(id, []), " ".join(map(html_compiler, next_nodes)))
                + "</p>"
            )
        return wrapping(styles.get(id, []), "\n".join(map(html_compiler, next_nodes)))

    if out_type == "html":
        return html_compiler(struct)

    def compile_txt(node):
        node_id, subnodes = node

        if len(subnodes) == 1 and isinstance(leaf := subnodes[0], str):
            leaf_id = leaf[1:]
            indent = " "
            end = ""
            prefix = ""
            sentence = data[leaf_id]
            sentence_len = len(sentence)

            if mute and labels is not None:
                if labels and labels[leaf_id] >= 0:

                    label = labels[leaf_id]
                    n_entrie = checked_labels.get(label, 0)
                    checked_labels[label] = n_entrie + 1
                    n_labels = labels_counter[label]

                    if n_entrie > 20:
                        sentence = ""
                        end = ""

                    elif n_entrie > 0:
                        if len(sentence) > limit:
                            sentence = sentence[:limit] + "  <<<<<<<<"

                        else:
                            sentence = ""
                            end = ""

                    else:
                        pass

                    prefix = "[%s | %s:%s]" % (label, n_entrie + 1, n_labels)

                elif sentence_len > 80:
                    prefix = "[!]"

                elif sentence_len < 2:
                    sentence = ""
                    end = ""

            for s in styles[node_id]:
                if isinstance(s, style.ParagraphIndent):
                    indent = "\n" * s.width

            return indent + prefix + sentence + end

        content = "".join(map(compile_txt, subnodes))

        if is_paragraph_id(node_id):
            n_breaklines = 2
            end = ""
            for s in styles[node_id]:
                if isinstance(s, style.MarginTop):
                    n_breaklines += s.lines
                elif isinstance(s, style.FirstParagraph):
                    n_breaklines -= 2
                elif isinstance(s, style.FinalNewline):
                    end = "\n"
                if isinstance(s, style.Hide):
                    return ""

            return n_breaklines * "\n" + content + end

        return content

    if out_type == "txt":
        return compile_txt(struct)
