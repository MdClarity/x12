"""
test_fuzz_robustness.py

Property-based robustness fuzzing for the X12 parse pipeline.

The readers parse *untrusted* external input (X12 from trading partners), so the
robustness contract is:

    Parsing any input either succeeds or raises one of ``ALLOWED_EXCEPTIONS``
    (a clean, catchable parse/validation error) -- and always terminates.

Anything else -- ``KeyError``, ``IndexError``, ``AttributeError``,
``UnboundLocalError``, ``RecursionError``, or a hang -- is a robustness bug. This
suite generates malformed input three ways (structured mutation of real sample
transactions, arbitrary text, and raw bytes) and asserts the contract holds.

The run is derandomized so it behaves as a stable CI gate; deeper randomized
exploration can be run locally by overriding the Hypothesis profile.
"""

import glob
import os

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from linuxforhealth.x12.io import X12ModelReader, X12SegmentReader
from linuxforhealth.x12.parsing import X12ParseException
from tests.support import resources_directory

# The robustness contract: the only exception types a caller should ever have to
# handle when parsing untrusted input.
ALLOWED_EXCEPTIONS = (ValueError, X12ParseException, ValidationError)


def _load_seeds():
    """Returns every sample transaction as a mutation seed (multi-transaction coverage)."""
    seeds = []
    for path in sorted(glob.glob(os.path.join(resources_directory, "*", "*"))):
        if os.path.isfile(path):
            with open(path) as handle:
                seeds.append(handle.read())
    return seeds


SEEDS = _load_seeds()


@st.composite
def mutated_x12(draw):
    """
    Draws a real sample transaction and applies a handful of random point
    mutations (substitute / delete / truncate / insert), producing input that is
    structurally close to valid X12 but corrupted -- the cases most likely to slip
    past shallow guards and reach deep parser state.
    """
    chars = list(draw(st.sampled_from(SEEDS)))
    for _ in range(draw(st.integers(min_value=1, max_value=20))):
        if not chars:
            break
        operation = draw(st.integers(min_value=0, max_value=3))
        index = draw(st.integers(min_value=0, max_value=len(chars) - 1))
        if operation == 0:  # substitute
            chars[index] = draw(st.characters())
        elif operation == 1:  # delete a character
            del chars[index]
        elif operation == 2:  # truncate the remainder
            chars = chars[:index]
        else:  # insert junk
            chars.insert(index, draw(st.characters()))
    return "".join(chars)


# Structured mutations plus pure noise (arbitrary text, an ISA-prefixed variant
# that passes the is_x12_data gate, and raw decoded bytes).
fuzz_inputs = st.one_of(
    mutated_x12(),
    st.text(),
    st.text().map(lambda value: "ISA" + value),
    st.binary().map(lambda value: value.decode("latin-1")),
)

robustness_settings = settings(
    max_examples=400,
    deadline=5000,  # generous per-example bound; still catches hangs / pathological loops
    derandomize=True,  # deterministic gate
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


def _assert_only_contract_exceptions(reader_factory, data, drain):
    try:
        with reader_factory(data) as reader:
            drain(reader)
    except ALLOWED_EXCEPTIONS:
        pass
    except Exception as exc:  # noqa: BLE001 - the whole point is to catch the unexpected
        pytest.fail(
            f"{reader_factory.__name__} raised {type(exc).__name__} "
            f"on fuzz input ({data!r:.200}): {exc!r}"
        )


@robustness_settings
@given(data=fuzz_inputs)
def test_model_reader_only_raises_contract_exceptions(data):
    """X12ModelReader must never crash with an unexpected exception type."""
    _assert_only_contract_exceptions(
        X12ModelReader, data, lambda reader: list(reader.models())
    )


@robustness_settings
@given(data=fuzz_inputs)
def test_segment_reader_only_raises_contract_exceptions(data):
    """X12SegmentReader must never crash with an unexpected exception type."""
    _assert_only_contract_exceptions(
        X12SegmentReader, data, lambda reader: list(reader.segments())
    )
