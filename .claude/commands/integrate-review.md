---
description: "CP4後: 3つのAIレビュー結果を本文に統合する"
---

プロジェクト名: **$ARGUMENTS**

レビュー結果を本文に統合する（CP4 → CP6 への移行）。

## 前提確認

以下の3ファイルが存在し、空でないことを確認する:
- `projects/$ARGUMENTS/checkpoints/cp4_review_packet/results/claude.md`
- `projects/$ARGUMENTS/checkpoints/cp4_review_packet/results/chatgpt.md`
- `projects/$ARGUMENTS/checkpoints/cp4_review_packet/results/gemini.md`

不足しているファイルがあれば、その旨を伝えて停止する。

## 手順

**1. integrator エージェントを呼び出してレビューを統合する**

integrator エージェントへの入力:
- `cp3_draft_v1.md` — 元のドラフト
- `cp4_review_packet/results/claude.md` — Claude レビュー
- `cp4_review_packet/results/chatgpt.md` — ChatGPT レビュー
- `cp4_review_packet/results/gemini.md` — Gemini レビュー

統合ロジック:
- `[CRITICAL]` タグ付きの指摘 → 必ず対応
- 2つ以上の AI が同じ箇所を指摘 → 高優先度として必ず対応
- 単一 AI の指摘 → diff 形式でユーザーに提示し選択を求める

**2. 修正案を diff 形式で提示する**

各修正について以下の形式で表示する:
```
### 修正 #1（[CRITICAL] / 高優先度 / 任意）
**指摘**: <指摘内容>（出典: Claude / ChatGPT / Gemini）
**対象箇所**: <セクション名、引用文>

- Before: <変更前テキスト>
+ After:  <変更後テキスト>

承認しますか？ [y/n]
```

ユーザーの承認/却下を記録する。

**3. 承認された修正を適用して `cp6_draft_v2_review.md` を生成する**

（Factcheck 統合前の中間ファイル）

**4. `revision_report.md` を生成する**

```markdown
# レビュー統合レポート

## 適用した修正
- #1: ... ✓
- #3: ... ✓

## スキップした修正
- #2: ... (ユーザーが却下)

## 未対応の指摘（参考）
...
```

保存先: `projects/$ARGUMENTS/checkpoints/cp6_revision_report.md`

**5. progress.yaml を更新する**

```yaml
cp4_done: true
```

次のステップ: `/factcheck-packet $ARGUMENTS`（未実施の場合）または `/integrate-factcheck $ARGUMENTS`
