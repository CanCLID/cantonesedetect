import re, math

# Cantonese characters not found in SWC
CANTO_UNIQUE_RE = re.compile(
    r'[嘅嗰啲咗佢喺咁噉冇啩哋畀嚟諗惗乜嘢閪撚𨳍𨳊瞓睇㗎餸𨋢摷喎嚿噃嚡嘥嗮啱揾搵喐逳噏𢳂岋糴揈捹撳㩒𥄫攰癐冚孻冧𡃁嚫跣𨃩瀡氹嬲掟孭黐唞㪗埞忟𢛴嗱]|'
    r'唔[係得會好識使洗駛通知到去走掂該錯差]|點[樣會做得解]|[琴尋噚聽第]日|[而依]家|家[下陣]|[真就實梗又話都]係|邊[度個位科]|'
    r'[嚇凍攝整揩逢淥浸激][親嚫]|[橫搞傾諗得唔]掂|仲[有係話要得好衰唔]|返[學工去歸]|執[好生實返輸]|[留坐剩]低|'
    r'屋企|收皮|慳錢|傾[偈計]|幫襯|求其|是[但旦]|[濕溼]碎|零舍|肉[赤緊酸]|核突|同埋|勁[秋抽]'
)

# Cantonese characters that are less common in SWC
CANTO_FEATURE_RE = re.compile(r'[係唔喇]')

# A list of exceptions where the above characters can be found in SWC
CANTO_EXCLUDE_RE = re.compile(r'(關係|吱唔|咿唔|喇嘛|喇叭)')

# SWC characters that are less common in Cantonese
SWC_FEATURE_RE = re.compile(r'[那是的他它吧沒麼么些了卻説說吃弄]|而已')

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
)

# A list of quotes: Content inside and outside a pair of quotes should be treated separately.
ALL_QUOTEMARKS_RE = re.compile(r'「[^「]*」|“[^“]*”|《[^《]*》|【[^【]*】|『[^『]*』')

# A list of sentential delimiters
ALL_DELIMITERS_RE = re.compile(r'[，。；？！⋯\n]')

ALL_HAN_RE = re.compile(
    r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002ebef'
    r'\U00030000-\U000323af\ufa0e\ufa0f\ufa11\ufa13\ufa14\ufa1f\ufa21\ufa23\ufa24\ufa27\ufa28\ufa29\u3006\u3007]'
    r'[\ufe00-\ufe0f\U000e0100-\U000e01ef]?')

def hant_length(segment):
    """
    Return the number of Han characters in a segment.
    """
    return len(re.findall(ALL_HAN_RE, segment))

def extract_features(segment):
    """
    Return a set of Cantonese and SWC features in a segment.
    """
    return {
        'canto_unique': re.findall(CANTO_UNIQUE_RE, segment),
        'canto_feature': re.findall(CANTO_FEATURE_RE, segment),
        'canto_exclude': re.findall(CANTO_EXCLUDE_RE, segment),
        'swc_feature': re.findall(SWC_FEATURE_RE, segment),
        'swc_exclude': re.findall(SWC_EXCLUDE_RE, segment)
    }

def analyze(segment):
    """
    Return the number of Cantonese and SWC features in a segment.
    """
    features = extract_features(segment)
    stats = {
        'canto_unique_count': len(features['canto_unique']),
        'canto_feature_count': len(features['canto_feature']) - len(features['canto_exclude']),
        'swc_feature_count': len(features['swc_feature']) - len(features['swc_exclude']),
        'length': hant_length(segment) # len for faster execution
    }
    return features, stats

def separate_quotes(document):
    """
    Extract quotes and matrix from a document.
    """

    matrix = re.sub(ALL_QUOTEMARKS_RE, " ", document)
    quotes = "⋯".join(re.findall(ALL_QUOTEMARKS_RE, document))

    return matrix, quotes

def print_analysis(segment, features, stats):
    """
    Print the stats of a segment.
    """
    print(f"{segment} ({stats['length']} Han characters)")
    print(f"Cantonese unique ({stats['canto_unique_count']})")
    print(features['canto_unique'])
    print(f"Cantonese features ({stats['canto_feature_count']})")
    print(features['canto_feature'])
    print(f"SWC features ({stats['swc_feature_count']})")
    print(features['swc_feature'])


