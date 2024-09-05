"""
Core logic:
1. If quote is true, judge the input into 6 labels, otherwise 4 labels.
2. If split_seg is true, judge the input by aggregating the judgements of the segments. Otherwise judge the input as a whole segment.
3. If get_analysis is true, print the Cantonese and SWC ratio to I/O.
"""
import math
import re
from collections import Counter
from typing import List, Optional, Tuple

from .DocumentFeatures import DocumentFeatures
from .JudgementTypes import JudgementType
from .SegmentFeatures import SegmentFeatures

# Cantonese characters not found in SWC
CANTO_FEATURE_RE = re.compile(
    r'[嘅嗰啲咗佢喺咁噉冇哋畀嚟諗惗乜嘢閪撚𨳍𨳊瞓睇餸𨋢摷嚿嚡嘥嗮啱揾搵揦喐逳噏𢳂岋糴揈捹撳㩒𥄫攰癐冚孻冧𡃁嚫跣𨃩瀡氹嬲掟揼揸孭黐唞㪗埞忟𢛴踎脷]|' +
    r'[㗎𠺢喎噃啩𠿪啫唧嗱]|' +
    r'唔[係得會想好識使洗駛通知到去走掂該錯差多少]|點[樣會做得解知]|[琴尋噚聽第]日|[而依]家|[真就實梗緊堅又話都但淨剩只定一]係|邊[度個位科]|' +
    r'[嚇凍攝整揩逢淥浸激][親嚫]|[橫搞傾得唔好]掂|仲[有係話要得好衰唔]|返[學工去翻番到]|[好得]返|執[好生實返輸]|[癡痴][埋線住起身]|[同帶做整溝炒煮]埋|[剩淨坐留]低|傾[偈計]|' +
    r'屋企|收皮|慳錢|屈機|隔籬|幫襯|求其|家陣|仆街|是[但旦]|[濕溼]碎|零舍|肉[赤緊酸]|核突|[勁隻][秋抽]|[呃𧦠][鬼人秤稱錢]')


# A list of exceptions where the above characters can be found in SWC
CANTO_EXCLUDE_RE = re.compile(r'(關係|吱唔|咿唔|喇嘛|喇叭|俾路支|俾斯麥)')

# SWC characters that are less common in Cantonese
SWC_FEATURE_RE = re.compile(r'[這哪唄咱啥甭那是的他她它吧沒麼么些了卻説說吃弄把也在]|[事門塊勁花那點會]兒|而已')

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
ALL_QUOTEMARKS_RE = re.compile(
    r'「([^「]*)」|“([^“]*)”|《([^《]*)》|【([^【]*)】|『([^『]*)』')

# A list of sentential delimiters
ALL_DELIMITERS_RE = re.compile(r'[，。；？！⋯\n]')

ALL_HAN_RE = re.compile(
    r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002ebef'
    r'\U00030000-\U000323af\ufa0e\ufa0f\ufa11\ufa13\ufa14\ufa1f\ufa21\ufa23\ufa24\ufa27\ufa28\ufa29\u3006\u3007]'
    r'[\ufe00-\ufe0f\U000e0100-\U000e01ef]?')


