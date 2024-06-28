from cantonesedetect.judge import judge
import unittest


def load_test_sentences(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()
                 and not line.startswith('#')]
    test_cases = []
    for line in lines:
        if '|' in line:
            sentence, quotemode, expected = line.split('|')
            test_cases.append((sentence, quotemode, expected))
    return test_cases


test_cases = load_test_sentences('tests/test_judge_sentences.txt')


class TestJudgeFunction(unittest.TestCase):
    def test_judge(self):
        for sentence, quotemode, expected in test_cases:
            result = judge(sentence, get_quote = (quotemode == 'Quote'))[0]
            self.assertEqual(
                result, expected, f"Failed for input: {sentence}. Expected: {expected}, Quote Mode: {quotemode} but got: {result}")


if __name__ == "__main__":
    unittest.main()