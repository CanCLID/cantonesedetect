from typing import List


class SegmentFeatures:
    def __init__(self, segment, canto_feature, canto_exclude, swc_feature,
                 swc_exclude, canto_feature_count, swc_feature_count, length) -> None:
        self.segment: str = segment

        self.canto_feature: List[str] = canto_feature
        self.canto_exclude: List[str] = canto_exclude
        self.swc_feature: List[str] = swc_feature
        self.swc_exclude: List[str] = swc_exclude

        self.canto_feature_count: int = canto_feature_count
        self.swc_feature_count: int = swc_feature_count
        # Input with no Han characters will have a length of 0.
        self.length: int = length

        self.canto_ratio: float = canto_feature_count / length if length > 0 else 0
        self.swc_ratio: float = swc_feature_count / length if length > 0 else 0

    def print_analysis(self, print_features=False) -> None:
        """
        Print the stats of a segment.

        Args:
            print_features (bool): Whether to print the features of the segment.

        Returns:
            None
        """
        print(f"{self.segment} ({self.length} Han characters)")

        print(f"Cantonese features: {self.canto_feature_count}")
        if print_features:
            print(self.canto_feature)

        print(f"SWC features {self.swc_feature_count}")
        if print_features:
            print(self.swc_feature)
