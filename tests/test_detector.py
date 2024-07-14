import unittest
import pytest
from cantonesedetect.Detector import CantoneseDetector
from cantonesedetect.JudgementTypes import JudgementType


class TestCantoneseDetector(unittest.TestCase):
    """
    Test the CantoneseDetector class.
    """

    def setUp(self):
        self.detector = CantoneseDetector(
            split_seg=False, use_quotes=True, get_analysis=False)

    @pytest.mark.private
    def test_hant_length(self):
        """
        Non-Sinograms are not counted.
        """
        self.assertEqual(self.detector._hant_length("早晨。"), 2)
        self.assertEqual(self.detector._hant_length("Hello，早晨"), 2)
        self.assertEqual(self.detector._hant_length("123 foobar。"), 0)

    @pytest.mark.private
    def test_separate_quotes(self):
        """
        `_separate_quotes()` should always return 2 strings.
        """
        document = "一外「一內」二外『二內』三外“三內”。"
        matrix, quotes = self.detector._separate_quotes(document)
        self.assertEqual(matrix, "一外…二外…三外…。")
        self.assertEqual(quotes, "一內…二內…三內")

    @pytest.mark.private
    def test_get_segment_features(self):
        """
        `_get_segment_features()` should return a `SegmentFeatures` object.
        """
        segment = "我哋去邊度食飯啊？我們去哪裏吃飯呢？"
        segment_features = self.detector._get_segment_features(segment)
        self.assertEqual(segment_features.canto_feature_count, 2)  # 哋、邊度
        self.assertEqual(segment_features.swc_feature_count, 2)  # 們、哪裏
        self.assertEqual(segment_features.segment_length, 16)

    @pytest.mark.private
    def test_judge_single_segment(self):
        """
        `_judge_single_segment()` should return a `JudgementType`, which can be a string.
        """
        self.assertEqual(self.detector._judge_single_segment(
            "我哋去邊度食飯？"), "cantonese")
        self.assertEqual(
            self.detector._judge_single_segment("我們去哪裏吃飯？"), "swc")
        self.assertEqual(self.detector._judge_single_segment("你好"), "neutral")
        self.assertEqual(self.detector._judge_single_segment("是咁的"), "mixed")

    @pytest.mark.private
    def test_judge_segments(self):
        """
        `_judge_segments()` should return a `JudgementType`, which can be a string.
        """
        self.assertEqual(self.detector._judge_segments(
            ["我哋去邊度？", "我们去哪里？", "Hello!"]), "mixed")

    @pytest.mark.private
    def test_judge_matrix_quotes(self):
        """
        `_judge_matrix_quotes()` should return a `JudgementType`.
        """
        self.assertEqual(self.detector._judge_matrix_quotes(
            "他說「係噉嘅」"), JudgementType.CANTONESE_QUOTES_IN_SWC)
        self.assertEqual(self.detector._judge_matrix_quotes(
            "他說「是咁的」"), JudgementType.MIXED_QUOTES_IN_SWC)

    def test_judge(self):
        """
        `judge()` should return a `JudgementType`.
        """
        self.assertEqual(self.detector.judge(
            "我哋去邊度？"), JudgementType.CANTONESE)
        self.assertEqual(self.detector.judge("我们去哪里？"), JudgementType.SWC)
        self.assertEqual(self.detector.judge(
            "Hello World!"), JudgementType.NEUTRAL)


if __name__ == '__main__':
    unittest.main()
