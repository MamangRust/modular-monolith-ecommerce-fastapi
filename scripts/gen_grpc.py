"""Reproducible gRPC codegen for the pb/ package. Generated files are post-processed so imports resolve inside the `pb` package; never edit pb/ by hand. Usage: python -m scripts.gen_grpc"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTO_DIR = ROOT / "proto"
OUT_DIR = ROOT / "pb"

# Domain packages that appear in `import <pkg>.<mod>` inside generated code
DOMAIN = [
    "common", "role", "user", "user_role", "auth", "merchant",
    "merchant_document", "merchant_award", "merchant_business",
    "merchant_detail", "merchant_policy", "merchant_social_link",
    "category", "product", "cart", "order", "order_item", "transaction",
    "review", "review_detail", "shipping_address", "banner", "slider",
]

# Same list flattened into the regex alternation used by the rewriter.
_PKGS_ALT = "|".join(sorted(DOMAIN, key=len, reverse=True))



def rewrite_module_imports(path: Path) -> None:
    text = path.read_text()
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        m = re.match(rf"^import ((?:{_PKGS_ALT})\.)?([a-z0-9_]+_pb2(?:_grpc)?) as (\S+)", line)
        if m:
            pkg, mod, alias = m.group(1) or "", m.group(2), m.group(3)
            if pkg:
                line = f"from pb.{pkg} import {mod} as {alias}\n"
            else:
                line = f"from pb import {mod} as {alias}\n"
        m2 = re.match(rf"^from (?:{_PKGS_ALT}) import ", line)
        if m2:
            line = re.sub(rf"^from (?:{_PKGS_ALT}) import", lambda mm: "from pb." + mm.group(0)[5:], line, count=1)
        m3 = re.match(rf"^from (?:{_PKGS_ALT})\.[a-z0-9_]+ import", line)
        if m3:
            line = re.sub(rf"^from (?P<p>{_PKGS_ALT})\.", r"from pb.\g<p>.", line, count=1)
        out.append(line)
    path.write_text("".join(out))


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "__init__.py").write_text('"""Generated gRPC packages. Do not edit; run `make proto`."""\n')
    protoc = [sys.executable, "-m", "grpc_tools.protoc", f"-I{PROTO_DIR}"]
    protos = sorted(str(p) for p in PROTO_DIR.rglob("*.proto"))
    protoc += ["--python_out", str(OUT_DIR), "--grpc_python_out", str(OUT_DIR), *protos]
    subprocess.run(protoc, check=True)
    for path in OUT_DIR.rglob("*.py"):
        if path.name == "__init__.py":
            continue
        rewrite_module_imports(path)
    for pkg_dir in [OUT_DIR, *OUT_DIR.rglob("*")]:
        if pkg_dir.is_dir() and not (pkg_dir / "__init__.py").exists():
            pkg_dir.mkdir(parents=True, exist_ok=True)
            (pkg_dir / "__init__.py").touch()
    print(f"generated {len(protos)} proto files into pb/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
