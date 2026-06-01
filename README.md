# paper-agent

Q1/Q2 ジャーナル掲載論文のみを引用した日本語学術論文ドラフトを生成し、Word (.docx) 形式で出力する半自動エージェント（Claude Code プロジェクト）。

## セットアップ

```bash
pip install -r requirements.txt
```

`data/sjr_2025.csv` を [Scimago](https://www.scimagojr.com/journalrank.php) からダウンロードして配置してください。

詳細は `manuals/user_guide.md` を参照してください。

## 使い方

```
/load <project_name>           # CP0: 入力解析
/search <project_name>         # CP1: 文献検索・Q1/Q2 フィルタ
/outline <project_name>        # CP2: アウトライン生成
/draft <project_name>          # CP3: 本文執筆
/review-packet <project_name>  # CP4: AI レビュー
/integrate-review <project_name>
/factcheck-packet <project_name>  # CP5: Factcheck
/integrate-factcheck <project_name>
/export <project_name>         # CP7: Word 出力
```

入力テンプレート: `projects/template/input/input.md`

## ドキュメント

### マニュアル (`manuals/`)
- [`quickstart.md`](manuals/quickstart.md) — クイックスタート（最短手順）
- [`user_guide.md`](manuals/user_guide.md) — セットアップ・各チェックポイント操作・トラブルシューティング
- [`review_workflow.md`](manuals/review_workflow.md) — マルチ AI レビュー（ChatGPT / Gemini）の手順
- [`notebooklm_workflow.md`](manuals/notebooklm_workflow.md) — NotebookLM による Factcheck の手順

### 設計仕様書 (`docs/`)
- [`構成仕様書_v1.2.md`](docs/構成仕様書_v1.2.md) — システム全体の設計仕様（アーキテクチャ・各コンポーネント・チェックポイント設計）
