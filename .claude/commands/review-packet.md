---
description: "CP4: Claude 自動レビュー実行 + ChatGPT・Gemini 用パケット生成"
---

プロジェクト名: **$ARGUMENTS**

CP4（マルチ AI レビュー）を実行する。

## 前提確認

`progress.yaml` の `cp3_sections_pending` が空（全セクション完了）でなければ
「先に `/draft $ARGUMENTS` を完了させてください」と伝えて停止する。

## 手順

**1. レビューパケットディレクトリを作成する**

`projects/$ARGUMENTS/checkpoints/cp4_review_packet/` を作成し、以下の構成にする:
```
cp4_review_packet/
├── draft_v1.md          ← cp3_draft_v1.md のコピー
├── prompts/
│   ├── chatgpt.md
│   └── gemini.md
├── results/
│   ├── claude.md        ← 自動生成（このコマンドで作成）
│   ├── chatgpt.md       ← 空（ユーザーが記入）
│   └── gemini.md        ← 空（ユーザーが記入）
└── instructions.md
```

**2. Claude 自動レビューを実行する（reviewer エージェント）**

reviewer エージェントを呼び出し、`draft_v1.md` を評価させる。
出力を `results/claude.md` に保存する。

評価観点:
- IMRaD 構成の論理的一貫性
- 主張と根拠の対応
- 文体・冗長性（学術文体として）
- 致命的問題には `[CRITICAL]` タグを付ける

**3. ChatGPT・Gemini 用プロンプトを生成する**

`prompts/chatgpt.md`:
````markdown
あなたは理学・工学分野の国際ジャーナル査読者です。

以下の論文ドラフトについて、**学術的正確性と先行研究の網羅性**の観点でレビューしてください。

評価観点:
- 重要な先行研究の欠落
- 専門用語・概念定義の正確性
- 研究の新規性の主張が適切か

出力形式（必ずこの形式で回答してください）:
- 全体評価: 1〜5（5が最高）
- 主要な指摘:
  - セクション名 / 指摘内容 / 修正提案
- 致命的な問題: （あれば [CRITICAL] タグ付き）
- 良い点: （1〜3件）

---
<draft_v1.md の全文をここに貼り付けてください>
````

`prompts/gemini.md`:
````markdown
あなたは統計・データ解析の専門家です。

以下の論文ドラフトについて、**統計的記述とデータ解釈の妥当性**の観点でレビューしてください。

評価観点:
- 数値・統計値の表現の適切さ
- データ解釈の論理的妥当性
- 不確かさ・誤差の記述
- 因果関係と相関関係の混同

出力形式（必ずこの形式で回答してください）:
- 全体評価: 1〜5（5が最高）
- 主要な指摘:
  - セクション名 / 指摘内容 / 修正提案
- 致命的な問題: （あれば [CRITICAL] タグ付き）
- 良い点: （1〜3件）

---
<draft_v1.md の全文をここに貼り付けてください>
````

**4. instructions.md を生成する**

`instructions.md` の内容:
```markdown
# CP4: マルチ AI レビュー 操作手順

## Claude レビュー（完了）
`results/claude.md` を確認してください。

## ChatGPT レビュー
1. https://chat.openai.com にアクセス（GPT-4o 推奨）
2. `prompts/chatgpt.md` の内容をコピー
3. 末尾の指示に従い `draft_v1.md` の全文を貼り付けて送信
4. 回答を `results/chatgpt.md` に保存

## Gemini レビュー
1. https://gemini.google.com にアクセス
2. `prompts/gemini.md` の内容をコピー
3. `draft_v1.md` の全文を貼り付けて送信
4. 回答を `results/gemini.md` に保存

## 完了後
3つのファイルがすべて埋まったら Claude Code に戻り:
/integrate-review $ARGUMENTS
```

**5. ユーザーへの案内**

`results/claude.md` の内容（Claude 自動レビュー結果）を表示する。
その後、`instructions.md` の手順を案内する。

**6. progress.yaml を更新する**

```yaml
current_cp: 4
cp4_done: false  # integrate-review 完了後に true になる
```
