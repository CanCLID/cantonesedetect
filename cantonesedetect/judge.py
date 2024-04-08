import re, math
from typing import List, Tuple, Dict

# Cantonese characters not found in SWC
CANTO_FEATURE_RE = re.compile(
    r'[嘅嗰啲咗佢喺咁噉冇啩哋畀嚟諗惗乜嘢閪撚𨳍𨳊瞓睇㗎餸𨋢摷喎嚿噃嚡嘥嗮啱揾搵喐逳噏𢳂岋糴揈捹撳㩒𥄫攰癐冚孻冧𡃁嚫跣𨃩瀡氹嬲掟孭黐唞㪗埞忟𢛴嗱係唔喇俾]|'
    r'唔[係得會好識使洗駛通知到去走掂該錯差]|點[樣會做得解]|[琴尋噚聽第]日|[而依]家|家[下陣]|[真就實梗又話都]係|邊[度個位科]|'
    r'[嚇凍攝整揩逢淥浸激][親嚫]|[橫搞傾諗得唔]掂|仲[有係話要得好衰唔]|返[學工去歸]|執[好生實返輸]|[留坐剩]低|'
    r'屋企|收皮|慳錢|傾[偈計]|幫襯|求其|是[但旦]|[濕溼]碎|零舍|肉[赤緊酸]|核突|同埋|勁[秋抽]|邊[度隻條張樣個]|去邊'
)

# A list of exceptions where the above characters can be found in SWC
CANTO_EXCLUDE_RE = re.compile(r'(關係|吱唔|咿唔|喇嘛|喇叭|俾路支|俾斯麥)')

# SWC characters that are less common in Cantonese
SWC_FEATURE_RE = re.compile(r'[這哪唄咱啥甭那是的他她它吧沒麼么些了卻説說吃弄把也在]|而已')

# A list of exceptions where the above characters can be found in Cantonese (mainly phrases or proper nouns)
SWC_EXCLUDE_RE = re.compile(
    r'亞利桑那|剎那|巴塞羅那|薩那|沙那|哈瓦那|印第安那|那不勒斯|支那|'
    r'是[否日次非但旦]|[利於]是|唯命是從|頭頭是道|似是而非|自以為是|俯拾皆是|撩是鬥非|莫衷一是|唯才是用|'
    r'[目綠藍紅中]的|的[士確式]|波羅的海|眾矢之的|的而且確|大眼的度|的起心肝'
    r'些[微少許小]|'
    r'[淹沉浸覆湮埋沒出]沒|沒[落頂收]|神出鬼沒|'
    r'了[結無斷當然哥結得解事之]|[未明]了|不得了|大不了|'
    r'他[信人國日殺鄉]|[其利無排維結]他|馬耳他|他加祿|他山之石|'
    r'其[它]|'
    r'[酒網水貼]吧|吧[台臺枱檯]|'
    r'[退忘阻]卻|卻步|'
    r'[遊游小傳解學假淺眾衆訴論][説說]|[說説][話服明]|自圓其[説說]|長話短[說説]|不由分[說説]|'
    r'吃[虧苦力]|'
    r'弄[堂]'
    r'把[握柄持火風關鬼口嘴戲脈炮砲屁手聲]|大把|拉把|冧把|掃把|拖把|得把|加把|下把位|一把年紀|把死人聲|自把自為|兩把|三把|四把|五把|幾把|拎把|第一把|泵把|'
    r'也[許門]|[非威]也|也文也武|之乎者也|維也納|空空如也|頭也不回|時也[命運]也|'
    r'在[場乎下校學行任野意於望內案旁生世心線逃位即職座囚此家]|[站志旨爭所勝衰實內外念現好健存潛差弊活]在|我思故我在'
)

# A list of quotes: Content inside and outside a pair of quotes should be treated separately.
ALL_QUOTEMARKS_RE = re.compile(r'「[^「]*」|“[^“]*”|《[^《]*》|【[^【]*】|『[^『]*』')

# A list of sentential delimiters
ALL_DELIMITERS_RE = re.compile(r'[，。；？！⋯\n]')

ALL_HAN_RE = re.compile(
    r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002ebef'
    r'\U00030000-\U000323af\ufa0e\ufa0f\ufa11\ufa13\ufa14\ufa1f\ufa21\ufa23\ufa24\ufa27\ufa28\ufa29\u3006\u3007]'
    r'[\ufe00-\ufe0f\U000e0100-\U000e01ef]?')

