---
description: "CP2: IMRaD アウトラインを生成する"
---

プロジェクト名: **$ARGUMENTS**

CP2（アウトライン生成）を実行する。

## 前提確認

`progress.yaml` を読み、`cp1_done: true` でなければ
「先に `/search $ARGUMENTS` を実行してください」と伝えて停止する。

## 手順

**1. 入力を読み込む**

- `projects/$ARGUMENTS/checkpoints/cp0_input.yaml` — 研究要素
- `projects/$ARGUMENTS/checkpoints/cp1_references.md` — 承認済み引用候補

**2. outliner エージェントを呼び出してアウトラインを生成する**

エージェント: `outliner`

エージェントへの入力:
- 研究要素（theme / background / methods / data / results / interpretation）
- 引用候補リスト（ID・タイトル・著者・年）

**3. 生成したアウトラインを `projects/$ARGUMENTS/checkpoints/cp2_outline.md` に保存する**

出力フォーマット:
```markdown
# <論文タイトル>

## 1. Introduction
**要約**: <200字以内>
**引用候補**: R1, R3, R5

## 2. Methods
**要約**: <200字以内>
**引用候補**: R2, R4

## 3. Results
**要約**: <200字以内>
**引用候補**: R6, R7

## 4. Discussion
**要約**: <200字以内>
**引用候補**: R1, R8, R9

## 5. Conclusion
**要約**: <100字以内>

## Abstract
**要約**: <全体概要 100字>
**目標字数**: <config の abstract_chars>字
```

**4. ユーザー確認を求める**

アウトラインを表示し、以下を案内する:
- `cp2_outline.md` を直接編集して構成を変更可能
- 承認後は `/draft $ARGUMENTS` を実行

**5. progress.yaml を更新する**

```yaml
current_cp: 2
cp2_done: true
```
