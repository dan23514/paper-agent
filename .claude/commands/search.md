---
description: "CP1: OpenAlex で文献検索、Q1/Q2 フィルタ、BibTeX 取得"
---

プロジェクト名: **$ARGUMENTS**

CP1（文献検索 + Q1/Q2 フィルタ）を実行する。

## 前提確認

`projects/$ARGUMENTS/checkpoints/progress.yaml` を読み、`cp0_done: true` でなければ
「先に `/load $ARGUMENTS` を実行してください」と伝えて停止する。

## 手順

**1. OpenAlex 検索 + Q1/Q2 フィルタ（Python スクリプト）**

```bash
python scripts/search_openalex.py \
  projects/$ARGUMENTS/checkpoints/cp0_input.yaml \
  projects/$ARGUMENTS/config.yaml
```

このスクリプトは以下を生成する:
- `projects/$ARGUMENTS/checkpoints/cp1_references.md` — 候補リスト（Markdown テーブル）
- `projects/$ARGUMENTS/checkpoints/cp1_references.json` — 候補リスト（JSON）
- `projects/$ARGUMENTS/checkpoints/cp1_dois.txt` — DOI リスト

`data/sjr_YYYY.csv` が存在しない場合は以下を案内して停止する:
> `data/sjr_2025.csv` が見つかりません。
> https://www.scimagojr.com/journalrank.php から CSV をダウンロードし `data/sjr_2025.csv` として配置してください。

**2. BibTeX 取得（CrossRef API）**

```bash
python scripts/bib_fetcher.py \
  projects/$ARGUMENTS/checkpoints/cp1_dois.txt \
  projects/$ARGUMENTS/checkpoints/cp1_references.bib \
  projects/$ARGUMENTS/checkpoints/cp1_missing_bibtex.md
```

**3. 結果を表示してユーザー確認を求める**

`projects/$ARGUMENTS/checkpoints/cp1_references.md` の内容を表示する。

ユーザーへの案内:
- ファイルを直接編集して不要な行を削除・追加可能
- 承認後は `/outline $ARGUMENTS` を実行

**4. progress.yaml を更新する**

```yaml
current_cp: 1
cp1_done: true
last_updated: "<現在時刻>"
```
