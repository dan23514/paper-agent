---
description: "CP5: NotebookLM 用 Factcheck パケットを生成し OA PDF をダウンロードする"
---

プロジェクト名: **$ARGUMENTS**

CP5（Factcheck パケット生成）を実行する。

## 手順

**1. 本文中の全引用主張を抽出して `claims.md` を生成する**

`projects/$ARGUMENTS/checkpoints/cp3_draft_v1.md` を読み込み、
`[REF: Rx]` を含む文を全て抽出する。

`projects/$ARGUMENTS/checkpoints/cp5_factcheck_packet/claims.md`:
```markdown
# 引用主張リスト

| No. | 引用ID | 著者・年 | 主張（引用を含む文） | DOI |
|-----|--------|----------|----------------------|-----|
| 1 | R1 | Smith et al. 2024 | 「条件Aにおいて…」 | 10.1038/... |
| 2 | R3 | Tanaka et al. 2023 | 「本手法は…」 | 10.1109/... |
```

**2. OA PDF を自動ダウンロードする**

```bash
python scripts/pdf_fetcher.py \
  projects/$ARGUMENTS/checkpoints/cp1_references.json \
  projects/$ARGUMENTS/checkpoints/cp5_factcheck_packet/pdfs
```

**3. NotebookLM 用プロンプトテンプレートを生成する**

`notebooklm_prompts.md` の各エントリは以下の形式:
```
## 検証 No.1（R1: Smith et al. 2024）

アップロードされた論文 R1（Smith et al. 2024）に基づいて以下の主張を判定してください。

主張: 「条件Aにおいて○○の効率が△△%向上する」

以下の形式で回答してください:
- Verdict: SUPPORTED / PARTIAL / NOT_SUPPORTED
- Evidence: 該当箇所を論文から直接引用（なければ「該当箇所なし」）
- Comment: 補足（1〜2文）
```

**4. instructions.md を生成する**

NotebookLM 操作マニュアル（ノートブック分割対応含む）を `instructions.md` に書く。
PDF が 50 件を超える場合は分割運用の手順も含める。

**5. results.md（空テンプレート）を生成する**

```markdown
# Factcheck 結果

| No. | 引用ID | Verdict | Evidence | Comment |
|-----|--------|---------|----------|---------|
| 1 | R1 | | | |
| 2 | R3 | | | |
```

**6. ユーザーへの案内**

`missing_pdfs.md` の内容を表示する。
その後、`instructions.md` の手順（`cp5_factcheck_packet/instructions.md`）を案内する。
完了後は `/integrate-factcheck $ARGUMENTS` を実行するよう伝える。

**7. progress.yaml を更新する**

```yaml
current_cp: 5
cp5_done: false  # integrate-factcheck 完了後に true になる
```
