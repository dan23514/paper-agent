# マルチ AI レビュー ワークフロー

## 概要

`/review-packet` で生成されたパケットを使い、ChatGPT・Gemini のレビューを取得する手順です。
Claude のレビューは `/review-packet` 実行時に自動完了します。

---

## 手順

### 1. `/review-packet` を実行する

```
/review-packet my-paper
```

実行後、以下が生成されます:
- `cp4_review_packet/results/claude.md` — Claude 自動レビュー（完了済み）
- `cp4_review_packet/prompts/chatgpt.md` — ChatGPT 用プロンプト
- `cp4_review_packet/prompts/gemini.md` — Gemini 用プロンプト

Claude のレビュー内容を確認してください。

### 2. ChatGPT レビュー

1. https://chat.openai.com にアクセス（GPT-4o 推奨）
2. `cp4_review_packet/prompts/chatgpt.md` を開く
3. ファイルの全文をコピーして ChatGPT に貼り付ける
4. プロンプト末尾の指示に従い `draft_v1.md` の全文を追加して送信
5. 回答を `cp4_review_packet/results/chatgpt.md` に保存

### 3. Gemini レビュー

1. https://gemini.google.com にアクセス（Gemini 1.5 Pro 推奨）
2. `cp4_review_packet/prompts/gemini.md` を開く
3. ファイルの全文をコピーして Gemini に貼り付ける
4. `draft_v1.md` の全文を追加して送信
5. 回答を `cp4_review_packet/results/gemini.md` に保存

### 4. Claude Code に戻る

3つの `results/` ファイルがすべて埋まったら:

```
/integrate-review my-paper
```

---

## レビュー結果の保存形式

各 `results/<ai_name>.md` は以下の形式で保存してください
（AI の出力がこの形式でなくても `/integrate-review` が処理します）:

```markdown
## 全体評価: X / 5

## 主要な指摘
- セクション名 / 指摘内容 / 修正提案
- ...

## 致命的な問題
（あれば）

## 良い点
1. ...
```

---

## 注意事項

- ドラフト全文を貼り付けるとトークン数が多くなります。ChatGPT・Gemini の無料枠でのトークン制限に注意してください
- レビュー結果は貼り付け時に改行・フォーマットが崩れることがあります。大まかな内容が保存されていれば問題ありません
- `/integrate-review` が指摘内容を正規化して処理します
