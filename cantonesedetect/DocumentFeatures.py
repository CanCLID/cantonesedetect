from typing import List

from cantonesedetect.JudgementTypes import JudgementType
from cantonesedetect.SegmentFeatures import SegmentFeatures


class DocumentFeatures:
    """
    Store the `SegmentFeatures`s and segment judgements of the document.
    """

    def __init__(self, split_seg, use_quotes) -> None:
        self.split_seg = split_seg
        self.use_quotes = use_quotes

        self.document_segments_features: List[SegmentFeatures] = []
        self.document_segments_judgements: List[JudgementType] = []

    def _merge_judgements_features(self, matrix_judgements: List[JudgementType], quotes_judgements: List[JudgementType], matrix_features: List[SegmentFeatures], quotes_features: List[SegmentFeatures]) -> None:
        """
        For documents that split the matrix and quotes, the document judgements and features 
        are merged from those of the matrix and quotes.
        """
        assert self.use_quotes is True

        self.document_segments_features = matrix_features + quotes_features
        self.document_segments_judgements = matrix_judgements + quotes_judgements

    def get_analysis(self) -> str:
        """
        Return a string representation of the document features
        """
        assert len(self.document_segments_features) == len(
            self.document_segments_judgements)

        analysis_string = (
            f"------------------------------------\nSplitting quotes: {self.use_quotes}\n"
            f"Splitting segments: {self.split_seg}\n\n----------Segment Features----------\n"
        )

        for segment_features, segment_judgement in zip(self.document_segments_features, self.document_segments_judgements):
            cantonese_features = ", ".join(segment_features.canto_feature)
            swc_features = ", ".join(segment_features.swc_feature)

            analysis_string += f"""Segment: {segment_features.segment}\nJudgement: {segment_judgement}\nCantonese features: {
                cantonese_features}\nCantonese content: {segment_features.canto_content * 100:.2f}%\nSWC features: {swc_features}\nSWC content: {segment_features.swc_content * 100:.2f}%\n\n"""

        return analysis_string
