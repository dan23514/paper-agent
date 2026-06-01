---
name: docx-export
description: Markdown ドラフトを config.yaml の設定に従って Word (.docx) に変換するスキル
---

## 概要

`scripts/docx_export.py` を呼び出して、Markdown ファイルを python-docx で .docx に変換する。

## 入力

- `draft_md`: Markdown 形式の最終ドラフト（`cp7_final.md`）
- `config`: `config.yaml` の `export` セクション
- `output_path`: 出力先パス（`cp7_output.docx`）
- `template_path`: 学会指定テンプレート .docx（省略可）

## 処理

```python
import sys
sys.path.insert(0, 'scripts')
from docx_export import export_to_docx

export_to_docx(draft_md, config, output_path, template_path)
```

## テンプレート対応

`config.export.template` に `templates/<name>.docx` を指定すると、
そのファイルのスタイル定義（禁則処理・フォント・段落設定）を継承してコンテンツを挿入する。
テンプレートが指定されていない場合は `config` のパラメータからスタイルを直接設定する。

## 依存パッケージ

```bash
pip install python-docx
```
