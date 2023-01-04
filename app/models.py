import json


class Base:
    def __init__(self, token, name):
        self.token = token
        self.name = name
        self.path = f"app/storage/{token}/{name}.json"
        self.indent = 2

    def post(self, content=None):
        content = content or {}
        with open(self.path, "w") as f:
            json.dump(content, f, indent=self.indent)

    def get(self):
        with open(self.path) as f:
            return json.load(f)


class Struct(Base):
    def __init__(self, token):
        super().__init__(token, "struct")


class Style(Base):
    def __init__(self, token):
        super().__init__(token, "style")


class KeywordEntries(Base):
    def __init__(self, token):
        super().__init__(token, "keywords")

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
    def __init__(self, token):
        super().__init__(token, "data")

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
