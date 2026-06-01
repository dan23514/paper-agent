# ユーザーガイド

## 初回セットアップ

### 1. Python 環境

Python 3.10 以上が必要です。

```bash
pip install -r requirements.txt
```

### 2. SJR データの配置

1. https://www.scimagojr.com/journalrank.php にアクセス
2. 右下の「Download data」ボタンをクリック
3. ダウンロードした CSV を `data/sjr_2025.csv` として保存
   - ファイル名の年は実際のデータ年に合わせる（例: `sjr_2024.csv`）
   - 区切り文字はセミコロン（`;`）であることを確認

### 3. Exa API キーの設定（任意）

補完検索が必要な場合のみ設定します（OpenAlex だけで通常は十分）。

1. https://exa.ai から API キーを取得
2. `.claude/mcp.json` の `<EXA_API_KEY>` を実際のキーに置換

---

## 新しい論文プロジェクトの作成

### 1. 入力ファイルを作成する

```
projects/<project_name>/input/input.md
```

テンプレートをコピーして記入します:
```bash
cp projects/template/input/input.md projects/my-paper/input/input.md
```

### 2. 入力フォーマット

```markdown
# Theme
研究のタイトル候補

# Background
研究背景（200〜800字）

# Methods
- 使用した手法・実験条件

# Data
- データの概要

# Results
主要な結果

# Interpretation
結果の解釈・考察の方向性

# Config
citation_target_journal: "投稿先ジャーナル名"
boost_journals:
  - name: "優先的に引用したいジャーナル名"
    issn: "XXXX-XXXX"
citation_style: IEEE   # IEEE / ACS / AIP / Nature / Vancouver / APA
```

---

## チェックポイント別の操作手順

### CP0: 入力受領
```
/load my-paper
```
- 入力ファイルを解析して `checkpoints/cp0_input.yaml` を生成
- `config.yaml`（設定ファイル）と `progress.yaml`（進捗管理）を初期化

### CP1: 文献検索
```
/search my-paper
```
- OpenAlex API で関連論文を検索（通常30秒〜2分）
- SJR データで Q1/Q2 フィルタを適用
- `checkpoints/cp1_references.md` を確認・編集して不要な論文を削除

**Q1/Q2 フィルタで候補が少なすぎる場合:**
- `config.yaml` の `on_no_match: include` に変更（SJR 未収録誌を許容）
- または `boost_journals` に関連誌を追加

### CP2: アウトライン生成
```
/outline my-paper
```
- `checkpoints/cp2_outline.md` を確認・編集
- セクション構成・引用割り当てを調整してから次へ進む

### CP3: ドラフト執筆
```
/draft my-paper
```
- 各セクションを順番に執筆（通常5〜15分）
- 途中で中断しても再実行で再開可能

### CP4: マルチ AI レビュー
```
/review-packet my-paper
```
- Claude レビューが自動実行され `results/claude.md` が生成される
- ChatGPT・Gemini への手動投稿手順は `cp4_review_packet/instructions.md` を参照
- 外部 AI のレビューが完了したら:
  ```
  /integrate-review my-paper
  ```

### CP5: Factcheck
```
/factcheck-packet my-paper
```
- OA PDF の自動ダウンロードを試みる
- `missing_pdfs.md` に記載された PDF を手動で `pdfs/` に追加
- NotebookLM 操作手順は `cp5_factcheck_packet/instructions.md` を参照
- Factcheck 完了後:
  ```
  /integrate-factcheck my-paper
  ```

### CP7: Word 出力
```
/export my-paper
```
- `checkpoints/cp7_output.docx` が生成される

---

## エラー回復

中断した場合は同じコマンドを再実行してください。
`checkpoints/progress.yaml` を参照して未完了箇所から再開します。

特定の CP に巻き戻すには `progress.yaml` を直接編集:
```yaml
current_cp: 2   # ← ここを変更
cp3_sections_done: []
cp3_sections_pending: [introduction, methods, results, discussion, conclusion, abstract, keywords]
```

---

## 設定のカスタマイズ

`projects/<name>/config.yaml` を編集して動作を調整できます。

主要なパラメータ:

| パラメータ | 説明 | デフォルト |
|---|---|---|
| `literature.max_candidates` | 引用候補の最大件数 | 20 |
| `literature.search_years` | 検索対象の年数 | 10 |
| `literature.target_boost` | ブーストジャーナルの優先度倍率 | 1.5 |
| `draft.length.body_chars` | 本文目標文字数 | 8000 |
| `draft.length.abstract_chars` | Abstract 目標文字数 | 250 |
| `export.citation_style` | 引用スタイル | IEEE |
| `export.template` | 学会テンプレート（空欄なら自動設定） | （空） |

---

## トラブルシューティング

### SJR CSV が読み込めない
- `data/sjr_YYYY.csv` のファイル名の年が一致しているか確認
- CSV の区切り文字がセミコロン（`;`）であるか確認
- `scripts/sjr_filter.py "Physical Review Letters"` で動作確認

### OpenAlex で候補が少ない
- テーマ・手法のキーワードをより一般的な英語表現に変更
- `config.yaml` の `search_years` を増やす（例: 15）

### python-docx が見つからない
```bash
pip install python-docx
```
