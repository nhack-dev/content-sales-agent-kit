# 出す前の確かめ：{{TITLE}}

- [ ] brief.md に空欄がない（オーナーが読んで OK と言った日を書く）
- [ ] 中身が brief.md の「約束すること」を全部満たしている（目次と照らす）
- [ ] `python3 scripts/claim_check.py products/{{ID}}/` 強 0件・中と弱は1件ずつ読んで判断した
- [ ] `python3 scripts/legal_check.py --tokushoho products/{{ID}}/legal.md --final products/{{ID}}/final-confirm.md` 足りない 0件
- [ ] 販売ページ・決済画面・特商法の表記・LINE の文で、値段・返品・届く時期が同じ
- [ ] 決済はテストモードで1回通した（テストカード）→ LINE にお届けが来た → タグが付いた → 売り込みの便が止まった
- [ ] お届けのリンクは期限つきか会員ページ（知っていれば誰でも開けるリンクではない）
- [ ] 問い合わせを受ける場所と、返事をする人が決まっている
- [ ] 本番の鍵に切り替えるのはオーナーの OK の後
