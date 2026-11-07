"""A minimal JSON Schema validator for tool inputs.

It covers the subset that tool schemas use in practice: object, string,
integer, number, boolean, array, required, enum and properties. Real projects
can swap in the `jsonschema` package; the harness only needs a list of errors.
"""
from __future__ import annotations

from typing import Any

_TYPES = {
    "object": dict, "string": str, "integer": int, "number": (int, float),
    "boolean": bool, "array": list,
}


def validate(value: Any, schema: dict, path: str = "input") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    if expected:
        py = _TYPES[expected]
        ok = isinstance(value, py) and not (expected in ("integer", "number") and isinstance(value, bool))
        if not ok:
            return [f"{path} should be {expected}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path} must be one of {schema['enum']}, got {value!r}")
    if expected == "object":
        props = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in value:
                errors.append(f"{path}.{name} is required")
        for name, sub in props.items():
            if name in value:
                errors.extend(validate(value[name], sub, f"{path}.{name}"))
        if schema.get("additionalProperties") is False:
            for name in value:
                if name not in props:
                    errors.append(f"{path}.{name} is not an allowed field")
    if expected == "array" and "items" in schema:
        for i, item in enumerate(value):
            errors.extend(validate(item, schema["items"], f"{path}[{i}]"))
    return errors
