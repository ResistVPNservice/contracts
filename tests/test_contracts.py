import json
from datetime import UTC, datetime

from resist_contracts import ALL_EVENTS, PaymentSucceeded, SubscriptionExtended
from resist_contracts.schema import SCHEMAS, breaking_changes, check, event_schema


def test_topics_are_unique() -> None:
    topics = [cls.TOPIC for cls in ALL_EVENTS]
    assert len(topics) == len(set(topics))


def test_roundtrip_json() -> None:
    e = SubscriptionExtended(
        grant_id="payment:1",
        tg_id=42,
        source="payment",
        days=30,
        expire_at=datetime(2026, 1, 1, tzinfo=UTC),
        subscription_url="https://sub.example.com/x",
        short_uuid="x",
    )
    back = SubscriptionExtended.model_validate_json(e.model_dump_json())
    assert back == e


def test_committed_schemas_are_current() -> None:
    """schemas/*.json должны совпадать с кодом — иначе забыли `python -m resist_contracts.schema export`."""
    for cls in ALL_EVENTS:
        committed = json.loads((SCHEMAS / f"{cls.TOPIC}.json").read_text(encoding="utf-8"))
        assert committed == json.loads(json.dumps(event_schema(cls))), cls.TOPIC


def test_no_breaking_changes() -> None:
    assert check() == []


def test_breaking_change_detection() -> None:
    old = event_schema(PaymentSucceeded)
    new = json.loads(json.dumps(old))
    del new["properties"]["amount"]
    new["required"].append("brand_new")
    new["properties"]["brand_new"] = {"type": "string"}
    problems = breaking_changes(old, new)
    assert any("'amount' удалено" in p for p in problems)
    assert any("'brand_new' стало обязательным" in p for p in problems)

    optional_added = json.loads(json.dumps(old))
    optional_added["properties"]["promo_code"] = {"type": "string"}
    assert breaking_changes(old, optional_added) == []
