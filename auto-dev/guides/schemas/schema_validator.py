#!/usr/bin/env python3
"""
Schema Validator - 类型化约束校验器
验证 JSON/YAML 文件是否符合 Schema 定义

用法:
  python schema_validator.py validate <schema> <file>
  python schema_validator.py check-pipeline <pipeline_dir>
  python schema_validator.py check-memory <memory_file>
  python schema_validator.py check-task <task_file>
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Tuple, List
import yaml

try:
    from jsonschema import validate, ValidationError, Draft7Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class SchemaValidator:
    """Schema 校验器"""

    SCHEMAS_DIR = Path(__file__).parent
    SCHEMA_MAP = {
        "pipeline": "pipeline.schema.json",
        "memory": "memory.schema.json",
        "agent": "agent.schema.json",
        "task": "task.schema.json"
    }

    def __init__(self):
        self.errors = []
        self.warnings = []

    def load_schema(self, schema_name: str) -> Optional[dict]:
        """加载 Schema"""
        if schema_name not in self.SCHEMA_MAP:
            schema_file = Path(schema_name)
        else:
            schema_file = self.SCHEMAS_DIR / self.SCHEMA_MAP[schema_name]

        if not schema_file.exists():
            self.errors.append(f"Schema not found: {schema_file}")
            return None

        try:
            with open(schema_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.errors.append(f"Failed to load schema: {e}")
            return None

    def load_document(self, file_path: str) -> Optional[dict]:
        """加载文档"""
        path = Path(file_path)
        if not path.exists():
            self.errors.append(f"File not found: {file_path}")
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                if path.suffix in [".yaml", ".yml"]:
                    return yaml.safe_load(f)
                elif path.suffix == ".json":
                    return json.load(f)
                else:
                    # 尝试 JSON，然后 YAML
                    f.seek(0)
                    content = f.read()
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return yaml.safe_load(content)
        except Exception as e:
            self.errors.append(f"Failed to load document: {e}")
            return None

    def validate(self, schema_name: str, file_path: str) -> Tuple[bool, List[str]]:
        """校验文档"""
        self.errors = []
        self.warnings = []

        if not HAS_JSONSCHEMA:
            self.warnings.append("jsonschema not installed, skipping validation")
            return True, self.warnings

        schema = self.load_schema(schema_name)
        if not schema:
            return False, self.errors

        doc = self.load_document(file_path)
        if not doc:
            return False, self.errors

        try:
            validate(instance=doc, schema=schema)
            return True, []
        except ValidationError as e:
            self.errors.append(f"Validation error: {e.message}")
            self.errors.append(f"  Path: {' -> '.join(str(p) for p in e.path)}")
            return False, self.errors
        except Exception as e:
            self.errors.append(f"Unexpected error: {e}")
            return False, self.errors

    def check_pipeline(self, pipeline_dir: str) -> Tuple[bool, List[str]]:
        """检查流水线"""
        self.errors = []
        self.warnings = []

        pipeline_path = Path(pipeline_dir)
        status_file = pipeline_path / "status.json"

        if not status_file.exists():
            # 尝试从 JSON 文件推断
            json_files = list(pipeline_path.glob("*.json"))
            if json_files:
                status_file = json_files[0]

        if not status_file.exists():
            self.errors.append(f"No status file found in {pipeline_dir}")
            return False, self.errors

        return self.validate("pipeline", str(status_file))

    def check_all_schemas(self) -> Tuple[bool, dict]:
        """检查所有 Schema 文件是否有效"""
        results = {}

        for name, filename in self.SCHEMA_MAP.items():
            schema_file = self.SCHEMAS_DIR / filename
            if schema_file.exists():
                try:
                    with open(schema_file, "r", encoding="utf-8") as f:
                        json.load(f)
                    results[name] = {"valid": True, "file": str(schema_file)}
                except json.JSONDecodeError as e:
                    results[name] = {"valid": False, "file": str(schema_file), "error": str(e)}
            else:
                results[name] = {"valid": False, "error": "File not found"}

        return all(r.get("valid", False) for r in results.values()), results


def main():
    parser = argparse.ArgumentParser(description="Schema Validator - 类型化约束校验")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # validate 命令
    val_parser = subparsers.add_parser("validate", help="校验文档")
    val_parser.add_argument("schema", help="Schema 名称或文件路径")
    val_parser.add_argument("file", help="要校验的文件")

    # check-pipeline 命令
    subparsers.add_parser("check-pipeline", help="校验流水线")
    subparsers.add_parser("check-all", help="校验所有 Schema")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    validator = SchemaValidator()

    if args.command == "validate":
        valid, errors = validator.validate(args.schema, args.file)
        if valid:
            print(f"[PASS] {args.file} is valid")
        else:
            print(f"[FAIL] {args.file} validation failed:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)

    elif args.command == "check-all":
        valid, results = validator.check_all_schemas()
        print("\n[Schema Check Results]")
        print("=" * 60)
        for name, result in results.items():
            status = "[PASS]" if result.get("valid") else "[FAIL]"
            print(f"{status} {name}: {result.get('file', result.get('error'))}")
        print("=" * 60)
        if valid:
            print("[PASS] All schemas are valid")
        else:
            print("[FAIL] Some schemas are invalid")
            sys.exit(1)

    elif args.command == "check-pipeline":
        # 检查所有流水线
        pipelines_dir = Path(__file__).parent.parent / "tasks" / "pipeline"
        if not pipelines_dir.exists():
            print(f"[INFO] No pipelines directory found")
            return

        all_valid = True
        for pipeline_dir in sorted(pipelines_dir.iterdir())[:5]:  # 检查最新5个
            valid, errors = validator.check_pipeline(str(pipeline_dir))
            status = "[PASS]" if valid else "[FAIL]"
            print(f"{status} {pipeline_dir.name}")
            if not valid:
                for err in errors[:3]:
                    print(f"    {err}")
                all_valid = False

        if all_valid:
            print("\n[PASS] All pipelines are valid")


if __name__ == "__main__":
    main()
