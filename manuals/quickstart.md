# paper-agent クイックスタート

---

## 初回セットアップ（一度だけ）

```bash
# 1. paper-agent フォルダを Claude Code で開く
cd C:\Users\tkm14\OneDrive\Research\paper-agent

# 2. Python 依存関係をインストール
pip install -r requirements.txt

# 3. SJR データを配置
#    https://www.scimagojr.com/journalrank.php → 右下「Download data」
#    → data\sjr_2025.csv として保存
```

---

## 新しい論文を書くたびに

### Step 1: 入力ファイルを作成する

テンプレートをコピーして研究内容を記入する:

```
projects\template\input\input.md  ← コピー元
projects\<プロジェクト名>\input\input.md  ← ここに作成
```

| セクション | 内容 |
|---|---|
| `# Theme` | 研究タイトル候補 |
| `# Background` | 研究背景・課題（200〜800字） |
| `# Methods` | 手法・実験条件 |
| `# Data` | データの概要 |
| `# Results` | 主要な結果 |
| `# Interpretation` | 結果の解釈・考察の方向性 |
| `# Config` | 引用スタイル・目標文字数など |

### Step 2: コマンドを順番に実行する

```
/load <プロジェクト名>
```
入力ファイルを解析し、設定ファイルと進捗管理ファイルを初期化する。

---

```
/search <プロジェクト名>
```
OpenAlex で関連論文を検索し Q1/Q2 のみに絞り込む。BibTeX も自動取得。

> **要確認**: `checkpoints/cp1_references.md` を開いて不要な論文を削除する

---

```
/outline <プロジェクト名>
```
IMRaD 構成のアウトラインを生成する。

> **要確認**: `checkpoints/cp2_outline.md` を開いてセクション構成を調整する

---

```
/draft <プロジェクト名>
```
本文・Abstract・Keywords を執筆する（5〜15分）。途中中断しても再実行で再開可能。

---

```
/review-packet <プロジェクト名>
```
Claude が自動でレビューを実行する。ChatGPT・Gemini 用のプロンプトも生成される。

> **要作業**: 表示される手順に従い ChatGPT・Gemini にも投げ、結果をファイルに保存する
> 詳細手順 → `manuals/review_workflow.md`

---

```
/integrate-review <プロジェクト名>
```
3つの AI レビュー結果を本文に統合する。修正案を diff 形式で提示するので承認/却下を選ぶ。

---

```
/factcheck-packet <プロジェクト名>
```
引用論文の PDF を自動ダウンロードし、NotebookLM 用の検証パケットを生成する。

> **要作業**: NotebookLM で引用の裏付けを確認し結果を保存する
> 詳細手順 → `manuals/notebooklm_workflow.md`

---

```
/integrate-factcheck <プロジェクト名>
```
Factcheck 結果を本文に反映する（NOT_SUPPORTED の引用を修正）。

---

```
/export <プロジェクト名>
```
Word (.docx) ファイルを出力する。

**出力先**: `projects/<プロジェクト名>/checkpoints/cp7_output.docx`

---

## フロー全体図

```
input.md を作成
      ↓
/load              → cp0_input.yaml（研究要素の構造化）
      ↓
/search            → cp1_references.md ★確認・編集
      ↓
/outline           → cp2_outline.md ★確認・編集
      ↓
/draft             → cp3_draft_v1.md
      ↓
/review-packet
  Claude:              自動レビュー完了
  ChatGPT・Gemini:     手動で投げて結果を保存 ★
      ↓
/integrate-review  → diff を確認して承認/却下
      ↓
/factcheck-packet
  PDF 自動 DL → NotebookLM で検証 → 結果を保存 ★
      ↓
/integrate-factcheck → diff を確認して承認/却下
      ↓
/export            → cp7_output.docx ✓
```

---

## よくある操作

| やりたいこと | 操作 |
|---|---|
| 途中から再開する | 同じコマンドを再実行するだけ |
| CP2 からやり直す | `progress.yaml` の `current_cp: 2` に書き換えて `/outline` を実行 |
| 誌名略語を追加する | `python scripts/add_abbr.py "略称" "正式名称"` |
| 学会テンプレートを使う | `templates/` に .docx を置き `config.yaml` の `export.template` に指定 |
| 引用スタイルを変える | `config.yaml` の `export.citation_style` を `APA` / `Nature` などに変更 |
| 候補論文数を増やす | `config.yaml` の `literature.max_candidates` を増やす |
| 年代範囲を広げる | `config.yaml` の `literature.search_years` を増やす（例: `15`） |
