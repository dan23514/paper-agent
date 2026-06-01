---
name: sjr-filter
description: SJR CSV データを使って論文リストを Q1/Q2 のみにフィルタリングするスキル
---

## 概要

`scripts/sjr_filter.py` を呼び出して、論文リストの各エントリに対して Scimago Journal Rank の Quartile を取得し、Q1/Q2 のみを返す。

## 入力

- 論文リスト（Python dict のリスト）。各エントリは `issn` または `journal` キーを持つ
- `bypass_issns`: SJR フィルタをバイパスする ISSN のセット（`boost_journals` の ISSN）

## 処理

```python
import sys
sys.path.insert(0, 'scripts')
from sjr_filter import filter_q1_q2

filtered = filter_q1_q2(references, bypass_issns=bypass_issns)
```

## データソース

- `data/sjr_YYYY.csv`: [Scimago Journal Rank](https://www.scimagojr.com/journalrank.php) から年次ダウンロード
- `data/journal_abbr.json`: 誌名略語辞書（約100誌収録）。不足時は `python scripts/add_abbr.py` で追加

## マッチング優先順位

1. ISSN（完全一致）
2. 誌名の正規化 + Levenshtein 類似度（閾値 0.85）

## エラー時

`data/sjr_YYYY.csv` が存在しない場合は `FileNotFoundError` を出力し、ダウンロード手順を案内する。
