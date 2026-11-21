#!/usr/bin/env python3
"""Shared harness library for the Y13g independent verification.

Rebuilt from scratch (the /tmp/y13r2* harnesses are lost). The
runner and the launcher both exit 2 on import now (script-form-only
guard), so this library AST-extracts named functions and constants
from a source file and execs them in a fresh namespace. It never
imports the target module and never executes the target file.

Usage:
  ns = extract_funcs(path, func_names, const_names, extra_globals)
  ns["_is_runner_cmdline"](cmdline, cwd)  # etc.

extra_globals are injected into the namespace before exec (use for
_SHIP_DIR / SHIP_DIR, which must point at the staged ship under
test). Stdlib modules os/sys/json/hashlib/re/shlex/subprocess/time/
marshal are always available as globals.
"""
import ast
import hashlib
import json
import marshal
import os
import re
import shlex
import subprocess
import sys
import time


def extract_funcs(path, func_names, const_names=(), extra=None):
    """Return a namespace holding the named top-level functions
    and Assign constants from the file at path, execed without
    importing the module."""
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    tree = ast.parse(src, filename=path)
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in func_names:
            nodes.append(node)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if (isinstance(target, ast.Name)
                        and target.id in const_names):
                    nodes.append(node)
                    break
    missing_f = [n for n in func_names
                 if n not in {x.name for x in nodes
                              if isinstance(x, ast.FunctionDef)}]
    if missing_f:
        raise ValueError(f"{path}: functions not found: {missing_f}")
    mod = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(mod)
    code = compile(mod, path, "exec")
    ns = {
        "os": os, "sys": sys, "json": json, "hashlib": hashlib,
        "re": re, "shlex": shlex, "subprocess": subprocess,
        "time": time, "marshal": marshal,
        "__builtins__": __builtins__,
    }
    if extra:
        ns.update(extra)
    exec(code, ns)
    return ns


TOKENIZER_FUNCS = (
    "_script_basename_is_runner", "_is_python_token",
    "_shlex_tokens", "_runner_md5s", "_path_is_runner_copy",
    "_token_is_runner_script", "_c_code_executes_runner",
    "_python_executes_runner", "_command_executes_runner",
    "_argv_tokens", "_is_runner_cmdline", "_is_codex_process",
)
TOKENIZER_CONSTS = (
    "_RUNNER_MODULE_NAMES", "_RUNNER_MANIFEST_PATHS",
    "_RUNNER_MD5S", "_PY_NO_VALUE",
)


def extract_tokenizer(path, ship_dir):
    """Extract the 12 tokenizer functions from a runner/launcher
    copy, with _SHIP_DIR pointed at ship_dir."""
    return extract_funcs(
        path, TOKENIZER_FUNCS, TOKENIZER_CONSTS,
        extra={"_SHIP_DIR": ship_dir, "SHIP_DIR": ship_dir})


def strip_docstrings(tree):
    """Return a copy of an AST tree with module/function docstrings
    removed (so the AST comparison ignores doc text)."""
    import copy
    tree = copy.deepcopy(tree)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef, ast.Module)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                node.body = body[1:] or [ast.Pass()]
    return tree


def func_ast_dump(path, func_name):
    """ast.dump of one named function with its docstring stripped."""
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    tree = ast.parse(src, filename=path)
    for node in tree.body:
        if (isinstance(node, ast.FunctionDef)
                and node.name == func_name):
            return ast.dump(strip_docstrings(node))
    raise ValueError(f"{path}: function not found: {func_name}")


def now_hcm():
    """Wall-clock timestamp in Asia/Ho_Chi_Minh."""
    import datetime
    tz = datetime.timezone(datetime.timedelta(hours=7))
    return datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S +07")
