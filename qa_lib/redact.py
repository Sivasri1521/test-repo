"""Redact before anything goes near an AI tool (AI guardrails one-pager, 2 Nov):
same value -> same token, so the redacted text still makes sense."""
import re


class Redactor:
    PATTERNS = {
        "IP": r"\b\d{1,3}(?:\.\d{1,3}){3}\b",
        "EMAIL": r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
        "HOST": r"\b[a-z0-9-]+\.orion\.internal\b",
        "CUST": r"\bC\d{3}\b",
    }

    def __init__(self):
        self.mapping = {}
        self.counters = {}

    def _token(self, kind, value):
        if value not in self.mapping:
            self.counters[kind] = self.counters.get(kind, 0) + 1
            self.mapping[value] = f"{kind}_{self.counters[kind]:03d}"
        return self.mapping[value]

    def redact(self, text):
        for kind, pat in self.PATTERNS.items():
            text = re.sub(pat, lambda m, k=kind: self._token(k, m.group(0)), text)
        return text
