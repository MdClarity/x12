"""
test_config.py

Characterization tests for the X12 settings models in ``config.py``.

``X12Config`` subclasses Pydantic's ``BaseSettings``, which moves to the separate
``pydantic-settings`` package in Pydantic v2.  These tests pin the observable
behavior -- environment-variable loading, case-insensitivity, defaults, and the
``x12_character_set`` pattern constraint -- so the migration preserves it.
"""

import pytest
from pydantic import ValidationError

from linuxforhealth.x12.config import X12Config


def test_defaults():
    config = X12Config()
    assert config.x12_character_set == "BASIC"
    assert config.x12_reader_buffer_size == 1024000


def test_loads_from_environment(monkeypatch):
    monkeypatch.setenv("X12_CHARACTER_SET", "EXTENDED")
    monkeypatch.setenv("X12_READER_BUFFER_SIZE", "2048")
    config = X12Config()
    assert config.x12_character_set == "EXTENDED"
    assert config.x12_reader_buffer_size == 2048


def test_environment_is_case_insensitive(monkeypatch):
    monkeypatch.setenv("x12_character_set", "EXTENDED")
    config = X12Config()
    assert config.x12_character_set == "EXTENDED"


def test_character_set_pattern_is_enforced(monkeypatch):
    monkeypatch.setenv("X12_CHARACTER_SET", "BOGUS")
    with pytest.raises(ValidationError):
        X12Config()
