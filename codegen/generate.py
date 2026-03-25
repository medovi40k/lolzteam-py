#!/usr/bin/env python3
"""
Lolzteam API Python wrapper code generator.
Reads an OpenAPI 3.0 schema and generates typed Python methods.

Usage:
    python generate.py --schema forum_openapi.json --output ../lolzteam/sections/forum_generated.py
    python generate.py --schema market_openapi.json --output ../lolzteam/sections/market_generated.py
    python generate.py --all
"""

import argparse
import json
import re
from pathlib import Path

# Maps OpenAPI type -> Python type hint
TYPE_MAP = {
    "integer": "int",
    "number": "float",
    "string": "str",
    "boolean": "bool",
    "object": "dict",
    "array": "list",
}


def to_snake(name: str) -> str:
    """Convert camelCase / PascalCase / kebab-case to snake_case. Also strips [] suffixes."""
    name = name.replace("-", "_").replace("[]", "").replace(".", "_")
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    result = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    # Prefix identifiers that start with a digit (e.g. "2fa" -> "p_2fa")
    if result and result[0].isdigit():
        result = "p_" + result
    return result


def get_py_type(schema: dict) -> str:
    """Return a Python type annotation string from an OpenAPI schema fragment."""
    if not schema:
        return "Any"
    t = schema.get("type")
    # OpenAPI 3.1 allows type to be a list e.g. ["string", "null"]
    if isinstance(t, list):
        non_null = [x for x in t if x != "null"]
        t = non_null[0] if non_null else None
    if t == "array":
        items = schema.get("items", {})
        inner = get_py_type(items)
        return f"list[{inner}]"
    if t == "object":
        return "dict[str, Any]"
    return TYPE_MAP.get(t, "Any")


def resolve_path_params(path: str) -> list[str]:
    """Extract path parameter names from a path template."""
    return re.findall(r"\{(\w+)\}", path)


def build_method(
    operation_id: str,
    http_method: str,
    path: str,
    operation: dict,
    class_name: str,
) -> str:
    """Generate a single async/sync method string."""
    path_params = resolve_path_params(path)
    parameters = operation.get("parameters", [])
    request_body = operation.get("requestBody", {})
    summary = operation.get("summary", "")

    # Collect all params — required first, optional second
    required_params: list[str] = []
    optional_params: list[str] = []
    param_docs: list[str] = []

    # Path params first (always required)
    for pp in path_params:
        snake_pp = to_snake(pp)
        required_params.append(f"{snake_pp}: int")
        param_docs.append(f"        :param {snake_pp}: Path parameter.")

    # Query / header params
    query_params: list[str] = []
    for p in parameters:
        if p.get("in") not in ("query", "header"):
            continue
        p_name = to_snake(p["name"])
        p_schema = p.get("schema", {})
        p_type = get_py_type(p_schema)
        required = p.get("required", False)
        if required:
            required_params.append(f"{p_name}: {p_type}")
        else:
            optional_params.append(f"{p_name}: {p_type} | None = None")
        query_params.append(p["name"])
        param_docs.append(f"        :param {p_name}: {p.get('description', '')}")

    # Body params
    body_params: list[str] = []
    if request_body:
        content = request_body.get("content", {})
        schema = (
            content.get("application/json", {})
            .get("schema", {})
        )
        props = schema.get("properties", {})
        required_fields = schema.get("required", [])
        for prop_name, prop_schema in props.items():
            snake_prop = to_snake(prop_name)
            prop_type = get_py_type(prop_schema)
            is_req = prop_name in required_fields
            if is_req:
                required_params.append(f"{snake_prop}: {prop_type}")
            else:
                optional_params.append(f"{snake_prop}: {prop_type} | None = None")
            body_params.append(prop_name)
            param_docs.append(
                f"        :param {snake_prop}: {prop_schema.get('description', '')}"
            )

    func_params = required_params + optional_params

    # Build the actual path string
    path_fmt = path
    for pp in path_params:
        path_fmt = path_fmt.replace(f"{{{pp}}}", f"{{{to_snake(pp)}}}")

    # Build query dict construction
    query_lines: list[str] = []
    for p in parameters:
        if p.get("in") != "query":
            continue
        p_name = to_snake(p["name"])
        orig_name = p["name"]
        query_lines.append(f'        if {p_name} is not None: params["{orig_name}"] = {p_name}')

    # Build body dict construction
    body_lines: list[str] = []
    for bp in body_params:
        snake_bp = to_snake(bp)
        body_lines.append(f'        if {snake_bp} is not None: data["{bp}"] = {snake_bp}')

    # Signature
    params_str = ", ".join(["self"] + func_params)
    doc = f'        """{summary}"""\n' if summary else ""

    lines: list[str] = []

    # ---- sync version ----
    lines.append(f"    def {to_snake(operation_id)}({params_str}) -> dict[str, Any]:")
    if doc:
        lines.append(doc)
    lines.append("        params: dict[str, Any] = {}")
    lines.extend(query_lines)
    if body_params:
        lines.append("        data: dict[str, Any] = {}")
        lines.extend(body_lines)
    if path_params:
        path_arg = f'f"{path_fmt}"'
    else:
        path_arg = f'"{path_fmt}"'
    
    if body_params:
        lines.append(
            f"        return self._client.request(\"{http_method.upper()}\", {path_arg}, params=params, json=data)"
        )
    else:
        lines.append(
            f"        return self._client.request(\"{http_method.upper()}\", {path_arg}, params=params)"
        )
    lines.append("")

    # ---- async version ----
    lines.append(
        f"    async def {to_snake(operation_id)}_async({params_str}) -> dict[str, Any]:"
    )
    if doc:
        lines.append(doc)
    lines.append("        params: dict[str, Any] = {}")
    lines.extend(query_lines)
    if body_params:
        lines.append("        data: dict[str, Any] = {}")
        lines.extend(body_lines)
    if body_params:
        lines.append(
            f"        return await self._client.request_async(\"{http_method.upper()}\", {path_arg}, params=params, json=data)"
        )
    else:
        lines.append(
            f"        return await self._client.request_async(\"{http_method.upper()}\", {path_arg}, params=params)"
        )
    lines.append("")

    return "\n".join(lines)


