# paper-agent アーキテクチャ概要

## フォルダ構成と役割

```
paper-agent/
├── CLAUDE.md                   Claude Code 起動時に自動ロードされる操作ガイド
├── README.md                   プロジェクト概要・セットアップ手順・コマンド一覧
├── requirements.txt            Python 依存パッケージ（pyyaml / python-docx / requests）
├── .gitignore                  研究データ・PDF・SJR CSV・config.py を除外するルール
│
├── .claude/
│   ├── commands/               スラッシュコマンド定義（/load〜/export、計9本）
│   │   ├── load.md             CP0: 入力ファイルを解析し cp0_input.yaml を生成
│   │   ├── search.md           CP1: OpenAlex 検索・Q1/Q2 フィルタ・BibTeX 取得
│   │   ├── outline.md          CP2: IMRaD アウトライン生成
│   │   ├── draft.md            CP3: 本文・Abstract・Keywords 執筆（引用 ID 検証付き）
│   │   ├── review-packet.md    CP4: Claude 自動レビュー + 外部 AI 用パケット生成
│   │   ├── integrate-review.md CP4後: 3AI レビュー結果を本文に統合（diff 提示）
│   │   ├── factcheck-packet.md CP5: 引用主張を抽出・OA PDF 取得・NotebookLM パケット生成
│   │   ├── integrate-factcheck.md CP5後: Factcheck 結果を本文に統合
│   │   └── export.md           CP7: 引用変換・参考文献付加・.docx 出力
│   │
│   ├── agents/                 サブエージェント定義（システムプロンプト）
│   │   ├── outliner.md         研究要素から IMRaD アウトラインを生成するエージェント
│   │   ├── writer.md           アウトライン + 研究要素から本文を執筆するエージェント
│   │   ├── reviewer.md         論理構成・文体を批判的にレビューする Claude 自動レビューエージェント
│   │   └── integrator.md       レビュー・Factcheck 結果を diff 形式で本文に統合するエージェント
│   │
│   ├── skills/                 スキル定義（Python スクリプトの呼び出し方を説明）
│   │   ├── sjr-filter/SKILL.md SJR CSV で Q1/Q2 判定するスキル
│   │   ├── citation/SKILL.md   BibTeX → 指定スタイルの参考文献リスト生成スキル
│   │   └── docx-export/SKILL.md Markdown → .docx 変換スキル
│   │
│   └── mcp.json                Exa MCP サーバー設定（補完検索用、API キーは別途設定）
│
├── scripts/                    Python バックエンド（各スラッシュコマンドから呼び出される）
│   ├── config.example.py       設定テンプレート → config.py にコピーして MAILTO_EMAIL を設定
│   ├── search_openalex.py      OpenAlex API 主検索・ブースト・Q1/Q2 フィルタ・候補リスト生成
│   ├── sjr_filter.py           SJR CSV から Quartile 判定（ISSN 優先 / Levenshtein 誌名正規化）
│   ├── bib_fetcher.py          CrossRef API から DOI → BibTeX を一括取得
│   ├── pdf_fetcher.py          OpenAlex OA リンクから PDF を自動ダウンロード（PDF 実体検証付き）
│   ├── citation_format.py      [REF: Rx] を APA/IEEE 等の実形式に置換・参考文献リスト生成
│   ├── docx_export.py          Markdown ドラフト → python-docx で .docx 出力（テンプレート対応）
│   ├── resolve_refs.py         著者・年・ヒントから CrossRef で DOI を解決（既存引用の補完）
│   ├── resolve_extra.py        レビュー推奨文献を CrossRef で解決・Quartile 確認
│   ├── cp1_run.py              CP1 一括実行オーケストレーター（既存引用補完 + 検索 + フィルタ + マージ）
│   ├── cp1_append.py           CP1 候補リストへ検証済み文献を追加
│   ├── cp1_finalize.py         CP1 候補リストの不要文献削除・再採番・確定
│   ├── cp7_finalize.py         CP7 引用変換・ナラティブ重複除去・参考文献リスト付加
│   ├── build_claims.py         CP5 本文から引用主張を抽出して claims.md / results.md テンプレート生成
│   ├── pdf_coverage.py         CP5 引用文献の PDF カバレッジをレポート・missing_pdfs.md 更新
│   ├── add_abbr.py             journal_abbr.json へ誌名略語エントリを追加
│   └── verify_refs.py          ドラフト内の [REF: Rx] が候補リストの有効 ID かを検証（捏造防止）
│
├── data/
│   ├── journal_abbr.json       誌名略語 → 正式名の辞書（約100誌収録、add_abbr.py で追加可能）
│   └── sjr_YYYY.csv            ※gitignore。scimagojr.com から手動配置する Quartile データ
│
├── templates/                  ※gitignore。学会指定 Word テンプレート（.docx）を配置する場所
│
├── docs/
│   ├── 構成仕様書_v1.2.md      システム全体の設計仕様書（アーキテクチャ・CP 設計・各コンポーネント仕様）
│   ├── spec_final.pdf          最終仕様書（PDF）
│   ├── security_guide.pdf      セキュリティ説明書（PDF）
│   └── operations_guide.pdf    運用説明書（PDF）
│
├── manuals/
│   ├── quickstart.md           最短手順クイックスタート（コマンド表・フロー図）
│   ├── user_guide.md           セットアップ・各 CP 操作・エラー回復・トラブルシューティング
│   ├── review_workflow.md      ChatGPT / Gemini レビュー操作手順（Human-in-the-loop）
│   └── notebooklm_workflow.md  NotebookLM ファクトチェック操作手順
│
└── projects/                   ※gitignore（研究データ・PDF・BibTeX はリモートに上がらない）
    └── template/
        └── input/input.md      論文入力ファイルのテンプレート（Theme / Background / Methods ...）
```

