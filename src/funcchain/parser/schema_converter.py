import json
import re
from typing import Type

from pydantic import BaseModel

SPACE_RULE = '" "?'

PRIMITIVE_RULES = {
    "boolean": '("true" | "false") space',
    "number": '("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ([eE] [-+]? [0-9]+)? space',
    "integer": '("-"? ([0-9] | [1-9] [0-9]*)) space',
    "string": r""" "\"" (
        [^"\\] |
        "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])
      )* "\"" space """,
    "null": '"null" space',
}

INVALID_RULE_CHARS_RE = re.compile(r"[^a-zA-Z0-9-]+")
GRAMMAR_LITERAL_ESCAPE_RE = re.compile(r'[\r\n"]')
GRAMMAR_LITERAL_ESCAPES = {"\r": "\\r", "\n": "\\n", '"': '\\"'}


class SchemaConverter:
    def __init__(self, prop_order: dict, defs: dict) -> None:
        self._prop_order = prop_order
        self._defs = defs
        self._rules = {"space": SPACE_RULE}

    def _format_literal(self, literal: str) -> str:
        escaped = GRAMMAR_LITERAL_ESCAPE_RE.sub(
            lambda m: GRAMMAR_LITERAL_ESCAPES.get(m.group(0)),  # type: ignore
            json.dumps(literal),
        )
        return f'"{escaped}"'

    def _add_rule(self, name: str, rule: str) -> str:
        esc_name = INVALID_RULE_CHARS_RE.sub("-", name)
        if esc_name not in self._rules or self._rules[esc_name] == rule:
            key = esc_name
        else:
            i = 0
            while f"{esc_name}{i}" in self._rules:
                i += 1
            key = f"{esc_name}{i}"
        self._rules[key] = rule
        return key

    def visit(self, schema: dict, name: str) -> str:
        schema_type = schema.get("type")
        rule_name = name or "root"

        if "$ref" in schema:
            ref_name = schema["$ref"].split("/")[-1]
            assert ref_name in self._defs, f"Unresolved reference: {schema['$ref']}"
            return self.visit(self._defs[ref_name], ref_name)

        elif "oneOf" in schema or "anyOf" in schema:
            rule = " | ".join(
                (
                    self.visit(alt_schema, f'{name}{"-" if name else ""}{i}')
                    for i, alt_schema in enumerate(schema.get("oneOf") or schema["anyOf"])
                )
            )
            return self._add_rule(rule_name, rule)

        elif "allOf" in schema:
            rule = " ".join(
                (
                    self.visit(sub_schema, f'{name}{"-" if name else ""}{i}')
                    for i, sub_schema in enumerate(schema["allOf"])
                )
            )
            return self._add_rule(rule_name, rule)

        elif "const" in schema:
            return self._add_rule(rule_name, self._format_literal(schema["const"]))

        elif "enum" in schema:
            rule = " | ".join((self._format_literal(v) for v in schema["enum"]))
            return self._add_rule(rule_name, rule)

        elif schema_type == "object" and "properties" in schema:
            # TODO: `required` keyword
            prop_order = self._prop_order
            prop_pairs = sorted(
                schema["properties"].items(),
                # sort by position in prop_order (if specified) then by key
                key=lambda kv: (prop_order.get(kv[0], len(prop_order)), kv[0]),
            )

            rule = '"{" space'
            for i, (prop_name, prop_schema) in enumerate(prop_pairs):
                prop_rule_name = self.visit(prop_schema, f'{name}{"-" if name else ""}{prop_name}')
                if i > 0:
                    rule += ' "," space'
                rule += rf' {self._format_literal(prop_name)} space ":" space {prop_rule_name}'
            rule += ' "}" space'

            return self._add_rule(rule_name, rule)

        elif schema_type == "object":
            self._rules["number"] = '("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ([eE] [-+]? [0-9]+)? space'
            # todo self._rules["array"]
            # todo arbitrary nested objects
            self._rules["generic"] = 'string | number | "true" | "false" | "null"'
            return self._add_rule(
                rule_name,
                '"{" space (' 'string ":" space generic' '( "," space string ":" space generic )*' ')? "}" space',
            )

        elif schema_type == "array" and "items" in schema:
            # TODO `prefixItems` keyword
            item_rule_name = self.visit(schema["items"], f'{name}{"-" if name else ""}item')
            rule = f'"[" space ({item_rule_name} ("," space {item_rule_name})*)? "]" space'
            return self._add_rule(rule_name, rule)

        else:
            assert schema_type in PRIMITIVE_RULES, f"Unrecognized schema: {schema}"
            return self._add_rule(
                "root" if rule_name == "root" else schema_type,
                PRIMITIVE_RULES[schema_type],
            )

    def format_grammar(self) -> str:
        return "\n".join((f"{name} ::= {rule}" for name, rule in self._rules.items()))


def schema_to_grammar(json_schema: dict) -> str:
    schema = json_schema
    prop_order = {name: idx for idx, name in enumerate(schema["properties"].keys())}
    defs = schema.get("$defs", {})
    converter = SchemaConverter(prop_order, defs)
    converter.visit(schema, "")
    return converter.format_grammar()


def pydantic_to_grammar(model: Type[BaseModel]) -> str:
    return schema_to_grammar(model.model_json_schema())
