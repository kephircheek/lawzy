import unittest

from lawzy import core
from lawzy.core.config import PATTERN_SENTENCE_SPLIT
from tests.config import PATH_SAMPLE_SHORT_TXT


class TestAssebmle(unittest.TestCase):
    def test_reassemble_short(self):
        content = PATH_SAMPLE_SHORT_TXT.read_text()
        struct, styles, data = core.parser.parse_txt(content, PATTERN_SENTENCE_SPLIT)
        content_ = core.compiler.assemble(struct, styles, data, out_type="txt")
        self.assertSequenceEqual(content, content_)