class CantoneseDetector:
    """
    To judge a document, you can either judge the entire document with as one single segment based on its Cantonese and SWC presence,
    or split the document into segments and aggregate the judgement from the segments.

    Attributes:
        split_seg (bool): Split the document into segments if True. Defaults to False.
        use_quotes (bool): Separate Matrix and Quote if True. Defaults to False.
        get_analysis (bool): Print judgement to I/O if True. Defaults to False.
    """

    def __init__(self, split_seg: bool = False, use_quotes: bool = False, get_analysis: bool = False, canto_tolerance: float = 0.01, swc_tolerance: float = 0.01, canto_presence: float = 0.03, swc_presence: float = 0.03) -> None:
        """
        Initialize the thresholds
        """
        # If True, split the document into segments, and the final judgement is aggregated from the segments.
        self.split_seg: bool = split_seg
        # If True, separate Matrix and Quote, and the final judgement is aggregated from the two parts.
        self.use_quotes: bool = use_quotes
        self.get_analysis: bool = get_analysis

        # Cantonese features in less than 1% of the text will still be considered SWC.
        self.canto_tolerance: float = canto_tolerance
        # SWC features in less than 1% of the text will still be considered Written Cantonese.
        self.swc_tolerance: float = swc_tolerance
        # The minimum Cantonese features expected to be found in Mixed or Cantonese text.
        self.canto_presence: float = canto_presence
        # The minimum SWC features expected to be found in Mixed or SWC text.
        self.swc_presence: float = swc_presence

    def _hant_length(self, segment: str) -> int:
        """
        Return the number of Han characters in a segment. Punctuations are excluded.

        Args:
            segment (str): The segment of text to be analyzed.

        Returns:
            int: The number of Han characters in the segment.
        """
        return sum(1 for _ in ALL_HAN_RE.finditer(segment))

    def _separate_quotes(self, document: str) -> Tuple[str, str]:
        """
        Extract quotes and matrix from a document.

        Args:
            document (str): The input document from which quotes and matrix will be extracted.

        Returns:
            quotes (Tuple[str, str]): A tuple containing the matrix and quotes extracted from the document.
        """
        matrix = re.sub(ALL_QUOTEMARKS_RE, "…", document)
        quote_segments = re.findall(ALL_QUOTEMARKS_RE, document)
        quotes = "…".join(["".join(s) for s in quote_segments])

        return matrix, quotes

    def _get_segment_features(self, segment: str) -> SegmentFeatures:
        """
        Extract and set Cantonese and SWC features in a segment.

        Args:
            segment (str): The segment of text to be analyzed.

        Returns:
            segment_features (SegmentFeatures): The features of the segment.
        """
        canto_feature = CANTO_FEATURE_RE.findall(segment)
        canto_exclude = CANTO_EXCLUDE_RE.findall(segment)
        swc_feature = SWC_FEATURE_RE.findall(segment)
        swc_exclude = SWC_EXCLUDE_RE.findall(segment)

        canto_feature_count: int = len(canto_feature) - len(canto_exclude)
        swc_feature_count: int = len(swc_feature) - len(swc_exclude)

        # len for faster execution
        segment_length = self._hant_length(segment)

        segment_features = SegmentFeatures(segment, canto_feature, canto_exclude, swc_feature,
                                           swc_exclude, canto_feature_count, swc_feature_count, segment_length)

        return segment_features

    def _judge_single_segment(self, segment: str) -> JudgementType | Tuple[JudgementType, SegmentFeatures]:
        """
        Determine the language of a segment based on the presence of Cantonese and SWC features.

        If the Cantonese feature presence are above the threshold, and the Mandarin feature is below the threshold, then it's Cantonese.
        If the Cantonese feature presence are below the threshold, and the Mandarin feature is above the threshold, then it's SWC.
        If both Cantonese and SWC features are below the threshold, then it's Neutral text.
        If both Cantonese and SWC features are above the threshold, then it's Mixed.

        Args:
            segment (str): The segment of text to be judged.

        Returns:
            tuple: A tuple containing the judgement and the segment features.
        """
        segment_features: SegmentFeatures = self._get_segment_features(segment)

        # If the segment has no Han characters, it's neutral
        if segment_features.segment_length == 0:
            return (JudgementType.NEUTRAL, segment_features) if self.get_analysis else JudgementType.NEUTRAL

        # Number of Cantonese and SWC features in total
        num_all_features: int = segment_features.canto_feature_count + \
            segment_features.swc_feature_count

        # If the Cantonese or SWC features are less than the torlerance threshold, then it's lacking Cantonese or SWC features.
        lack_swc: bool = segment_features.swc_feature_count <= math.floor(
            self.swc_tolerance * segment_features.segment_length)
        lack_canto: bool = segment_features.canto_feature_count <= math.floor(
            self.canto_tolerance * segment_features.segment_length)

        # If there are no features or both are lacking, it's a neutral segment
        if num_all_features == 0 or (lack_canto and lack_swc):
            return (JudgementType.NEUTRAL, segment_features) if self.get_analysis else JudgementType.NEUTRAL

        # If not lacking
        else:
            has_canto: bool = segment_features.canto_feature_count >= math.ceil(
                self.canto_presence * segment_features.segment_length)
            has_swc: bool = segment_features.swc_feature_count >= math.ceil(
                self.swc_presence * segment_features.segment_length)

            canto_pref: bool = segment_features.canto_feature_count / num_all_features - \
                segment_features.swc_feature_count / num_all_features > 0.9
            swc_pref: bool = segment_features.swc_feature_count / num_all_features - \
                segment_features.canto_feature_count / num_all_features > 0.9

            if canto_pref and not has_swc:
                return (JudgementType.CANTONESE, segment_features) if self.get_analysis else JudgementType.CANTONESE
            elif swc_pref and not has_canto:
                return (JudgementType.SWC, segment_features) if self.get_analysis else JudgementType.SWC
            else:
                return (JudgementType.MIXED, segment_features) if self.get_analysis else JudgementType.MIXED

    def _judge_segments(self, segments: List[str], document_features: Optional[DocumentFeatures] = None) -> JudgementType | Tuple[JudgementType, DocumentFeatures]:
        """
        Given a list of segments:
        1. If >95% of the segments are Neutral, the overall judgement is Neutral
        2. If Neutral + Cantonese takes up >95%, then overall it is Cantonese
        3. If Neutral + SWC takes up > 95%, then overall it is SWC
        4. Otherwise, it is Mixed.
        If self.get_analysis is True, return the document features as well.

        Args:
            segments (list): A list of segments to be judged.
            document_features (DocumentFeatures): The features of the document.

        Returns:
            judgement (JudgementType): The aggregated judgement of the segments.
            document_features (DocumentFeatures): Aggregation of all segment features.
        """
        if self.get_analysis:
            assert document_features is not None
            segment_judgements: List[JudgementType] = []
            # Aggregate the judgements and features of the segments into document_features
            for segment in segments:
                segment_judgement, segment_features = self._judge_single_segment(
                    segment)
                document_features.document_segments_judgements.append(
                    segment_judgement)
                document_features.document_segments_features.append(
                    segment_features)
                segment_judgements.append(segment_judgement)
        else:
            segment_judgements: List[JudgementType] = [self._judge_single_segment(
                segment) for segment in segments]

        judgements_counter: Counter = Counter(segment_judgements)

        canto_seg_count: int = judgements_counter[JudgementType.CANTONESE]
        swc_seg_count: int = judgements_counter[JudgementType.SWC]
        neutral_seg_count: int = judgements_counter[JudgementType.NEUTRAL]

        # 95% threshold
        threshold = math.ceil(sum(judgements_counter.values()) * 0.95)

        canto_only: bool = canto_seg_count + neutral_seg_count >= threshold
        swc_only: bool = swc_seg_count + neutral_seg_count >= threshold
        neutral_only: bool = neutral_seg_count >= threshold

        if neutral_only:
            return (JudgementType.NEUTRAL, document_features) if self.get_analysis else JudgementType.NEUTRAL
        elif canto_only:
            return (JudgementType.CANTONESE, document_features) if self.get_analysis else JudgementType.CANTONESE
        elif swc_only:
            return (JudgementType.SWC, document_features) if self.get_analysis else JudgementType.SWC
        else:
            return (JudgementType.MIXED, document_features) if self.get_analysis else JudgementType.MIXED

    def _judge_document(self, document: str) -> JudgementType | Tuple[JudgementType, DocumentFeatures]:
        """
        For an input document, judge based on whether `split_seg` and `get_analysis` are True or False.

        If `split_seg` is True, document is split into segments and the final judgement is an aggregation of
        segment judgements, otherwise the document is judged as one single segment.

        If `get_analysis` is True, function will return the document features along with the judgement.
        Otherwise, it will return the judgement only.
        """
        # Split the document into segments if split_seg is True
        if self.split_seg:
            segments: List[str] = filter(lambda x: x.strip(),
                                         ALL_DELIMITERS_RE.split(document))
        # Otherwise, treat the document as a single segment
        else:
            segments: List[str] = [document]

        if self.get_analysis:
            # Store document features in an object if get_analysis is True
            document_features = DocumentFeatures(
                split_seg=self.split_seg, use_quotes=self.use_quotes)

            judgement, document_features = self._judge_segments(
                segments=segments, document_features=document_features)

            return judgement, document_features
        else:
            judgement = self._judge_segments(segments)
            return judgement

    def _judge_matrix_quotes(self, document: str) -> JudgementType | Tuple[JudgementType, DocumentFeatures]:
        """
        Judge the language of a document with quotes.

        Args:
            document (str): The document to be judged.
        Returns:
            tuple: A tuple containing the language of the document, the Cantonese ratio, and the SWC ratio.
        """
        matrix, quotes = self._separate_quotes(document)

        if matrix == "…":
            # Matrix is empty, entire input is a quote
            return self._judge_document(
                ALL_QUOTEMARKS_RE.sub("", quotes))
        elif quotes == "":
            # No quotes
            return self._judge_document(matrix)
        else:
            if self.get_analysis:
                matrix_judgement, matrix_document_features = self._judge_document(
                    matrix)
                quotes_judgement, quotes_document_features = self._judge_document(
                    quotes)

                if matrix_judgement == quotes_judgement:
                    return matrix_judgement, matrix_document_features
                elif matrix_judgement == JudgementType.NEUTRAL:
                    return quotes_judgement, quotes_document_features
                elif quotes_judgement == JudgementType.NEUTRAL:
                    return matrix_judgement, matrix_document_features
                else:
                    # Initalize a new document features object for returning
                    document_features = DocumentFeatures(
                        self.split_seg, self.use_quotes)
                    document_features._merge_judgements_features(
                        matrix_document_features.document_segments_judgements,
                        quotes_document_features.document_segments_judgements,
                        matrix_document_features.document_segments_features,
                        quotes_document_features.document_segments_features
                    )

                    if matrix_judgement == JudgementType.SWC and quotes_judgement == JudgementType.CANTONESE:
                        return JudgementType.CANTONESE_QUOTES_IN_SWC, document_features
                    elif matrix_judgement == JudgementType.SWC and quotes_judgement == JudgementType.MIXED:
                        return JudgementType.MIXED_QUOTES_IN_SWC, document_features
                    else:
                        return JudgementType.MIXED, document_features
            else:
                matrix_judgement = self._judge_document(matrix)
                quotes_judgement = self._judge_document(quotes)

                if matrix_judgement == quotes_judgement:
                    return matrix_judgement
                elif matrix_judgement == JudgementType.NEUTRAL:
                    return quotes_judgement
                elif quotes_judgement == JudgementType.NEUTRAL:
                    return matrix_judgement
                elif matrix_judgement == JudgementType.SWC and quotes_judgement == JudgementType.CANTONESE:
                    return JudgementType.CANTONESE_QUOTES_IN_SWC
                elif matrix_judgement == JudgementType.SWC and quotes_judgement == JudgementType.MIXED:
                    return JudgementType.MIXED_QUOTES_IN_SWC
                else:
                    return JudgementType.MIXED

    def judge(self, document: str) -> JudgementType | Tuple[JudgementType, DocumentFeatures]:
        """
        The only exposed api. Judge the language of a document.

        Args:
            document (str): The document to be judged.

        Returns:
            JudgementType: The final judgement.
            (if self.get_analysis) DocumentFeatures: The features of the document if get_analysis is True.
        """
        if self.use_quotes:
            return self._judge_matrix_quotes(document)
        else:
            if self.get_analysis:
                judgement, document_features = self._judge_document(document)
                return judgement, document_features
            else:
                judgement = self._judge_document(document)
                return judgement
