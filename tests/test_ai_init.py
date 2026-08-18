import importlib
import os
import sys


def test_import_ai_without_groq_key_does_not_crash(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(sys.modules, "__dict__", dict(sys.modules))

    sys.modules.pop("ai", None)

    module = importlib.import_module("ai")

    assert module is not None
