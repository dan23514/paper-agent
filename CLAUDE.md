# 論文執筆エージェント

Q1/Q2 ジャーナル掲載論文のみを引用した日本語学術論文ドラフトを生成し、Word (.docx) 形式で出力する半自動エージェント。

## 初回セットアップ（一度だけ）

1. Python 依存関係をインストール
   ```
   pip install -r requirements.txt
   ```

2. SJR CSV を配置
   - https://www.scimagojr.com/journalrank.php から全件 CSV をダウンロード
   - `data/sjr_2025.csv` として保存（区切り文字はセミコロン）

3. Exa API キーを設定（補完検索が必要な場合）
   - `.claude/mcp.json` の `<EXA_API_KEY>` を実際のキーに置換

## 基本的な使い方

新しい論文プロジェクトを開始する手順:

1. `projects/<project_name>/input/input.md` を作成（テンプレート: `projects/template/input/input.md`）
2. 以下のコマンドを順に実行する

| コマンド | CP | 処理内容 |
|---|---|---|
| `/load <project_name>` | CP0 | 入力解析・初期化 |
| `/search <project_name>` | CP1 | OpenAlex 検索・Q1/Q2 フィルタ・BibTeX 取得 |
| `/outline <project_name>` | CP2 | IMRaD アウトライン生成 |
| `/draft <project_name>` | CP3 | 本文・Abstract・Keywords 執筆 |
| `/review-packet <project_name>` | CP4 | Claude 自動レビュー + 外部 AI 用パケット生成 |
| `/integrate-review <project_name>` | — | レビュー結果を本文に統合 |
| `/factcheck-packet <project_name>` | CP5 | OA PDF ダウンロード + NotebookLM 用パケット生成 |
| `/integrate-factcheck <project_name>` | — | Factcheck 結果を本文に統合 |
| `/export <project_name>` | CP7 | Word (.docx) 出力 |

## エラー回復

途中で中断した場合は同じコマンドを再実行する。
`projects/<name>/checkpoints/progress.yaml` を参照して未完了の箇所から再開する。
特定の CP に巻き戻すには `progress.yaml` の `current_cp` を手動で編集する。

## ディレクトリ構成

```
paper-agent/
├── .claude/
│   ├── commands/       スラッシュコマンド（/load, /search, ...）
│   ├── agents/         サブエージェント定義（writer, reviewer, ...）
│   ├── skills/         スキル定義（sjr-filter, citation, docx-export）
│   └── mcp.json        Exa MCP 設定
├── data/
│   ├── sjr_2025.csv    SJR データ（手動配置・年次更新）
│   └── journal_abbr.json  誌名略語辞書
├── scripts/            Python バックエンド
├── templates/          学会指定 Word テンプレート（オプション）
├── projects/           論文ごとのワークスペース
└── manuals/            操作マニュアル
```

## スクリプト一覧

| スクリプト | 役割 |
|---|---|
| `scripts/search_openalex.py` | OpenAlex 検索・Q1/Q2 フィルタ・ブースト |
| `scripts/sjr_filter.py` | SJR Quartile 判定（ISSN/誌名マッチング） |
| `scripts/bib_fetcher.py` | CrossRef API → BibTeX 取得 |
| `scripts/pdf_fetcher.py` | OpenAlex OA リンクから PDF ダウンロード |
| `scripts/citation_format.py` | [REF: Rx] → 番号置換・参考文献リスト生成 |
| `scripts/docx_export.py` | Markdown → .docx 変換 |
| `scripts/add_abbr.py` | 誌名略語辞書に追加登録 |
