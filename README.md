# CantoneseDetect 粵語特徵分類器

[![license](https://img.shields.io/github/license/DAVFoundation/captain-n3m0.svg?style=flat-square)](https://github.com/DAVFoundation/captain-n3m0/blob/master/LICENSE)

本項目為 [CantoFilter](https://github.com/CanCLID/cantonese-classifier) 之後續。
This is an extension of the [CantoFilter](https://github.com/CanCLID/cantonese-classifier) project.

## 引用 Citation

抽出字詞特徵嘅策略同埋實踐方式，喺下面整理。討論本分類器時，請引用：

Chaak-ming Lau, Mingfei Lau, and Ann Wai Huen To. 2024. 
[The Extraction and Fine-grained Classification of Written Cantonese Materials through Linguistic Feature Detection.](https://aclanthology.org/2024.eurali-1.4/) 
In Proceedings of the 2nd Workshop on Resources and Technologies for Indigenous, Endangered and Lesser-resourced Languages in Eurasia (EURALI) 
@ LREC-COLING 2024, pages 24–29, Torino, Italia. ELRA and ICCL.

分類器採用嘅分類標籤及基準，參考咗對使用者嘅語言意識形態嘅研究。討論分類準則時，請引用：

The definitions and boundaries of the labels depend on the user's language ideology. 
When discussing the criteria adopted by this tool, please cite:

Lau, Chaak Ming. 2024. Ideologically driven divergence in Cantonese vernacular writing practices. In J.-F. Dupré, editor, _Politics of Language in Hong Kong_, Routledge.

---

## 簡介 Introduction

分類方法係利用粵語同書面中文嘅特徵字詞，用 Regex 方式加以識別。

The filter is based on Regex rules and detects lexical features specific to Cantonese or Written-Chiense.

### 標籤 Labels

分類器會將輸入文本分成四類（粗疏）或六類（精細），分類如下:
The classifiers output four (coarse) or six (fine-grained) categories. The labels are:

1. `Cantonese`: 純粵文，僅含有粵語特徵字詞，例如“你喺邊度” | Pure Cantonese text, contains Cantonese-featured words. E.g. 你喺邊度
1. `SWC`: 書面中文，係一個僅含有書面語特徵字詞，例如“你在哪裏” | Pure Standard Written Chinese (SWC) text, contains Mandarin-feature words. E.g. 你在哪裏
1. `Mixed`：書粵混雜文，同時含有書面語同粵語特徵嘅字詞，例如“是咁的” | Mixed Cantonese-Mandarin text, contains both Cantonese and Mandarin-featured words. E.g. 是咁的
1. `Neutral`：無特徵中文，唔含有官話同粵語特徵，既可以當成粵文亦可以當成官話文，例如“去學校讀書” | No feature Chinese text, contains neither Cantonese nor Mandarin feature words. Such sentences can be used for both Cantonese and Mandarin text corpus. E.g. 去學校讀書
1. `MixedQuotesInSWC` : 書面中文，引文入面係 `Mixed` | `Mixed` contents quoted within SWC text
1. `CantoneseQuotesInSWC` : 書面中文，引文入面係純粵文 `cantonese` | `Cantonese` contents quoted within SWC text

## 用法 Usage

### 系統要求 Requirement

Python >= 3.11

### 安裝 Installation

首先用 pip 安裝

```bash
pip install cantonesedetect
```

### Python

Use `judge()`

```python
from cantonesedetect.judge import judge

print(judge('你喺邊度')[0]) # Cantonese
print(judge('你在哪裏')[0]) # Mandarin
print(judge('是咁的')[0])  # Mixed
print(judge('去學校讀書')[0])  # Neutral
```

### CLI

待補充 to be added.
