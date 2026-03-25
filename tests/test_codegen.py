"""
tests/test_codegen.py
~~~~~~~~~~~~~~~~~~~~~
Tests that verify the code generator produces valid, importable Python.
"""

from __future__ import annotations

import ast
import json
import sys
import tempfile
from pathlib import Path

import pytest

CODEGEN_DIR = Path(__file__).parent.parent / "codegen"
FORUM_SCHEMA = CODEGEN_DIR / "forum_openapi.json"
MARKET_SCHEMA = CODEGEN_DIR / "market_openapi.json"


def _run_generator(schema_path: Path, output_path: Path) -> None:
    """Helper: call the generator directly."""
    sys.path.insert(0, str(CODEGEN_DIR))
    import importlib
    import importlib.util

    spec = importlib.util.spec_from_file_location("generate", CODEGEN_DIR / "generate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.generate_from_schema(str(schema_path), str(output_path), "test")


class TestCodeGenerator:
    def test_forum_schema_is_valid_json(self):
        data = json.loads(FORUM_SCHEMA.read_text(encoding="utf-8"))
        assert "paths" in data
        assert "openapi" in data

    def test_market_schema_is_valid_json(self):
        data = json.loads(MARKET_SCHEMA.read_text(encoding="utf-8"))
        assert "paths" in data

    def test_generates_valid_python_from_forum_schema(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            out = Path(f.name)
        try:
            _run_generator(FORUM_SCHEMA, out)
            source = out.read_text(encoding="utf-8")
            tree = ast.parse(source)  # Should not raise SyntaxError
            assert tree is not None
        finally:
            out.unlink(missing_ok=True)

    def test_generates_valid_python_from_market_schema(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            out = Path(f.name)
        try:
            _run_generator(MARKET_SCHEMA, out)
            source = out.read_text(encoding="utf-8")
            ast.parse(source)
        finally:
            out.unlink(missing_ok=True)

    def test_generated_forum_has_expected_classes(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            out = Path(f.name)
        try:
            _run_generator(FORUM_SCHEMA, out)
            source = out.read_text(encoding="utf-8")
            tree = ast.parse(source)
            class_names = {
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
            }
            assert "UsersSection" in class_names
            assert "ThreadsSection" in class_names
            assert "PostsSection" in class_names
            assert "ConversationsSection" in class_names
        finally:
            out.unlink(missing_ok=True)

    def test_generated_market_has_expected_classes(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            out = Path(f.name)
        try:
            _run_generator(MARKET_SCHEMA, out)
            source = out.read_text(encoding="utf-8")
            tree = ast.parse(source)
            class_names = {
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
            }
            assert "AccountsManagingSection" in class_names
            assert "PaymentsSection" in class_names
            assert "AccountPurchasingSection" in class_names
            assert "ProfileSection" in class_names
        finally:
            out.unlink(missing_ok=True)

    def test_each_method_has_async_counterpart(self):
        """Every sync method should have an _async twin."""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            out = Path(f.name)
        try:
            _run_generator(FORUM_SCHEMA, out)
            source = out.read_text(encoding="utf-8")
            tree = ast.parse(source)
            # Collect both regular and async function names
            func_names = [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            sync_funcs = {n for n in func_names if not n.endswith("_async") and n != "__init__"}
            async_funcs = {n[: -len("_async")] for n in func_names if n.endswith("_async")}
            assert sync_funcs == async_funcs, (
                f"Mismatch — sync without async: {sync_funcs - async_funcs}"
            )
        finally:
            out.unlink(missing_ok=True)

    def test_custom_schema_generates_correct_operationids(self):
        """Minimal custom schema: check operationId -> method name mapping."""
        schema = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {
                "/items/{itemId}": {
                    "get": {
                        "operationId": "getItem",
                        "tags": ["items"],
                        "parameters": [
                            {
                                "name": "itemId",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"},
                            }
                        ],
                        "responses": {"200": {"description": "ok"}},
                    }
                }
            },
        }
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        ) as sf:
            json.dump(schema, sf)
            schema_file = Path(sf.name)

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            out = Path(f.name)
        try:
            _run_generator(schema_file, out)
            source = out.read_text(encoding="utf-8")
            tree = ast.parse(source)
            func_names = {
                node.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            assert "get_item" in func_names
            assert "get_item_async" in func_names
        finally:
            out.unlink(missing_ok=True)
            schema_file.unlink(missing_ok=True)

    def test_snake_case_conversion(self):
        from importlib.util import spec_from_file_location, module_from_spec

        spec = spec_from_file_location("generate", CODEGEN_DIR / "generate.py")
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)

        assert mod.to_snake("camelCase") == "camel_case"
        assert mod.to_snake("PascalCase") == "pascal_case"
        assert mod.to_snake("kebab-case") == "kebab_case"
        assert mod.to_snake("already_snake") == "already_snake"
        assert mod.to_snake("getItemById") == "get_item_by_id"
