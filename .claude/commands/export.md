---
description: "CP7: 承認済みドラフトを Word (.docx) 形式で出力する"
---

プロジェクト名: **$ARGUMENTS**

CP7（Word 出力）を実行する。

## 前提確認

`projects/$ARGUMENTS/checkpoints/cp6_draft_v2.md` が存在しない場合は
「先に `/integrate-factcheck $ARGUMENTS` を実行してください」と伝えて停止する。

## 手順

**1. 引用 ID を実際の番号に置換して最終 Markdown を生成する**

`cp1_references.md` の ID 列と `cp1_references.bib` を使い、
`cp6_draft_v2.md` 内の `[REF: Rx]` をすべて `[番号]` に置換する。
`config.citation_style` に従い参考文献リストを末尾に追加する。

```bash
python -c "
import sys, json, re
from pathlib import Path
sys.path.insert(0, 'scripts')
from citation_format import parse_bibtex, replace_ref_ids, build_reference_list

proj = 'projects/$ARGUMENTS/checkpoints'
draft = Path(f'{proj}/cp6_draft_v2.md').read_text(encoding='utf-8')
bib = Path(f'{proj}/cp1_references.bib').read_text(encoding='utf-8')

# Build id -> citekey map from cp1_references.md
refs_md = Path(f'{proj}/cp1_references.md').read_text(encoding='utf-8')
id_map = {}
for line in refs_md.splitlines():
    m = re.match(r'\|\s*(R\d+)\s*\|.*\|\s*(10\.\S+)\s*\|', line)
    if m:
        rid, doi = m.group(1), m.group(2)
        # Find citekey from bib
        bib_entries = parse_bibtex(bib)
        for key, entry in bib_entries.items():
            if entry.get('doi','').lower() == doi.lower():
                id_map[rid] = key
                break

import yaml
cfg = yaml.safe_load(Path('projects/$ARGUMENTS/config.yaml').read_text())
style = cfg.get('export',{}).get('citation_style','ieee').lower()
bib_entries = parse_bibtex(bib)
ref_list, id_to_num = build_reference_list(bib_entries, id_map, style)
final = replace_ref_ids(draft, id_to_num)
final += '\n\n## 参考文献\n\n' + ref_list
Path(f'{proj}/cp7_final.md').write_text(final, encoding='utf-8')
print('OK')
"
```

**2. python-docx で .docx に変換する**

```bash
python scripts/docx_export.py \
  projects/$ARGUMENTS/checkpoints/cp7_final.md \
  projects/$ARGUMENTS/checkpoints/cp7_output.docx \
  projects/$ARGUMENTS/config.yaml
```

テンプレートが指定されている場合（`config.export.template` が空でない）:
```bash
python scripts/docx_export.py \
  projects/$ARGUMENTS/checkpoints/cp7_final.md \
  projects/$ARGUMENTS/checkpoints/cp7_output.docx \
  projects/$ARGUMENTS/config.yaml \
  <config.export.template の値>
```

**3. progress.yaml を更新する**

```yaml
current_cp: 7
cp7_done: true
last_updated: "<現在時刻>"
```

## 完了報告

- 出力ファイルパス: `projects/$ARGUMENTS/checkpoints/cp7_output.docx`
- ファイルサイズ
- 参考文献数
- 本文の総文字数（目標との差）
