import argparse
import sys
from .judge import judge

sys.stdout.reconfigure(encoding='utf-8')

def main():
    """
    When used as a command line tool, specify input text file with `--input <INPUT.txt>`, and output mode with `--mode <MODE>`.
    """
    argparser = argparse.ArgumentParser(
        description='Specify input text file with `--input <INPUT.txt>`, where each line is a sentence. ')

    argparser.add_argument('--input', type=str, default='input.txt',
                           help='Specify input text file, where each line is a sentence. Default is `input.txt`.')
    argparser.add_argument('--mode', type=str, default='judgement',
                           help='Specify the mode of output.\n `judgement` for all judgements with a class label, `full` for all the labels prepended to the sentences, Default is `judgement`.')
    argparser.add_argument('--label', type=str, default='all', help='Specify the label of output. Default is `all`.')
    argparser.add_argument('--stat', help='Print extracted features and ratio to I/O if True', action='store_true')
    argparser.add_argument('--quotes', help='Separate quotes from matrix and judge them separately.', action='store_true')
    argparser.add_argument('--split', help='Split the document into segments if True', action='store_true')
    argparser.add_argument('--fullstat', help='Print judgement to I/O if True', action='store_true')
    argparser.add_argument('--fast', help='Fast mode if True', action='store_true')

    args = argparser.parse_args()

    with open(args.input, encoding='utf-8') as f:
        for line in f:
            l = line.strip()
            judgement, canto, swc = judge(l, split_seg=args.split, get_quote=args.quotes, print_stat=args.fullstat, fast_mode=args.fast)
            _line = judgement
            if args.stat:
                _line = _line + (f'\t{canto}\t{swc}')
            if args.mode == 'full':
                _line = _line + (f'\t{l}')
            _line = _line + '\n'
            sys.stdout.write(_line)

if __name__ == '__main__':
    main()