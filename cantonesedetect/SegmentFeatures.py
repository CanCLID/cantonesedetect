from typing import List


class SegmentFeatures:
    def __init__(self, segment, canto_feature, canto_exclude, swc_feature,
                 swc_exclude, canto_feature_count, swc_feature_count, segment_length) -> None:
        self.segment: str = segment

        self.canto_feature: List[str] = canto_feature
        self.canto_exclude: List[str] = canto_exclude
        self.swc_feature: List[str] = swc_feature
        self.swc_exclude: List[str] = swc_exclude

        self.canto_feature_count: int = canto_feature_count
        self.swc_feature_count: int = swc_feature_count
        # Input with no Han characters will have a length of 0.
        self.segment_length: int = segment_length

        self.canto_content: float = canto_feature_count / \
            segment_length if segment_length > 0 else 0
        self.swc_content: float = swc_feature_count / \
            segment_length if segment_length > 0 else 0
