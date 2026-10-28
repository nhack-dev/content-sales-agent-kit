#!/usr/bin/env python3
"""特定商取引法にもとづく表記のページと、申込の最終確認の画面に、要る項目が書いてあるかを確かめる。

  python3 scripts/legal_check.py --tokushoho products/recipe-book/legal.md
  python3 scripts/legal_check.py --final products/recipe-book/final-confirm.md
  python3 scripts/legal_check.py --tokushoho legal.md --final final.md

見るのは「その項目の見出しや言葉があり、中身が空でないか」だけ。中身が正しいかは人が確かめる。
項目は消費者庁「特定商取引法ガイド」の通信販売の広告表示と、申込みの最終確認画面の表示を元にした（2026年10月に読んだもの）。
"""
from __future__ import annotations

import os as _ng_os, sys as _ng_sys  # N-Hack 専用の門（下の3行を消すとこのキットは動きません）
_ng_sys.path.insert(0, _ng_os.path.dirname(_ng_os.path.abspath(__file__)))
import nhack_gate as _nhack_gate  # noqa: E402,F401


import argparse
import re
import sys
from pathlib import Path

TOKUSHOHO = [
    ("販売事業者（法人名・個人の氏名）", r"(販売事業者|事業者の?名称|販売業者|氏名)"),
    ("責任者の氏名（法人のとき・代表者か通信販売の責任者）", r"(代表者|運営責任者|責任者)"),
    ("住所", r"(所在地|住所)"),
    ("電話番号", r"電話"),
    ("メールアドレス", r"(メール|E-?mail)"),
    ("販売価格（税込）", r"(販売価格|価格|料金)"),
    ("商品代金以外に必要な費用（送料・手数料など）", r"(以外|送料|手数料|必要な?料金|追加費用)"),
    ("支払方法", r"(支払方法|お支払い方法|決済方法)"),
    ("支払時期", r"(支払時期|お支払い時期|支払いの時期|決済の時期)"),
    ("引渡し・提供の時期", r"(引渡|引き渡し|提供時期|お届け|提供の時期|視聴開始)"),
    ("申込の撤回・解除（返品・返金・キャンセル）", r"(返品|返金|キャンセル|解約|撤回|解除)"),
    ("動作環境（デジタルのもの）", r"(動作環境|推奨環境|視聴環境|閲覧環境|対応端末)"),
]

FINAL = [
    ("分量（数・回数・期間）", r"(数量|分量|回数|期間|ページ数|本数|か月|ヶ月)"),
    ("販売価格（送料等を含む総額）", r"(価格|金額|合計|お支払い総額)"),
    ("支払時期・方法", r"(支払|決済)"),
    ("引渡し・提供の時期", r"(引渡|お届け|提供|視聴開始|ダウンロード)"),
    ("申込期間（あるとき）", r"(申込期間|受付期間|締め切り|期限|なし)"),
    ("申込の撤回・解除", r"(返品|返金|キャンセル|解約|撤回|解除)"),
    ("定期・継続のときはその旨と条件", r"(定期|継続|自動更新|サブスク|毎月|単発|1回限り|一回限り|都度)"),
]


def check(path: Path, items) -> int:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    missing = 0
    print(f"■ {path}")
    for label, pat in items:
        found = [ln for ln in lines if re.search(pat, ln)]
        filled = [ln for ln in found if re.sub(pat, "", ln).strip(" ：:|-*#　\t") and "〇〇" not in ln and "XXXX" not in ln]
        if not found:
            print(f"  ✗ {label} … 見つかりません")
            missing += 1
        elif not filled:
            print(f"  △ {label} … 見出しはあるが中身が空か見本のまま")
            missing += 1
        else:
            print(f"  ○ {label}")
    return missing


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tokushoho")
    ap.add_argument("--final")
    args = ap.parse_args()
    if not (args.tokushoho or args.final):
        ap.error("--tokushoho か --final のどちらかを指定")
    missing = 0
    if args.tokushoho:
        missing += check(Path(args.tokushoho), TOKUSHOHO)
    if args.final:
        missing += check(Path(args.final), FINAL)
    print(f"\n足りない・空 {missing} 件。" + ("" if missing else "形はそろっています。中身は人が読んで確かめてください。"))
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