def generate_section_class(tag: str, methods_code: str, use_json: bool = False) -> str:
    """Wrap methods into a section class."""
    class_name = "".join(w.capitalize() for w in tag.replace("_", " ").split()) + "Section"
    uj = "True" if use_json else "False"
    return (
        f"class {class_name}:\n"
        f"    \"\"\"Auto-generated section for tag: {tag}\"\"\"\n"
        f"\n"
        f"    def __init__(self, client: object) -> None:\n"
        f"        self._client = client\n"
        f"        self._use_json = {uj}\n"
        f"\n"
        f"{methods_code}\n"
    )


def generate_from_schema(schema_path: str, output_path: str, api_name: str) -> None:
    schema: dict = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    paths: dict = schema.get("paths", {})

    # Group operations by tag
    tag_methods: dict[str, list[str]] = {}

    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method.startswith("x-") or not isinstance(operation, dict):
                continue
            operation_id = operation.get("operationId", "")
            tags = operation.get("tags", ["misc"])
            tag = tags[0] if tags else "misc"

            method_code = build_method(
                operation_id=operation_id,
                http_method=method,
                path=path,
                operation=operation,
                class_name=tag,
            )
            tag_methods.setdefault(tag, []).append(method_code)

    # Build output
    sections: list[str] = []
    class_names: list[str] = []

    for tag, methods in tag_methods.items():
        class_name = "".join(w.capitalize() for w in tag.replace("_", " ").split()) + "Section"
        class_names.append((tag, class_name))
        methods_code = "\n".join(methods)
        sections.append(generate_section_class(tag, methods_code, use_json=(api_name == "market")))

    header = f'''# AUTO-GENERATED by codegen/generate.py
# Source schema: {Path(schema_path).name}
# DO NOT EDIT MANUALLY — regenerate from schema instead.
# fmt: off

from __future__ import annotations
from typing import Any  # noqa: I001

'''

    output = header + "\n\n".join(sections)
    Path(output_path).write_text(output, encoding="utf-8")
    print(f"[codegen] Generated {output_path}  ({len(tag_methods)} sections, {sum(len(v) for v in tag_methods.values())} operations)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Lolzteam API code generator")
    parser.add_argument("--schema", help="Path to OpenAPI JSON schema")
    parser.add_argument("--output", help="Output Python file path")
    parser.add_argument("--name", help="API name (forum/market)", default="api")
    parser.add_argument("--all", action="store_true", help="Generate all schemas")
    args = parser.parse_args()

    base = Path(__file__).parent

    if args.all or (not args.schema):
        generate_from_schema(
            str(base / "forum_openapi.json"),
            str(base.parent / "lolzteam" / "sections" / "_forum_generated.py"),
            "forum",
        )
        generate_from_schema(
            str(base / "market_openapi.json"),
            str(base.parent / "lolzteam" / "sections" / "_market_generated.py"),
            "market",
        )
    else:
        generate_from_schema(args.schema, args.output, args.name)


if __name__ == "__main__":
    main()