## Thresholds
CANTO_TOLERANCE = 0.01 # Cantonese features in less than 1% of the text will still be considered SWC.
SWC_TOLERANCE = 0.01 # SWC features in less than 1% of the text will still be considered Written Cantonese.
CANTO_PRESENCE = 0.03 # The minimum Cantonese features expected to be found in Mixed or Cantonese text.
SWC_PRESENCE = 0.03 # The minimum SWC features expected to be found in Mixed or SWC text.


def hant_length(segment: str) -> int:
    """
    Return the number of Han characters in a segment.
    """
    return len(re.findall(ALL_HAN_RE, segment))

def extract_features(segment: str) -> Dict[str, List[str]]:
    """
    Return a set of Cantonese and SWC features in a segment.
    """
    return {
        'canto_feature': re.findall(CANTO_FEATURE_RE, segment),
        'canto_exclude': re.findall(CANTO_EXCLUDE_RE, segment),
        'swc_feature': re.findall(SWC_FEATURE_RE, segment),
        'swc_exclude': re.findall(SWC_EXCLUDE_RE, segment)
    }

def get_feature_stats(segment: str, fast_mode: bool = False) -> Tuple[Dict[str, List[str]], Dict[str, int]]:
    """
    Return the number of Cantonese and SWC features in a segment.

    Parameters:
    segment (str): The input segment to extract features from.
    fast_mode (bool, optional): If True, use a faster method to calculate the length of the segment. 
                                Defaults to False.

    Returns:
    tuple: A tuple containing two dictionaries. The first dictionary contains the extracted features, 
           including Cantonese and SWC features. The second dictionary contains the statistics, 
           including the count of Cantonese features, count of Cantonese features (excluding 
           excluded features), count of SWC features (excluding excluded features), and the length 
           of the segment.

    """
    features = extract_features(segment)
    stats = {
        'canto_feature_count': len(features['canto_feature']) - len(features['canto_exclude']),
        'swc_feature_count': len(features['swc_feature']) - len(features['swc_exclude']),
        'length': hant_length(segment) if fast_mode else len(segment) # len for faster execution
    }
    return features, stats

def separate_quotes(document: str) -> Tuple[str, str]:
    """
    Extract quotes and matrix from a document.

    Args:
        document (str): The input document from which quotes and matrix will be extracted.

    Returns:
        tuple: A tuple containing the matrix and quotes extracted from the document.
    """

    matrix = re.sub(ALL_QUOTEMARKS_RE, " ", document)
    quotes = "⋯".join(re.findall(ALL_QUOTEMARKS_RE, document))

    return matrix, quotes

def print_analysis(segment: str, features: Dict[str, List[str]], stats: Dict[str, int]) -> None:
    """
    Print the stats of a segment.

    Args:
        segment (str): The segment to be analyzed.
        features (dict): A dictionary containing the features of the segment.
        stats (dict): A dictionary containing the statistics of the segment.

    Returns:
        None
    """
    print(f"{segment} ({stats['length']} Han characters)")
    print(f"Cantonese features ({stats['canto_feature_count']})")
    print(features['canto_feature'])
    print(f"SWC features ({stats['swc_feature_count']})")
    print(features['swc_feature'])


def judge_single(segment: str, detailed: bool = False, fast_mode: bool = False) -> Tuple[str, int, int, int]:
    """
    Determine the language of a segment based on the presence of Cantonese and SWC features.

    If the Cantonese feature presence are above the threshold, and the Mandarin feature is below the threshold, then it's Cantonese.
    If the Cantonese feature presence are below the threshold, and the Mandarin feature is above the threshold, then it's SWC.
    If both Cantonese and SWC features are below the threshold, then it's Neutral text.
    If both Cantonese and SWC features are above the threshold, then it's Mixed.

    Parameters:
    - segment: The segment of text to be judged.
    - detailed: If True, print the analysis of the segment.
    - fast_mode: If True, use a faster method to calculate the length of the segment.

    Returns:
    - language: The language of the segment (Cantonese, SWC, Neutral, or Mixed).
    - canto_count: The count of Cantonese features in the segment.
    - swc_count: The count of SWC features in the segment.
    - length: The length of the segment in Han characters.
    """
    features, stats = get_feature_stats(segment, fast_mode)
    length = stats['length']
    if length == 0:
        return "Empty", 0, 0, length
    if detailed:
        print_analysis(segment, features, stats)

    canto_count = stats['canto_feature_count']
    swc_count = stats['swc_feature_count']

    feature_total = canto_count + swc_count
    lack_swc = swc_count <= math.floor(SWC_TOLERANCE * length)
    lack_canto = canto_count <= math.floor(CANTO_TOLERANCE * length)
    if feature_total == 0 or (lack_canto and lack_swc):
        language = "Neutral"
    else:
        has_canto = canto_count >= math.ceil(CANTO_PRESENCE * length)
        has_swc = swc_count >= math.ceil(SWC_PRESENCE * length)
        canto_pref = canto_count / feature_total - swc_count / feature_total > 0.9
        swc_pref = swc_count / feature_total - canto_count / feature_total > 0.9
        if canto_pref and not has_swc:
            language = "Cantonese"
        elif swc_pref and not has_canto:
            language = "SWC"
        else:
            language = "Mixed"
    return language, canto_count, swc_count, length