## Thresholds
SWC_TOLERANCE = 0.01 # SWC_features lower than 1% of the text will still be considered Written Cantonese.
CANTO_TOLERANCE = 0.01 # Cantonese unique words in lower than 1% of the text will still be considered SWC.
CANTO_PRESENCE = 0.03 # Cantonese unique or features are expected to be found even in formal speech
SWC_PRESENCE = 0.03 # SWC features are expected to be found even in informal speech


def judge(segment, detailed = False):
    """
    """
    features, stats = analyze(segment)
    l = stats['length']
    if l == 0:
        return "Nil"
    if detailed:
        print_analysis(segment, features, stats)

    if (stats['canto_unique_count'] + stats['canto_feature_count'] ) >= math.floor(CANTO_PRESENCE * l) and stats['swc_feature_count'] <= math.floor(SWC_TOLERANCE * l):
        return "Written Cantonese"
    elif stats['canto_unique_count'] <=  math.floor(CANTO_TOLERANCE * l) and stats['swc_feature_count'] >= math.floor (SWC_PRESENCE *l):
        return "SWC"
    else:
        return "Mixed"

from collections import Counter

def get_document_stat(document):

    # Document-level stats: Coarse
    print("Document-level: All words")
    print(judge(document, True))

    # Document-level stats: Coarse: Separate quotes and matrix
    matrix, quotes = separate_quotes(document)
    if len(quotes) > 10:
        print("** Docoument-level: Quotes and matrix")
        matrix_coarse_judgement = judge(matrix, False)
        quotes_coarse_judgement = judge(quotes, False)
        if matrix_coarse_judgement == quotes_coarse_judgement == 'Written Cantonese':
            print(matrix_coarse_judgement)
        elif matrix_coarse_judgement == 'SWC' and quotes_coarse_judgement == 'Written Cantonese':
            print("Dialogue-Narrative split: Cantonese quotes")
        elif matrix_coarse_judgement == 'SWC' and quotes_coarse_judgement == 'Mixed':
            print("Dialogue-Narrative split: Mixed quotes")
        else:
            print("Mixed/Translanguaging")
    else:
        "N/A: No quotes"
    # Document-level stats: Fine
#     sents_matrix = re.split(r'ALL_DELIMTERS_RE', matrix, 2)
#     sents_quotes = re.split(r'ALL_DELIMTERS_RE', quotes, 2)
#     matrix_judgements = [judge(s) for s in sents_matrix]
#     quotes_judgements = [judge(s) for s in sents_quotes]
#     matrix_stats = Counter(matrix_judgements)    
#     quotes_stats = Counter(quotes_judgements)
#     total_stats = matrix_stats + quotes_stats
#     wc_matrix = sum([len(s) for s in sents_matrix])
#     wc_quotes = sum([len(s) for s in sents_quotes])
#     wc_total = len_matrix + len_quotes
#     sc_matrix = len(sents_matrix)
#     sc_quotes = len(sents_quotes)
#     sc_total = sc_matrix + sc_quotes    
#     print("Fine")
#     print("Matrix stats")
#     print (matrix_stats)
#     print("Quotes stats")
#     print (quotes_stats)

#     if total_stats['Written Cantonese'] >= math.ceil(sc_total * 0.95) and
#         print("Written Cantonese")

#     if matrix_stats['SWC'] >= math.ceil(sc_total * 0.5) and
#         quotes_stats['Written Cantonese'] >= matrix_stats['Written Cantonese'] and
#         print("Dialogue-Narrative split")

#         matrix_stats['SWC'] <= math.floor(SWC_TOLERANCE * l):
#         print("Written Cantonese")


#     if doc_matrix_swc_feature <= 3 and doc_matrix_canto_unique > 1:
#         print("Written Cantonese")
#     elif (
#         doc_quotes_canto_unique > doc_matrix_canto_unique
#         and doc_matrix_swc_feature > doc_matrix_canto_unique
#     ):

#     elif doc_matrix_swc_feature > 3 and doc_matrix_canto_unique > 1:
#         print("Mixed/ Translanguaging")
#     else:
#         print("Cannot be classified")

# # Matrix stats

# # Quote stats

