# content-sales-agent-kit

**SNSで知ってもらう → LINEで友だちになる → LINEで学んでもらう → 自分の教材を作る → 自動で売って自動で届ける**
を、あなたのAIエージェント（Claude Code など）が通しで回すための手順書です。

このキットは「流れ全体の地図」と「売る所（教材・販売ページ・決済・お届け・法律の確かめ）」を受け持ちます。
集客・LINE は別のキットと組み合わせて使います。

LINE の自動化は別のリポジトリ **line-agent-kit**（https://github.com/nhack-dev/line-agent-kit ）です。このキットの中には入っていません。
2つを同じ親フォルダに並べて置く形をおすすめします（例 `~/kits/content-sales-agent-kit` と `~/kits/line-agent-kit`）。手順書の「line-agent-kit の〜」は、その並べたフォルダを指します。

## 全体の地図（どの順に・何を使うか）

```
 ① 集める           ② つなぐ            ③ 学んでもらう        ④ 作る               ⑤ 売る・届ける         ⑥ 測る
 ─────────          ─────────          ─────────           ─────────           ─────────            ─────────
 x-agent-kit        投稿から LINE へ     line-agent-kit       このキット          このキット＋            このキット
 instagram-agent-kit  （templates/        ・あいさつ           ・new_product.py    line-agent-kit         ・funnel_report.py
 threads-agent-kit    sns-post-to-line）  ・ステップ配信       ・教材/PDF/note/    ・Stripe Payment Links   （週1回）
 blog-agent-kit     lp-agent-kit        ・アンケート→タグ     動画台本の型        ・購入→LINEでお届け
   （検索から）        （LINEに誘うページ） ・購入ボタン         ・claim_check.py     ・legal_check.py
```

| 順番 | やること | 使うキット | このキットの手順 |
|---|---|---|---|
| 0 | 誰に・何を・いくらで売るかを決める | このキット | playbooks/01-offer.md |
| 1 | SNS・ブログで役に立つ投稿を続ける | x／instagram／threads／blog の各キット | （各キットの README を正とする） |
| 2 | 投稿から LINE に誘う（特典・続き・アンケート） | 各SNSキット＋lp-agent-kit（受け取りページ） | playbooks/02-sns-to-line.md |
| 3 | LINE で7日間学んでもらう・答えでタグを付ける | line-agent-kit | playbooks/03-line-education.md |
| 4 | 教材（PDF・note・動画）を作る | このキット | playbooks/04-make-content.md |
| 5 | 販売ページ・決済リンク・自動お届け | このキット＋line-agent-kit（＋lp-agent-kit） | playbooks/05-sell-and-deliver.md |
| 6 | 毎週の数字で、落ちている段を1つだけ直す | このキット | playbooks/06-measure.md |
| 毎回 | 出す前の法律・言い方の確かめ | このキット | playbooks/07-legal-check.md・AGENT.md |

**はじめて組むときの順番**：0 → 4（小さな教材を先に1つ） → 3 → 5 → 2 → 1 → 6。
売るものと LINE の受け皿を先に作り、集客は最後に足します（人が来ても受け皿がないと無駄になるため）。

ほかのキットを持っていなくても、0・3〜6 はこのキットと line-agent-kit だけで動きます（集客は手で投稿）。

## 最初の10分

```bash
cp .env.example .env                                  # Stripe を使うときだけ鍵を入れる
python3 scripts/new_product.py first-guide --title "はじめての〇〇ガイド" --kind pdf
python3 scripts/claim_check.py products/first-guide/   # 言い方の確かめ（見本のまま → 注意が出ます）
python3 scripts/legal_check.py --tokushoho products/first-guide/legal.md --final products/first-guide/final-confirm.md
python3 scripts/funnel_report.py data/funnel.example.csv
python3 scripts/stripe_payment_link.py --name "はじめての〇〇ガイド" --amount 1980 --tos   # 試し（何も作らない）
```

