#!/usr/bin/env python3
"""集客から購入までの数字を週ごとに並べ、いちばん落ちている段を1つ選ぶ。

  python3 scripts/funnel_report.py data/funnel.example.csv
  python3 scripts/funnel_report.py data/funnel.csv --last 4

CSV の列（1行＝1週）:
  week, impressions, profile_clicks, line_adds, step_reads, offer_clicks, purchases, revenue, refunds, blocks
  ・impressions … SNS の表示回数（各キットの数字を足す）
  ・line_adds … LINE の友だち追加（line-agent-kit の admin.py stats の増え）
  ・offer_clicks … 購入リンクを開いた数（決済サービスの数字）
  ・revenue・refunds … 円
足りない列は空でよい（その段は計算しない）。
"""
from __future__ import annotations

import os as _ng_os, sys as _ng_sys  # N-Hack 専用の門（下の3行を消すとこのキットは動きません）
_ng_sys.path.insert(0, _ng_os.path.dirname(_ng_os.path.abspath(__file__)))
import nhack_gate as _nhack_gate  # noqa: E402,F401


import argparse
import csv
import sys
from pathlib import Path

STAGES = [
    ("impressions", "profile_clicks", "表示→プロフィール", "投稿の最初の1行と、プロフィールへの理由づけ"),
    ("profile_clicks", "line_adds", "プロフィール→LINE追加", "LINE で受け取れるもの（特典）の分かりやすさ"),
    ("line_adds", "offer_clicks", "LINE追加→購入リンク", "教育の便の中身と、案内の回数・時期"),
    ("offer_clicks", "purchases", "購入リンク→購入", "販売ページ・値段・不安への答え・支払い方法"),
]


def num(v: str | None) -> float | None:
    try:
        return float(v) if v not in (None, "") else None
    except ValueError:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--last", type=int, default=8, help="直近何週を見るか")
    args = ap.parse_args()

    rows = list(csv.DictReader(Path(args.csv).open(encoding="utf-8")))[-args.last:]
    if not rows:
        print("行がありません")
        sys.exit(2)

    print("週         " + "  ".join(f"{s[2]:>16}" for s in STAGES) + "   売上(返金引き)  ブロック/追加")
    latest = {}
    for r in rows:
        cells = []
        for a, b, label, _ in STAGES:
            x, y = num(r.get(a)), num(r.get(b))
            rate = (y / x * 100) if x and y is not None else None
            cells.append(f"{rate:>15.1f}%" if rate is not None else f"{'-':>16}")
            latest[label] = rate
        rev = (num(r.get("revenue")) or 0) - (num(r.get("refunds")) or 0)
        adds, blocks = num(r.get("line_adds")), num(r.get("blocks"))
        br = f"{blocks / adds * 100:.0f}%" if adds and blocks is not None else "-"
        print(f"{r.get('week', ''):<10} " + "  ".join(cells) + f"   {rev:>12,.0f}円  {br:>8}")

    # 前の週より下がった段・いちばん低い段ではなく「直近の週で、前の4週の平均からいちばん落ちた段」を選ぶ
    if len(rows) >= 2:
        worst, worst_drop = None, 0.0
        for a, b, label, hint in STAGES:
            series = [(num(r.get(b)) / num(r.get(a)) * 100) for r in rows
                      if num(r.get(a)) and num(r.get(b)) is not None]
            if len(series) < 2:
                continue
            base = sum(series[-5:-1]) / len(series[-5:-1])
            drop = base - series[-1]
            if drop > worst_drop:
                worst, worst_drop = (label, hint, base, series[-1]), drop
        if worst:
            label, hint, base, now = worst
            print(f"\nいちばん落ちた段: {label}（前の平均 {base:.1f}% → 直近 {now:.1f}%）")
            print(f"まず見るところ: {hint}")
            print("次の1週間で変えるのは この段の1か所だけにする（2か所変えると、どちらが効いたか分からない）")
        else:
            print("\n前の平均より落ちた段はありません。いちばん率の低い段から1つ試す案を出してください")


if __name__ == "__main__":
    main()
