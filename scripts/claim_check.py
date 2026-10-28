#!/usr/bin/env python3
"""売る文（LP・投稿・LINE の便・note）に、誤解を招きやすい言い方が入っていないかを探す。

  python3 scripts/claim_check.py templates/sales-page.md
  python3 scripts/claim_check.py products/recipe-book/        # フォルダの .md .txt .json を全部

見つけたものは「言い換えの案」と一緒に出す。0件でも法律に合っている証明にはならない（人が最後に読む）。
終了コード: 強い注意が1件でもあれば 1、なければ 0。
"""
from __future__ import annotations

import os as _ng_os, sys as _ng_sys  # N-Hack 専用の門（下の3行を消すとこのキットは動きません）
_ng_sys.path.insert(0, _ng_os.path.dirname(_ng_os.path.abspath(__file__)))
import nhack_gate as _nhack_gate  # noqa: E402,F401


import argparse
import re
import sys
from pathlib import Path

# (強さ, 正規表現, なぜ, 言い換えの案)
RULES = [
    ("強", r"(誰でも|だれでも|全員|必ず|絶対に?|確実に|100\s*%|１００％).{0,12}(稼げ|儲か|もうか|成功|痩せ|治)",
     "成果を言い切っている（景品表示法の優良誤認になりやすい）", "「〜した方の例です（成果を約束するものではありません）」＋実例の条件"),
    ("強", r"(月収|月商|年収|日給)\s*[0-9０-９,，.]+\s*(万|億)?円?.{0,10}(稼げ|可能|保証|確定)",
     "金額の成果を約束している", "実例として出すなら、その人の条件・期間・かけた費用も並べる"),
    ("強", r"(元本|返金|成果)\s*保証", "保証の中身と条件が書かれていないと有利誤認になりやすい", "保証するなら条件・期限・手続きを同じ画面に書く"),
    ("強", r"(No\.?\s*1|ナンバーワン|NO1|業界初|日本初|世界初|最安|日本一|業界最大)",
     "比べた根拠（調査の主体・時期・対象）を持てないなら使わない", "根拠の調査がないなら外す。あるなら出どころと時期を並べて書く"),
    ("中", r"(今だけ|いまだけ|本日限り|今日だけ|残り\s*[0-9０-９]+\s*(名|席|個)|先着|期間限定|締め切り間近)",
     "本当に期限・数の上限があるか。無い・延長するなら有利誤認になりやすい", "締め切りの日時を書き、その日時に本当に止める"),
    ("中", r"(通常|定価|元値|参考価格)\s*[0-9０-９,，]+\s*円.{0,20}(→|を|が|から).{0,10}[0-9０-９,，]+\s*円",
     "比べる元の値段が、最近その値段で売っていた実績のあるものか（二重価格）", "実際に売っていた期間と値段を書けないなら、元の値段を出さない"),
    ("中", r"(完全)?(無料).{0,15}(ただし|※|別途|のみ)", "「無料」の後ろに条件が隠れていないか", "条件を「無料」と同じ大きさ・同じ場所に書く"),
    ("中", r"(リスク|損)(ゼロ|なし|０|0)", "リスクが無いと言い切っている", "どんな場合に費用・手間がかかるかを書く"),
    ("中", r"(口コミ|体験談|お客様の声|レビュー)", "依頼・謝礼をして書いてもらったものなら広告だと分かるように（ステルスマーケティングの告示）",
     "「モニター価格でお試しいただいた方の感想です」など、関係を書く"),
    ("弱", r"(放置|ほったらかし|自動で).{0,8}(稼|収入|お金)", "手間がかからないと誤解させやすい", "最初にやる作業と毎日・毎週の作業を書く"),
    ("弱", r"(誰にも言えない|裏技|秘密の|禁断)", "中身より期待をあおる言い方", "何が分かるかを具体的に書く"),
]


def scan(path: Path) -> list[tuple[str, int, str, str, str, str]]:
    hits = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return hits
    for n, line in enumerate(text.splitlines(), 1):
        for level, pat, why, fix in RULES:
            m = re.search(pat, line)
            if m:
                hits.append((level, n, m.group(0), why, fix, str(path)))
    return hits


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()

    files: list[Path] = []
    for p in map(Path, args.paths):
        if p.is_dir():
            files += [f for f in sorted(p.rglob("*")) if f.suffix in (".md", ".txt", ".json", ".html")]
        elif p.exists():
            files.append(p)
        else:
            print(f"見つかりません: {p}")
            sys.exit(2)

    hits = [h for f in files for h in scan(f)]
    order = {"強": 0, "中": 1, "弱": 2}
    for level, n, found, why, fix, path in sorted(hits, key=lambda h: (order[h[0]], h[5], h[1])):
        print(f"[{level}] {path}:{n}  「{found}」\n      なぜ: {why}\n      案: {fix}")
    strong = sum(1 for h in hits if h[0] == "強")
    print(f"\n{len(files)} ファイル・注意 {len(hits)} 件（強 {strong}）。0件でも最後は人が読んで確かめてください。")
    sys.exit(1 if strong else 0)


if __name__ == "__main__":
    main()
