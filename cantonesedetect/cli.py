import argparse
import sys
from cantonesedetect import CantoneseDetector

sys.stdout.reconfigure(encoding='utf-8')


def main():
    """
    When used as a command line tool, specify input text file with `--input <INPUT.txt>`, 
    and output mode with `--mode <MODE>`.
    """
    argparser = argparse.ArgumentParser(
        description='Specify input text file with `--input <INPUT.txt>`, where each line is a sentence. ')

    argparser.add_argument('--input', type=str, default='input.txt',
                           help='Specify input text file, where each line is a sentence. Default is `input.txt`.')
    argparser.add_argument(
        '--quotes', help='Separate quotes from matrix and judge them separately.', action='store_true')
    argparser.add_argument(
        '--split', help='Split the document into segments', action='store_true', default=False)
    argparser.add_argument(
        '--print_analysis', help='Split the document into segments', action='store_true', default=False)
    args = argparser.parse_args()

    detector = CantoneseDetector(
        split_seg=args.split, use_quotes=args.quotes, get_analysis=args.print_analysis)

    with open(args.input, encoding='utf-8') as f:
        if args.print_analysis:
            for line in f:
                judgement, document_features = detector.judge(line.strip())
                analysis = document_features.get_analysis()
                sys.stdout.write(f"====================================\nINPUT:{line.strip()}\nJUDGEMENT: {
                                 judgement.value}\n")
                sys.stdout.write(analysis)
        else:
            for line in f:
                judgement = detector.judge(line.strip())
                sys.stdout.write(judgement.value + '\n')


if __name__ == '__main__':
    main()
else:
    # This allows the script to be run as a module
    __all__ = ['main']
