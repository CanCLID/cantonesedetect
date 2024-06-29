import unittest
import pytest
from cantonesedetect.Detector import CantoneseDetector


class TestCantoneseDetector(unittest.TestCase):
    """
    Test the CantoneseDetector class.
    """

    def setUp(self):
        self.detector = CantoneseDetector()

    @pytest.mark.private
    def test_hant_length(self):
        self.assertEqual(self.detector._hant_length("早晨。"), 2)
        self.assertEqual(self.detector._hant_length("Hello，早晨"), 2)
        self.assertEqual(self.detector._hant_length("123 foobar。"), 0)

    @pytest.mark.private
    def test_separate_quotes(self):
        document = "一外「一內」二外『二內』三外“三內”。"
        matrix, quotes = self.detector._separate_quotes(document)
        self.assertEqual(matrix, "一外…二外…三外…。")
        self.assertEqual(quotes, "一內…二內…三內")

    @pytest.mark.private
    def test_get_segment_features(self):
        segment = "我哋去邊度食飯啊？我們去哪裏吃飯呢？"
        features = self.detector._get_segment_features(segment)
        self.assertEqual(features.canto_feature_count, 2)  # 哋、邊度
        self.assertEqual(features.swc_feature_count, 2)  # 們、哪裏
        self.assertEqual(features.length, 18)

    @pytest.mark.private
    def test_judge_single_segment(self):
        self.assertEqual(self.detector._judge_single_segment(
            "我哋去邊度食飯？"), "Cantonese")
        self.assertEqual(
            self.detector._judge_single_segment("我們去哪裏吃飯？"), "SWC")
        self.assertEqual(self.detector._judge_single_segment("你好"), "Neutral")
        self.assertEqual(self.detector._judge_single_segment("是咁的"), "Mixed")

    @pytest.mark.private
    def test_judge_segments(self):
        self.assertEqual(self.detector._judge_segments(
            "我哋去邊度？我们去哪里？Hello!"), "Mixed")

    @pytest.mark.private
    def test_judge_matrix_quotes(self):
        self.assertEqual(self.detector._judge_matrix_quotes(
            "他說「係噉嘅」"), "CantoneseQuotesInSWC")
        self.assertEqual(self.detector._judge_matrix_quotes(
            "他說「是咁的」"), "MixedQuotesInSWC")

    def test_judge(self):
        self.assertEqual(self.detector.judge("我哋去邊度？"), "Cantonese")
        self.assertEqual(self.detector.judge("我们去哪里？"), "SWC")
        self.assertEqual(self.detector.judge("Hello World!"), "Neutral")


if __name__ == '__main__':
    unittest.main()
