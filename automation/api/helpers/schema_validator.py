from typing import Any

import allure
from jsonschema import Draft202012Validator


def validate_schema(payload: Any, schema: dict) -> None:
    """Validate the original payload; report failed schema rules without payload values."""
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: str(list(e.schema_path)))
    if errors:
        # jsonschema error.message may contain the entire secret-bearing instance.
        # Schema locations identify the rule without copying response values into Allure.
        details = "\n".join(
            f"schema {list(e.schema_path)}: failed {e.validator} (payload value omitted)"
            for e in errors
        )
        allure.attach(details, name="schema-errors", attachment_type=allure.attachment_type.TEXT)
        raise AssertionError(f"Schema validation failed:\n{details}")