## ワークフロー（CP0〜CP7）

```
/load    CP0  入力解析・config.yaml / progress.yaml 初期化
/search  CP1  OpenAlex 主検索 → boost_journals 追加検索 → Q1/Q2 フィルタ
              → CrossRef で BibTeX 取得 → cp1_references.md / .bib 確定
/outline CP2  研究要素 + 引用候補 → IMRaD アウトライン（ユーザー確認）
/draft   CP3  writer エージェントがセクション別に執筆 → 引用 ID 検証（verify_refs.py）
              → Abstract / Keywords 生成 → cp3_draft_v1.md
/review-packet    CP4  reviewer エージェントが自動レビュー（results/claude.md）
                       + ChatGPT・Gemini 用プロンプト生成（Human-in-the-loop）
/integrate-review     → 3AI 結果を integrator エージェントが diff 統合
/factcheck-packet CP5  build_claims.py で引用主張抽出 → OA PDF ダウンロード
                       → NotebookLM 用パケット生成（Human-in-the-loop）
/integrate-factcheck  → PARTIAL / NOT_SUPPORTED を本文に反映
/export  CP7  cp7_finalize.py で引用変換・参考文献付加 → docx_export.py で .docx 出力
```

## 主要コンポーネントの依存関係

```
OpenAlex API ──────→ search_openalex.py ──┬→ sjr_filter.py     → cp1_references.md
                                           ├→ bib_fetcher.py    → cp1_references.bib
                                           └→ pdf_fetcher.py    → pdfs/

.claude/agents/writer.md ──────────────────→ cp3_draft_v1.md
                                               ↓ build_claims.py → claims.md
                                               ↓ NotebookLM      → results.md
                                               ↓ cp7_finalize.py → cp7_final.md
                                                                     ↓ docx_export.py
                                                                       → output.docx
```

## 設計原則

| 原則 | 内容 |
|---|---|
| **引用捏造防止** | `verify_refs.py` が `[REF: Rx]` を候補リスト ID と照合。無効 ID はリジェクト |
| **チェックポイント駆動** | `progress.yaml` で進捗管理。中断後も同コマンド再実行で再開 |
| **DOI 検証優先** | 文献は必ず CrossRef で DOI・タイトル・年を実在確認してから採用 |
| **Human-in-the-loop** | ChatGPT・Gemini レビューと NotebookLM Factcheck はユーザーが手動実施 |
| **API コスト最小** | OpenAlex / CrossRef は無料 API。Exa は補完用途のみで無料枠内 |
