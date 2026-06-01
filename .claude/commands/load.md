---
description: "CP0: 入力ファイルを解析し研究要素を抽出する"
---

プロジェクト名: **$ARGUMENTS**

CP0（入力受領）を実行する。

## 手順

**1. 入力ファイルを読み込む**

`projects/$ARGUMENTS/input/` 内のファイルを探す（input.md → input.yaml → input.docx の優先順）。
ファイルが存在しない場合はエラーを出力して停止する。

**2. 研究要素を抽出して `projects/$ARGUMENTS/checkpoints/cp0_input.yaml` に保存する**

以下の構造で出力する:
```yaml
theme: ""
background: ""
methods: ""
data: ""
results: ""
interpretation: ""
config:
  citation_target_journal: ""
  boost_journals: []
  citation_style: "IEEE"
  length:
    abstract_chars: 250
    body_chars: 8000
```

**3. 必須フィールドの欠損チェック**

theme / background / methods / data / results / interpretation のうち空のものがあれば
`⚠️ 欠損フィールド: <フィールド名>` として警告を出力する。

**4. `projects/$ARGUMENTS/checkpoints/progress.yaml` を初期化する**

ファイルが存在しない場合のみ作成する:
```yaml
project: "$ARGUMENTS"
current_cp: 0
cp0_done: true
cp1_done: false
cp2_done: false
cp3_sections_done: []
cp3_sections_pending: [introduction, methods, results, discussion, conclusion, abstract, keywords]
cp4_done: false
cp5_done: false
cp6_done: false
cp7_done: false
last_updated: "<現在時刻 ISO 8601>"
error_log: []
```

**5. `projects/$ARGUMENTS/config.yaml` が存在しない場合、デフォルト設定で生成する**

```yaml
field: science_engineering
literature:
  search_years: 10
  max_candidates: 20
  openalex_target: 30
  quartile_filter: [Q1, Q2]
  on_no_match: exclude
  boost_journals: []
  target_boost: 1.5
  reserve_slots: 5
  max_target_citation_ratio: 0.4
  bypass_sjr_for_targets: false
  expand_citation_network: false
review:
  enabled_ais: [claude, chatgpt, gemini]
  assignments:
    logic: claude
    style: claude
    accuracy: chatgpt
    statistics: gemini
factcheck:
  on_unverifiable: flag
export:
  format: docx
  template: ""
  font_family_jp: 游明朝
  font_family_en: Times New Roman
  font_size_body: 10.5
  font_size_heading: 12
  line_spacing: 1.5
  paper_size: A4
  margin_mm: 25
  column: 1
  citation_style: IEEE
  citation_target_journal: ""
```

## 完了報告

以下を出力する:
- 抽出した各フィールドの先頭50字サマリー
- 欠損フィールドの警告（あれば）
- 次のステップ: `/search $ARGUMENTS`
