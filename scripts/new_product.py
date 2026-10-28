#!/usr/bin/env python3
"""新しい商品（教材・PDF・note・動画講座）の作業フォルダを、型から作る。

  python3 scripts/new_product.py recipe-book --title "15分晩ごはん 30品レシピ本" --kind pdf

products/<id>/ に次のファイルができる（あるファイルは上書きしない）:
  brief.md          誰の・どの悩みを・どこまで解くか（最初にオーナーと決める）
  outline.md        中身の目次（kind ごとの型）
  sales-page.md     販売ページの下書き
  legal.md          特定商取引法にもとづく表記の下書き
  final-confirm.md  申込の最終確認に出す項目
  line-steps.json   line-agent-kit の flow.json に足す教育の便（7日分の型）
  checklist.md      出す前の確かめ
"""
from __future__ import annotations

import os as _ng_os, sys as _ng_sys  # N-Hack 専用の門（下の3行を消すとこのキットは動きません）
_ng_sys.path.insert(0, _ng_os.path.dirname(_ng_os.path.abspath(__file__)))
import nhack_gate as _nhack_gate  # noqa: E402,F401


import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "templates"

OUTLINE = {"pdf": "outline-pdf-guide.md", "note": "outline-note-article.md",
           "video": "outline-video-script.md", "course": "outline-video-script.md"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("id", help="英小文字・数字・ハイフン")
    ap.add_argument("--title", required=True)
    ap.add_argument("--kind", choices=sorted(OUTLINE), default="pdf")
    args = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,40}", args.id):
        raise SystemExit("id は英小文字・数字・ハイフン（例 recipe-book）")

    out = ROOT / "products" / args.id
    out.mkdir(parents=True, exist_ok=True)
    plan = {
        "brief.md": "offer-brief.md",
        "outline.md": OUTLINE[args.kind],
        "sales-page.md": "sales-page.md",
        "legal.md": "tokushoho.md",
        "final-confirm.md": "final-confirm.md",
        "line-steps.json": "line-education-steps.json",
        "checklist.md": "launch-checklist.md",
    }
    for name, src in plan.items():
        dst = out / name
        if dst.exists():
            print(f"  そのまま（もうある）: {dst.relative_to(ROOT)}")
            continue
        text = (T / src).read_text(encoding="utf-8").replace("{{TITLE}}", args.title).replace("{{ID}}", args.id)
        dst.write_text(text, encoding="utf-8")
        print(f"  作った: {dst.relative_to(ROOT)}")
    print(f"次: products/{args.id}/brief.md をオーナーと埋める（playbooks/01-offer.md）")


if __name__ == "__main__":
    main()
