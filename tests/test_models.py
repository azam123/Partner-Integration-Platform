from common.models import build_envelope, validate_envelope


def test_build_envelope_uses_id():
    envelope = build_envelope("shopify", "partner_api", {"id": 123, "name": "Order-1"})
    assert envelope.record_id == "123"


def test_validate_envelope_ok():
    payload = {
        "connector": "netsuite",
        "source_type": "partner_api",
        "record_id": "abc",
        "received_at": "2026-01-01T00:00:00+00:00",
        "payload": {"total": 10},
    }
    validate_envelope(payload)
