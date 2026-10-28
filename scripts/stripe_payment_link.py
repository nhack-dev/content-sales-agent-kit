#!/usr/bin/env python3
"""Stripe に商品・価格・決済リンク（Payment Links）を作る。既定は試し（何も作らない）。

  python3 scripts/stripe_payment_link.py --name "15分晩ごはん 30品レシピ本（PDF）" --amount 1980 \
      --redirect https://example.com/thanks --tos
  python3 scripts/stripe_payment_link.py ... --go

  --tos       申込の前に「利用規約に同意」のチェックを出す（Stripe の公開情報に利用規約の URL を先に入れておく）
  --phone     電話番号を入力してもらう
  --limit 1   決済が1回終わったらリンクを止める（1点もの・試し用）

作ったら payment_link の id（plink_...）と url が出る。line-agent-kit の config/flow.json の products に入れる。
鍵は .env の STRIPE_SECRET_KEY（テスト中は sk_test_ から始まる鍵を使う）。
"""
from __future__ import annotations

import os as _ng_os, sys as _ng_sys  # N-Hack 専用の門（下の3行を消すとこのキットは動きません）
_ng_sys.path.insert(0, _ng_os.path.dirname(_ng_os.path.abspath(__file__)))
import nhack_gate as _nhack_gate  # noqa: E402,F401


import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def env_key() -> str:
    key = os.environ.get("STRIPE_SECRET_KEY", "")
    p = ROOT / ".env"
    if not key and p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.startswith("STRIPE_SECRET_KEY="):
                key = line.split("=", 1)[1].strip()
    return key


def call(key: str, path: str, params: list[tuple[str, str]]) -> dict:
    req = urllib.request.Request(
        "https://api.stripe.com" + path,
        data=urllib.parse.urlencode(params).encode(),
        method="POST",
        headers={"Authorization": "Basic " + base64.b64encode(f"{key}:".encode()).decode(),
                 "Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Stripe {path} {e.code}: {e.read().decode()[:400]}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True)
    ap.add_argument("--amount", type=int, required=True, help="税込の値段（円）")
    ap.add_argument("--currency", default="jpy")
    ap.add_argument("--redirect", help="支払い後に開くページ（無ければ Stripe の完了画面）")
    ap.add_argument("--tos", action="store_true")
    ap.add_argument("--phone", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--go", action="store_true")
    args = ap.parse_args()

    link_params = [("line_items[0][quantity]", "1")]
    if args.redirect:
        link_params += [("after_completion[type]", "redirect"), ("after_completion[redirect][url]", args.redirect)]
    if args.tos:
        link_params.append(("consent_collection[terms_of_service]", "required"))
    if args.phone:
        link_params.append(("phone_number_collection[enabled]", "true"))
    if args.limit:
        link_params.append(("restrictions[completed_sessions][limit]", str(args.limit)))

    print("== 本番（--go）: Stripe に作ります ==" if args.go else "== 試し: 何も作りません。作るときは --go ==")
    print(f"商品: {args.name} ／ {args.amount:,} {args.currency.upper()}")
    print("決済リンクの設定: " + ", ".join(f"{k}={v}" for k, v in link_params))
    if not args.go:
        return

    key = env_key()
    if not key.startswith(("sk_test_", "sk_live_", "rk_test_", "rk_live_")):
        raise SystemExit(".env に STRIPE_SECRET_KEY がありません（Stripe → 開発者 → API キー）")
    if key.startswith(("sk_live_", "rk_live_")):
        print("注意: 本番の鍵です。お客様が実際に支払えるリンクができます")
    product = call(key, "/v1/products", [("name", args.name)])
    price = call(key, "/v1/prices", [("product", product["id"]), ("unit_amount", str(args.amount)),
                                     ("currency", args.currency)])
    link = call(key, "/v1/payment_links", [("line_items[0][price]", price["id"])] + link_params)
    print(json.dumps({"product": product["id"], "price": price["id"],
                      "payment_link_id": link["id"], "payment_link_url": link["url"]}, ensure_ascii=False, indent=2))
    print("→ line-agent-kit の config/flow.json の products に payment_link_id と payment_link_url を入れる")


if __name__ == "__main__":
    main()
