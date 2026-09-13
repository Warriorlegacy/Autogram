"""
scripts/generate_repo_map.py - Zero-Cost AST Codebase Compressor
Generates .agents/memory/ARCHITECTURE_MAP.md to prevent AI agents from burning tokens
by scanning the entire repository on every reboot.
"""

import os
import ast
from pathlib import Path

EXCLUDE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__", 
    ".agents", "workspace", "output", "build", "dist", ".pytest_cache",
    ".codebase-memory", ".codeartsdoer", ".kilo", ".kilocode"
}

def parse_python_symbols(filepath: str) -> list:
    symbols = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            tree = ast.parse(f.read(), filename=filepath)
        for item in tree.body:
            if isinstance(item, ast.FunctionDef):
                args = [a.arg for a in item.args.args]
                symbols.append(f"  - def {item.name}({', '.join(args)})")
            elif isinstance(item, ast.ClassDef):
                methods = [m.name for m in item.body if isinstance(m, ast.FunctionDef)]
                symbols.append(f"  - class {item.name} [methods: {', '.join(methods)}]")
    except Exception:
        pass
    return symbols

def generate_map(root_dir: str = "."):
    out_dir = Path(root_dir) / ".agents" / "memory"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "ARCHITECTURE_MAP.md"

    lines = [
        "# REPOSITORY ARCHITECTURAL SYMBOL MAP",
        "> Auto-generated structural index. AGENTS: Consult this index instead of scanning directories.\n"
    ]

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        rel_root = os.path.relpath(root, root_dir).replace("\\", "/")
        if rel_root == ".":
            rel_root = ""

        py_files = sorted([f for f in files if f.endswith((".py", ".js", ".ts"))])
        for f in py_files:
            full_p = os.path.join(root, f)
            rel_p = f"{rel_root}/{f}" if rel_root else f
            symbols = parse_python_symbols(full_p)
            lines.append(f"### `{rel_p}`")
            if symbols:
                lines.extend(symbols)
            else:
                lines.append("  (scripts / configuration)")
            lines.append("")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[RepoMap] Generated architecture map at: {out_file} ({os.path.getsize(out_file)} bytes)")

if __name__ == "__main__":
    generate_map()
