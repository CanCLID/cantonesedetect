# CantoneseDetect 粵語特徵分類器

[![license](https://img.shields.io/github/license/DAVFoundation/captain-n3m0.svg?style=for-the-badge&color=)](https://github.com/DAVFoundation/captain-n3m0/blob/master/LICENSE)

本項目為 [canto-filter](https://github.com/CanCLID/canto-filter) 之後續。canto-filter 得 4 個分類標籤且判斷邏輯更加快速簡單，適合在線快速篩選判別文本或者其他要求低延遲、速度快嘅應用場合。本項目採用更精細嘅判斷邏輯，有 6 個分類標籤，準確度更高，但速度亦會相對 canto-filter 更慢。

This is an extension of the [canto-filter](https://github.com/CanCLID/canto-filter) project. canto-filter has only 4 output labels. It has a simipler classification logic and is faster, more suitable for use cases which require low-latency or high classification speed. This package has 6 output and uses a more sophisticated classification logic for more fine-grained classification. It has higher classification accuracy but slower performance.

## 引用 Citation

分類器採用嘅分類標籤及基準，參考咗對使用者嘅語言意識形態嘅研究。討論分類準則時，請引用：

The definitions and boundaries of the labels depend on the user's language ideology.
When discussing the criteria adopted by this tool, please cite:

> Chaak-ming Lau, Mingfei Lau, and Ann Wai Huen To. 2024.
> [The Extraction and Fine-grained Classification of Written Cantonese Materials through Linguistic Feature Detection.](https://aclanthology.org/2024.eurali-1.4/)
> In Proceedings of the 2nd Workshop on Resources and Technologies for Indigenous, Endangered and Lesser-resourced Languages in Eurasia (EURALI)
> @ LREC-COLING 2024, pages 24–29, Torino, Italia. ELRA and ICCL.

---

## 簡介 Introduction

分類方法係利用粵語同書面中文嘅特徵字詞，用 Regex 方式加以識別。分類器主要有兩個主要參數，`--split`同埋`--quotes`，兩個默認都係`False`。

The filter is based on Regex rules and detects lexical features specific to Cantonese or Written-Chiense.

### 分句參數`--split`

呢個參數默認關閉，如果打開，分類器會用句號、問號、感歎號等標點符號將輸入文本切成單句，對每個單句分類判斷，然後再按照下面判別標準整合嚟得到最終分類。所以呢個參數喺輸入都係單句嘅情況下唔會有區別，只會降低運行速度。喺官粵混雜比較多而且比較長嘅文本輸入下會有更多唔同。

目前因為整合分句判斷嘅邏輯比較嚴，所以如果打開，會相比於關閉更加容易將其他類別判斷為`mixed`。所以對於篩選純粵文嘅用途嚟講，打開呢個參數會提高 precision 但降低 recall。

### 分類標籤參數`--quotes`

呢個參數默認關閉，分類器淨係會將輸入分為 4 類。如果打開，就會再增加兩類總共有 6 個標籤。打開後分類器會將引號內嘅文本抽出嚟，將佢哋同引號外文本分開判斷。下面一段就係介紹呢四個同六個標籤。

### 標籤 Labels

分類器會將輸入文本分成四類（粗疏）或六類（精細），分類如下:

The classifiers output four (coarse) or six (fine-grained) categories. The labels are:

1. `Cantonese`: 純粵文，僅含有粵語特徵字詞，例如“你喺邊度” | Pure Cantonese text, contains Cantonese-featured words. E.g. 你喺邊度
1. `SWC`: 書面中文，係一個僅含有書面語特徵字詞，例如“你在哪裏” | Pure Standard Written Chinese (SWC) text, contains Mandarin-feature words. E.g. 你在哪裏
1. `Mixed`：書粵混雜文，同時含有書面語同粵語特徵嘅字詞，例如“是咁的” | Mixed Cantonese-Mandarin text, contains both Cantonese and Mandarin-featured words. E.g. 是咁的
1. `Neutral`：無特徵中文，唔含有官話同粵語特徵，既可以當成粵文亦可以當成官話文，例如“去學校讀書” | No feature Chinese text, contains neither Cantonese nor Mandarin feature words. Such sentences can be used for both Cantonese and Mandarin text corpus. E.g. 去學校讀書
1. `MixedQuotesInSWC` : 書面中文，引文入面係 `Mixed` | `Mixed` contents quoted within SWC text
1. `CantoneseQuotesInSWC` : 書面中文，引文入面係純粵文 `cantonese` | `Cantonese` contents quoted within SWC text

### 系統要求 Requirement

Python >= 3.11

### 安裝 Installation

```bash
pip install cantonesedetect
```

## 用法 Usage

可以通過 Python 函數嚟引用，亦可以直接 CLI 調用。

You can call the Python API or this library, or run it directly in CLI.

### Python

用下面嘅方法創建一個 `Detector`，然後直接調用 `judge()`就可以得到分類結果：

Initialize a `Detector` and call the `judge()` function on inputs, and you will get the classification outputs.

```python
from cantonesedetect import CantoneseDetector

# 默認情況下 use_quotes=False, split_seg=False, get_analysis=False
detector = CantoneseDetector()

detector.judge('你喺邊度') # cantonese
detector.judge('你在哪裏') # swc
detector.judge('是咁的')  # mixed
detector.judge('去學校讀書')  # neutral
detector.judge('他説：“係噉嘅。”')  # cantonese_quotes_in_swc
detector.judge('那就「是咁的」')  # mixed_quotes_in_swc
```

如果想要用引號抽取判別、分句判別同埋獲得分析結果，可以：

If you want to judge inputs based on matrix-quote-splitting, or spliting into segments, you can:

```python
from cantonesedetect import Detector

detector = Detector(use_quotes=True, split_seg=True, get_analysis=True)

judgement, document_features = detector.judge("他説：「我哋今晚食飯。你想去邊度食？」")

# 打印分析結果
# Print analysis results
print(document_features.get_analysis())

# `document_features` 入面有每個分句嘅 `document_segments_features` 同 `document_segments_judgements`
# `document_features` object contains `document_segments_features` which is a list of segment features
print(document_features.document_segments_features[0].canto_feature)
print(document_features.document_segments_features[0].canto_exclude)
print(document_features.document_segments_features[0].swc_feature)
print(document_features.document_segments_features[0].swc_exclude)
# Also contains `document_segments_judgements` which is a list of judgements of the segments
print([j.value for j in document_features.document_segments_judgements])
```

### CLI

如果直接喺 CLI 調用嘅話，只需要指明`--input`就得。 `--quotes`、`--split`、`--print_analysis`三個參數都默認關閉，如果標明就會打開：

If you run directly in CLI, simply specify the `--input`. The optional arguments `--quotes`、`--split`、`--print_analysis` are all `False` by default, and you can turn them on by specifying them.

```bash
cantonesedetect --input input.txt
# 開啓引號抽取判別、分句判別並且打印分析結果
# Enable matrix-quotes-splitting, segment-splitting and printing the analysis.
cantonesedetect --input input.txt --quotes --split --print_analysis
```
