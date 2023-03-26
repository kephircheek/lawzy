import collections
import enum
import json
from dataclasses import asdict, is_dataclass

from lawzy.config import UPLOAD_FOLDER


def document_ids(token):
    return [item.name for item in (UPLOAD_FOLDER / str(token)).iterdir() if item.is_dir()]


def document_name(token, document_id):
    config = json.loads(
        (UPLOAD_FOLDER / str(token) / str(document_id) / "config.json").read_text()
    )
    return config["FILENAME"] + config["EXTENSION"]


class Base:
    def __init__(self, token, document_id, name):
        self.token = token
        self.name = name
        self.path = f"{UPLOAD_FOLDER}/{token}/{document_id}/{name}.json"
        self.indent = 2

    @staticmethod
    def _json_default(obj):
        data = {
            "__class__": {
                "__module__": obj.__class__.__module__,
                "__name__": obj.__class__.__name__,
            }
        }

        args, kwargs = None, None

        if is_dataclass(obj):
            kwargs = {k: getattr(obj, k) for k in asdict(obj).keys()}

        if args is not None or kwargs is not None:
            data["__init__"] = [[], {}]

            if args is not None and len(args) != 0:
                data["__init__"][0] = args

            if kwargs is not None and len(kwargs.keys()) != 0:
                data["__init__"][1] = kwargs

        elif isinstance(obj, enum.Enum):
            data["__getattr__"] = obj.name

        else:
            raise TypeError(f"can not serialize: {type(obj)}")

        return data

    def post(self, content=None):
        content = content or {}
        with open(self.path, "w") as f:
            json.dump(content, f, indent=self.indent, default=self._json_default)

    @staticmethod
    def _json_object_hook(dct: dict):
        if cls_dct := dct.get("__class__"):
            module_name = cls_dct["__module__"]
            class_name = cls_dct["__name__"]
            module = __import__(module_name, globals(), locals(), [class_name], 0)
            cls = getattr(module, class_name)

            if "__init__" in dct:
                args, kwargs = dct["__init__"]
                return cls(*args, **kwargs)

            if "__getattr__" in dct:
                return getattr(cls, dct["__getattr__"])

            return cls

        return dct

    def get(self):
        with open(self.path) as f:
            return json.load(f, object_hook=self._json_object_hook)


class Struct(Base):
    def __init__(self, token, document_id):
        super().__init__(token, document_id, "struct")


class Style(Base):
    def __init__(self, token, document_id):
        super().__init__(token, document_id, "style")

    def get(self):
        styles = super().get()
        styles_ = collections.defaultdict(list)
        styles_.update(styles)
        return styles_


class KeywordEntries(Base):
    def __init__(self, token, document_id):
        super().__init__(token, document_id, "keywords")

    def pop(self, keyword):
        content = self.get()
        entries = content.pop(keyword)
        self.post(content)
        return entries

    def add(self, keyword_entries):
        content = self.get()
        content.update(keyword_entries)
        self.post(content)


class Data(Base):
    def __init__(self, token, document_id):
        super().__init__(token, document_id, "data")

    def add(self, column):
        content = self.get()
        for id in content:
            content[id].append(column[id])
        self.post(content)

    @property
    def indexes(self):
        return self.get().keys()

    @property
    def sentences(self):
        return {id: item[0] for id, item in self.get().items()}

    @property
    def labels(self):
        if len(tuple(self.get().items())[0][1]) < 2:
            # print(tuple(self.get().items())[0][1])
            return None

        return {id: item[1] for id, item in self.get().items()}

    @property
    def dublicates(self):
        return {id: item[2] for id, item in self.get().items()}