ここまでで、商品フォルダの型・法律の抜け・言い方の注意・数字の見方・決済リンクの作り方が一通り見えます。
次は `products/first-guide/brief.md` をオーナーと埋めます（playbooks/01-offer.md）。

## 費用（あなたの側だけ）

- **Stripe**（使うとき）… 日本のカード決済 3.6%／件、Payment Links 自体に追加の月額なし（2026年10月に https://stripe.com/jp/pricing で確認）
- **note・Brain など販売サービス**（使うとき）… 手数料・振込の条件は各サービスの公式で確かめる（変わるため、このキットには書かない）
- **LINE・Cloudflare** … line-agent-kit の README のとおり（無料の枠から始められる）
- このキットの作り手のサーバー・鍵・課金は一切使いません

## あなたが取るキー

| キー | 取る場所 | 使う所 |
|---|---|---|
| Stripe のシークレットキー（まずテスト用 `sk_test_`） | Stripe → 開発者 → API キー | `stripe_payment_link.py` |
| Stripe の Webhook 署名シークレット `whsec_` | Stripe → 開発者 → Webhook | line-agent-kit の Worker（購入→LINEでお届け） |
| LINE・Cloudflare | line-agent-kit の README | LINE の配信 |

## できないこと（正直に）

- **法律の判断はしません。** `claim_check.py`・`legal_check.py` は抜けや危ない言い方を見つける補助です。0件でも法律に合っている証明にはなりません。迷うものは専門家（弁護士・消費生活の相談窓口）に。
- **note・Brain での自動お届けは、そのサービスの中の仕組みで行います。** 購入者の連絡先がこちらに渡らない作りのことが多く、LINE のタグ付けや自動のお届けは Stripe で売ったときだけです。
- 各SNSへの自動投稿は、このキットには入っていません（各SNSのキットと、各SNSの規約の範囲で）。
- 売上を約束するものではありません。

## 中身

```
README.md / AGENT.md / CLAUDE.md / LICENSE
playbooks/   01-offer  02-sns-to-line  03-line-education  04-make-content  05-sell-and-deliver  06-measure  07-legal-check
templates/   offer-brief・outline-（pdf-guide／note-article／video-script）・sales-page・tokushoho・final-confirm
             line-education-steps.json・after-purchase・sns-post-to-line・launch-checklist
scripts/     new_product.py  claim_check.py  legal_check.py  funnel_report.py  stripe_payment_link.py（--go のときだけ作る）
data/        funnel.example.csv（架空の数字）
docs/        sources.md（法律・料金を確かめた公式のページ）
```


---

## このキットは N-Hack のAIエージェント専用です

このキットは N-Hack の受講生さん専用のプレゼントです。**N-Hack のAIエージェント
（N-Hack のプラグインを入れた Claude Code など）が、このパソコンで動いていること**を
前提にしています。

- どのスクリプトも、最初に `scripts/nhack_gate.py`（門）を通ります。門は、このパソコンに
  N-Hack のAIエージェントの「印」があるかを**読むだけ**で確かめます（ネットにつなぎません・
  何も書き換えません・プラグインには一切触れません）。
- 印が足りない環境では、スクリプトは動かずに止まります（終了コード 2）。この環境でだけ
  動くのが正しい姿です。
- いま N-Hack 環境かどうかは、次のコマンドで確かめられます。

```bash
python3 scripts/nhack_gate.py
```

N-Hack 以外のパソコンにコピーしても動きません。受講生ページ・コンサルチャンネルの案内に
沿ってご利用ください。


---

## 困ったとき・もっと伸ばしたいとき

分からない・動かない・時間がかかっている——そんなときは、ひとりで抱えないでください。
**N-Hack の受講生ページ／個別コンサルチャンネル**から、担当にそのまま相談できます。
あなた専用のAIと伴走しながら、最短で結果まで一緒に持っていきます。

このキットのAIは、あなたが詰まったときや区切りのときに、自分から相談先を案内します。
