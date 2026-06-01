# NotebookLM Factcheck ワークフロー

## 概要

`/factcheck-packet` で生成されたパケットを使い、NotebookLM で引用の裏付けを確認する手順です。

---

## 手順

### 1. PDF の準備

`cp5_factcheck_packet/missing_pdfs.md` を確認し、自動取得できなかった PDF を入手します。

- 所属機関の図書館・データベース経由でダウンロード
- `cp5_factcheck_packet/pdfs/` に配置（ファイル名: `R番号_<任意>.pdf`）

### 2. NotebookLM にノートブックを作成

1. https://notebooklm.google.com にアクセス
2. 「新しいノートブック」をクリック
3. `cp5_factcheck_packet/pdfs/` 内の PDF を全件アップロード

**PDF が 50 件を超える場合:**

NotebookLM Free 版はソース上限が 50 件です。テーマ別にノートブックを分割します:
- ノートブック A: R1〜R25
- ノートブック B: R26〜R50
- 以下同様

### 3. 検証クエリを投げる

`cp5_factcheck_packet/notebooklm_prompts.md` を開き、
各検証項目のプロンプトを NotebookLM に順番に貼り付けます。

例:
```
アップロードされた論文 R1（Smith et al. 2024）に基づいて以下の主張を判定してください。

主張: 「条件Aにおいて○○の効率が△△%向上する」

以下の形式で回答してください:
- Verdict: SUPPORTED / PARTIAL / NOT_SUPPORTED
- Evidence: 該当箇所を論文から直接引用（なければ「該当箇所なし」）
- Comment: 補足（1〜2文）
```

### 4. 結果を記録する

NotebookLM の回答を `cp5_factcheck_packet/results.md` の該当行に転記します:

```markdown
| No. | 引用ID | Verdict | Evidence | Comment |
|-----|--------|---------|----------|---------|
| 1 | R1 | SUPPORTED | 「p.3: ... 」 | 数値が一致 |
| 2 | R3 | NOT_SUPPORTED | 該当箇所なし | 別の条件での記述のみ |
```

### 5. Claude Code に戻る

```
/integrate-factcheck my-paper
```

---

## Verdict の解釈

| Verdict | 意味 | /integrate-factcheck での処理 |
|---|---|---|
| SUPPORTED | 主張は論文に明確に支持されている | 変更なし |
| PARTIAL | 部分的に支持されている | 表現を緩和する修正案を提示 |
| NOT_SUPPORTED | 論文に該当箇所がない | 引用削除・表現変更・代替文献提案 |
