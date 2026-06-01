---
description: "CP3: 本文・Abstract・Keywords を執筆する（引用 ID 検証付き）"
---

プロジェクト名: **$ARGUMENTS**

CP3（ドラフト執筆）を実行する。

## 前提確認

`progress.yaml` を読む。
- `cp2_done: false` なら「先に `/outline $ARGUMENTS` を実行してください」と伝えて停止する。
- `cp3_sections_done` に既に完了セクションがある場合は、`cp3_sections_pending` の先頭から再開する（クラッシュ回復）。

## 入力を読み込む

- `projects/$ARGUMENTS/checkpoints/cp0_input.yaml` — 研究要素
- `projects/$ARGUMENTS/checkpoints/cp2_outline.md` — アウトライン
- `projects/$ARGUMENTS/checkpoints/cp1_references.md` — 承認済み引用候補（ID: R1, R2, ...）
- `projects/$ARGUMENTS/config.yaml` — 設定（文字数、言語など）

## 引用 ID 制約（必ず守ること）

**`cp1_references.md` に記載された ID（R1, R2, ...）以外の引用 ID を絶対に生成しないこと。**
引用は `[REF: R1]`、`[REF: R2]` 形式のみ使用する。

## セクション別執筆

writer エージェントを呼び出し、`cp3_sections_pending` のセクションを順番に執筆する。
各セクション完了後に以下を実行する:

1. **引用 ID 検証**: 出力テキスト中の `[REF: Rx]` を全抽出し、`cp1_references.md` の ID 列と照合する。
   存在しない ID が1件でもあれば警告を出してセクションを再生成する（最大2回リトライ）。
   2回リトライ後も失敗する場合は、該当 ID を削除して続行し `error_log` に記録する。

2. **progress.yaml を更新**:
   ```yaml
   cp3_sections_done: [..., "<完了したセクション名>"]
   cp3_sections_pending: ["<残りのセクション>", ...]
   last_updated: "<現在時刻>"
   ```

## Abstract・Keywords の生成

本文セクション完了後、writer エージェントで以下を生成する:
- **Abstract**: `config.abstract_chars` 字以内（デフォルト250字）、全体の研究を要約
- **Keywords**: 5〜8語（分野の標準的なキーワード）

## 最終ドラフト出力

全セクションを結合して `projects/$ARGUMENTS/checkpoints/cp3_draft_v1.md` に保存する:

```markdown
# <タイトル>

**著者**: （ユーザーが後で記入）
**所属**: （ユーザーが後で記入）

## Abstract
<Abstract テキスト>

**Keywords**: keyword1, keyword2, ...

## 1. Introduction
<本文>

## 2. Methods
...

## 5. Conclusion
...
```

## progress.yaml を更新する

```yaml
current_cp: 3
cp3_sections_done: [introduction, methods, results, discussion, conclusion, abstract, keywords]
cp3_sections_pending: []
last_updated: "<現在時刻>"
```

## 完了報告

各セクションの文字数と合計文字数を出力する。目標文字数（`config.body_chars`）との差も表示する。
次のステップ: `/review-packet $ARGUMENTS`
