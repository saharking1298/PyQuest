import json
import os


FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "defaults.json")


class _Defaults:
    def __init__(self):
        self.data = self._load_defaults()
        self.prompts = self.data["prompts"]
        self.errors = self.data["errors"]
        self.commands = self.data["commands"]

    @staticmethod
    def _load_defaults():
        return json.load(open(FILE, "r", encoding="utf-8"))

    def get(self, query: str) -> str:
        if query.startswith("$"):
            query = query[1:]
        valid_namespaces = ("prompts", "errors", "commands")
        namespace, value = query.split(".", 1)
        if namespace in valid_namespaces:
            return self.data[namespace][value]


defaults = _Defaults()
