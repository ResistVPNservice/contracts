"""Экспорт контрактов в JSON Schema и AsyncAPI и проверка обратной совместимости.

    python -m quantum_contracts.schema export   # обновить schemas/*.json и asyncapi.yaml
    python -m quantum_contracts.schema check    # упасть, если изменения ломают старых потребителей

Правило совместимости (consumer-safe): к событию можно добавлять только необязательные поля.
Нельзя удалять поле, менять его тип или делать новое поле обязательным — потребители,
собранные со старой версией контрактов, перестанут понимать события.
"""

import json
import sys
from pathlib import Path
from typing import Any

from quantum_contracts.events import ALL_EVENTS, Event

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"


def event_schema(cls: type[Event]) -> dict[str, Any]:
    schema = cls.model_json_schema(mode="serialization")
    schema["x-topic"] = cls.TOPIC
    return schema


def asyncapi() -> str:
    lines = [
        "# Сгенерировано: python -m quantum_contracts.schema export — не редактировать руками",
        "asyncapi: 3.0.0",
        "info:",
        "  title: QuantumVPN events",
        "  version: 1.0.0",
        "  description: События Kafka между микросервисами QuantumVPN. Ключ сообщения — tg_id.",
        "channels:",
    ]
    for cls in ALL_EVENTS:
        name = cls.__name__
        lines += [
            f"  {name}:",
            f"    address: {cls.TOPIC}",
            "    messages:",
            f"      {name}:",
            f"        $ref: '#/components/messages/{name}'",
        ]
    lines += ["components:", "  messages:"]
    for cls in ALL_EVENTS:
        doc = " ".join((cls.__doc__ or "").split())
        lines += [
            f"    {cls.__name__}:",
            f"      summary: {json.dumps(doc, ensure_ascii=False)}",
            "      contentType: application/json",
            "      payload:",
            f"        $ref: './schemas/{cls.TOPIC}.json'",
        ]
    return "\n".join(lines) + "\n"


def export() -> None:
    SCHEMAS.mkdir(exist_ok=True)
    for cls in ALL_EVENTS:
        text = json.dumps(event_schema(cls), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        (SCHEMAS / f"{cls.TOPIC}.json").write_text(text, encoding="utf-8")
    (ROOT / "asyncapi.yaml").write_text(asyncapi(), encoding="utf-8")


def _type(prop: dict[str, Any]) -> Any:
    return prop.get("type") or prop.get("anyOf") or prop.get("$ref") or prop.get("enum")


def breaking_changes(old: dict[str, Any], new: dict[str, Any]) -> list[str]:
    problems = []
    old_props, new_props = old.get("properties", {}), new.get("properties", {})
    for field, prop in old_props.items():
        if field not in new_props:
            problems.append(f"поле {field!r} удалено")
        elif _type(prop) != _type(new_props[field]):
            problems.append(f"у поля {field!r} изменился тип")
    added_required = set(new.get("required", [])) - set(old.get("required", []))
    for field in sorted(added_required):
        problems.append(f"поле {field!r} стало обязательным")
    return problems


def check() -> list[str]:
    problems = []
    current = {cls.TOPIC: event_schema(cls) for cls in ALL_EVENTS}
    for path in sorted(SCHEMAS.glob("*.json")):
        topic = path.stem
        old = json.loads(path.read_text(encoding="utf-8"))
        if topic not in current:
            problems.append(f"{topic}: событие удалено")
            continue
        problems += [f"{topic}: {p}" for p in breaking_changes(old, current[topic])]
    return problems


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "export":
        export()
        print(f"schemas: {SCHEMAS}")
    else:
        found = check()
        for p in found:
            print(f"breaking: {p}")
        sys.exit(1 if found else 0)
