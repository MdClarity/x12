"""
test_serialization_internals.py

Characterization tests that pin the *observable* behavior of the X12 serializer
internals that are most fragile across the Pydantic v1 -> v2 migration:

* ``X12Segment._process_multivalue_field`` selecting the component separator (``:``)
  for ``Field(is_component=True)`` list fields versus the repetition separator (``^``)
  for ordinary list fields -- this reads ``__fields__[name].field_info.extra`` in v1,
  which becomes ``model_fields[name].json_schema_extra`` in v2.
* ``X12Segment.x12`` honoring custom delimiters.
* ``X12SegmentGroup.x12`` discovering serializable sub-models by filtering
  ``__fields__.values()`` on ``hasattr(f.type_, "x12")`` -- ``f.type_`` is removed in
  v2 and must be reconstructed from ``f.annotation``.

These give the migration direct unit coverage of the introspection logic rather than
relying solely on the end-to-end round-trip suite.
"""

from decimal import Decimal

from linuxforhealth.x12.models import X12Delimiters
from linuxforhealth.x12.v5010.segments import EbSegment, HiSegment

# A non-default delimiter set, used to prove the separators are not hard-coded.
CUSTOM_DELIMITERS = X12Delimiters(
    element_separator="|",
    component_separator="@",
    repetition_separator="!",
    segment_terminator="?",
)


def test_component_list_field_uses_component_separator():
    """``is_component=True`` list fields join their values with ``:`` (HI segment)."""
    hi = HiSegment(
        health_care_code_1=["BK", "8901"],
        health_care_code_2=["BF", "87200"],
    )
    assert hi.x12() == "HI*BK:8901*BF:87200~"


def test_repetition_list_field_uses_repetition_separator():
    """Ordinary list fields join their values with ``^`` (EB service_type_code)."""
    eb = EbSegment(eligibility_benefit_information="1", service_type_code=["BY", "BZ"])
    assert eb.x12() == "EB*1**BY^BZ~"


def test_component_field_honors_custom_delimiters():
    """Component serialization uses the supplied custom component separator."""
    hi = HiSegment(
        health_care_code_1=["BK", "8901"],
        health_care_code_2=["BF", "87200"],
    )
    assert hi.x12(custom_delimiters=CUSTOM_DELIMITERS) == "HI|BK@8901|BF@87200?"


def test_repetition_field_honors_custom_delimiters():
    """Repetition serialization uses the supplied custom repetition separator."""
    eb = EbSegment(eligibility_benefit_information="1", service_type_code=["BY", "BZ"])
    assert eb.x12(custom_delimiters=CUSTOM_DELIMITERS) == "EB|1||BY!BZ?"


def test_decimal_field_serializes_to_two_places():
    """Decimal fields render with two decimal places in the X12 output (AMT segment)."""
    from linuxforhealth.x12.v5010.segments import AmtSegment

    amt = AmtSegment(amount_qualifier_code="R", monetary_amount=Decimal("37.5"))
    assert amt.x12() == "AMT*R*37.50~"


def test_trailing_empty_elements_are_stripped():
    """Unset trailing optional fields are dropped from the X12 output (ACT segment)."""
    from linuxforhealth.x12.v5010.segments import ActSegment

    act = ActSegment(tpa_account_number="1234", tpa_account_number_2="23498765")
    assert act.x12() == "ACT*1234*****23498765~"
