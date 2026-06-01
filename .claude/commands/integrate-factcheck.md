---
description: "CP5後: NotebookLM の Factcheck 結果を本文に統合する"
---

プロジェクト名: **$ARGUMENTS**

Factcheck 結果を本文に統合する（CP5 → CP6 への移行）。

## 前提確認

`projects/$ARGUMENTS/checkpoints/cp5_factcheck_packet/results.md` が存在し、
Verdict 列に値が入っていることを確認する。空の場合は NotebookLM 作業の完了を促して停止する。

## 手順

**1. Factcheck 結果を解析する**

`results.md` の各行について:
- `SUPPORTED` → 変更なし
- `PARTIAL` → 主張の表現を慎重に弱める修正案を生成
- `NOT_SUPPORTED` → 以下のいずれかを提案:
  a. 引用を削除（主張が他の引用で支持される場合）
  b. 表現を緩和（「〜が示唆される」などの推測表現に変更）
  c. 別文献での代替提案（`cp1_references.md` 内で代替可能なものがあれば）
- `config.on_unverifiable: flag` の場合 → 「未検証」フラグを付けてユーザー判断に委ねる

**2. 最新ドラフトを読み込む**

`cp6_draft_v2_review.md` が存在すればそれを使用、なければ `cp3_draft_v1.md` を使用する。

**3. 修正案を diff 形式でユーザーに提示する**

```
### Factcheck 修正 #1
**引用**: [REF: R2]（Tanaka et al. 2023）
**Verdict**: NOT_SUPPORTED
**Evidence**: 該当箇所なし

提案: 引用を削除して表現を一般化
- Before: 「本手法は従来比50%の精度向上を達成した [REF: R2]。」
+ After:  「本手法は従来比50%の精度向上を達成した（詳細は Discussion 参照）。」

承認しますか？ [y/n]
```

**4. 承認された修正を適用して最終ドラフト `cp6_draft_v2.md` を生成する**

保存先: `projects/$ARGUMENTS/checkpoints/cp6_draft_v2.md`

**5. `revision_report.md` を更新する**

Factcheck 統合の結果を追記する:
- NOT_SUPPORTED → 対応内容
- PARTIAL → 修正内容
- 未検証フラグ一覧

**6. progress.yaml を更新する**

```yaml
current_cp: 6
cp5_done: true
cp6_done: true
```

## 完了報告

- 変更箇所の数（SUPPORTED / PARTIAL / NOT_SUPPORTED の内訳）
- `cp6_draft_v2.md` の総文字数
- 次のステップ: `/export $ARGUMENTS`
