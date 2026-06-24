"""
test_resource_roundtrip.py

A data-driven "characterization" oracle for the X12 parse -> validate -> serialize
pipeline.  Every sample transaction under ``tests/resources`` is auto-discovered and
round-tripped through :func:`tests.support.assert_eq_model`, which asserts that the
models regenerate their original X12 input byte-for-byte.

This single boolean-per-file suite transitively exercises the serializer introspection
in ``models.py`` (``__fields__`` / ``field_info.extra`` / ``type_``), the list/component
detection in ``parsing.py``, enum/Decimal/date serialization, and ``Optional`` field
defaults.  It is the safety net that makes the Pydantic v1 -> v2 migration verifiable:
if behavior is preserved, every file here still round-trips.
"""

import glob
import os

import pytest

from tests.support import assert_eq_model, resources_directory


def _discover_resource_files():
    """Yields every sample transaction file under the resources directory."""
    pattern = os.path.join(resources_directory, "*", "*")
    for path in sorted(glob.glob(pattern)):
        if os.path.isfile(path):
            yield os.path.relpath(path, resources_directory)


RESOURCE_FILES = list(_discover_resource_files())


def test_resources_were_discovered():
    """Guards against the glob silently matching nothing (e.g. moved resources)."""
    assert len(RESOURCE_FILES) >= 60


@pytest.mark.parametrize("rel_path", RESOURCE_FILES)
def test_resource_round_trips(rel_path: str):
    """Each sample transaction must regenerate its original X12 input exactly."""
    x12_file_path = os.path.join(resources_directory, rel_path)
    assert os.path.exists(x12_file_path)
    assert_eq_model(x12_file_path)