def judge_segments(segments: List[str], detailed: bool = False, fast_mode: bool = False) -> Tuple[str, int, int, int]:
    """
    Determines the language of each segment in the given list of segments.

    Args:
        segments (list): A list of segments to be judged.
        detailed (bool, optional): If True, returns detailed judgements for each segment. Defaults to False.
        fast_mode (bool, optional): If True, uses a faster mode for judging. Defaults to False.

    Returns:
        tuple: A tuple containing the language of the segments, the count of Cantonese segments,
               the count of SWC segments, and the total number of segments.

    Raises:
        None
    """
    l = len(segments)
    if l == 0:
        return "Empty", 0, 0, l
    else:
        judgements = [judge_single(segment, detailed, fast_mode)[0] for segment in segments]
        canto_seg_count = judgements.count("Cantonese")
        swc_seg_count = judgements.count("SWC")
        neutral_seg_count = judgements.count("Neutral")

        canto_only = canto_seg_count + neutral_seg_count >= math.ceil(len(judgements) * 0.95)
        swc_only = swc_seg_count + neutral_seg_count >= math.ceil(len(judgements) * 0.95)
        neutral_only = neutral_seg_count >= math.ceil(len(judgements) * 0.95)

        if neutral_only:
            language = "Neutral"
        elif canto_only:
            language = "Cantonese"
        elif swc_only:
            language = "SWC"
        else:
            language = "Mixed"
        return language, canto_seg_count, swc_seg_count, l

def judge(document: str, split_seg: bool = False, get_quote: bool = False, print_stat: bool = False, fast_mode: bool = False) -> Tuple[str, str, str]:
    """
    Judge the language of a document.

    Args:
        document (str): The document to be judged.
        split_seg (bool, optional): Split the document into segments if True. Defaults to False.
        get_quote (bool, optional): Separate Matrix and Quote if True. Defaults to False.
        print_stat (bool, optional): Print judgement to I/O if True. Defaults to False.
        fast_mode (bool, optional): Use fast mode if True. Defaults to False.

    Returns:
        tuple[str, str, str]: A tuple containing the category, Cantonese ratio, and SWC ratio.
            - Category: Cantonese, SWC, Mixed, Neutral, CantoneseQuotesInSWC, MixedQuotesInSWC
            - Cantonese ratio: The ratio of Cantonese characters in the document.
            - SWC ratio: The ratio of SWC characters in the document.
    """
    
    def show_ratio(count, total):
        if total == 0:
            return 'N/A'
        return f'{count}/{total} ({count/total*100:.2f}%)'

    if not get_quote:
        if not split_seg:
            judgement, _c, _s, _l = judge_single(document, print_stat, fast_mode)
        else:
            segments = [segment for segment in re.split(ALL_DELIMITERS_RE, document) if segment.strip()]
            judgement, _c, _s, _l = judge_segments(segments, print_stat, fast_mode)
        canto_ratio = show_ratio(_c, _l)
        swc_ratio = show_ratio(_s, _l)
    else: # get_quote
        matrix, quotes = separate_quotes(document)
        lm = len(matrix)
        lq = len(quotes)
        if lm == 0:
            return judge(quotes, split_seg, False, print_stat, fast_mode)
        elif lq == 0:
            return judge(matrix, split_seg, False, print_stat, fast_mode)
        else:
            judgement, _c1, _s1 = judge(matrix, split_seg, False, print_stat, fast_mode)
            quotes_judgement, _c2, _s2 = judge(quotes, split_seg, False, print_stat, fast_mode)
            if judgement == quotes_judgement or quotes_judgement == 'Neutral':
                pass
            elif judgement == 'Neutral':
                judgement = quotes_judgement
            elif judgement == 'SWC' and quotes_judgement == 'Cantonese':
                judgement = "CantoneseQuotesInSWC"
            elif judgement == 'SWC' and quotes_judgement == 'Mixed':
                judgement = "MixedQuotesInSWC"
            else:
                judgement = "Mixed"
            canto_ratio = '[M]' + _c1 + ':' + '[Q]' + _c2
            swc_ratio = '[M]' + _s1 + ':' + '[Q]' + _s2
    return judgement, canto_ratio, swc_ratio
