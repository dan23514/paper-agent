---
name: citation
description: BibTeX ファイルと引用 ID マップから指定スタイルの参考文献リストを生成するスキル
---

## 概要

`scripts/citation_format.py` を呼び出して、ドラフト内の `[REF: Rx]` プレースホルダを番号に置換し、
指定スタイルの参考文献リストを末尾に付加する。

## 入力

- `draft_text`: `[REF: R1]` 形式のプレースホルダを含む本文テキスト
- `bib_text`: BibTeX 形式の参考文献データ（`cp1_references.bib`）
- `ref_id_to_citekey`: `{'R1': 'smith2024', 'R2': 'tanaka2023', ...}` の対応マップ
- `style`: 引用スタイル（`ieee` / `apa` / `nature` / `acs` / `aip` / `vancouver`）

## 処理

```python
import sys
sys.path.insert(0, 'scripts')
from citation_format import process

final_text = process(draft_text, bib_text, ref_id_to_citekey, style)
```

## 対応スタイル

| スタイル | 番号形式 | 用途 |
|---|---|---|
| ieee | [1] [2] | 電気・情報工学 |
| apa | (著者, 年) | 心理・社会科学 |
| nature | 上付き番号 | 自然科学全般 |
| acs | 上付き番号 | 化学 |
| aip | 上付き番号 | 物理学 |
| vancouver | [1] [2] | 医学・生命科学 |
