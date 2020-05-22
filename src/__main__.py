#!/usr/bin/env python

"""Run package with `python -m $pkg_name`.
Help on system arguments with the `-h` or `--help` flag.
"""

import argparse
from os.path import join, dirname
import yaml

from . import Game, dynamic, simulate


def parse():
    """Parse system arguments."""
    parser = argparse.ArgumentParser(description="dice game simulation")
    parser.add_argument(
        '-g', '--game',
        type=argparse.FileType('r'),
        default=open(join(dirname(__file__), "game.yaml")),
        help='game file (yaml)')
    parser.add_argument(
        '-o', '--output',
        type=argparse.FileType('w'),
        help='output file (text)')
    parser.add_argument(
        '-d', '--dynamic',
        action='store_true',
        help="show dynamic programming result"
    )
    parser.add_argument(
        '-s', '--simulate',
        action='store_false',
        help="don't simulate the game"
    )
    parser.add_argument(
        '-n', '--size',
        type=int, default=10000,
        help='sample size per strategy')
    parser.add_argument(
        'names',
        nargs='*', default=[],
        help='strategies to compare')
    return parser.parse_args()


def main(**kwargs):
    """Get sample size, report expected score and execution time."""
    args = argparse.Namespace(**kwargs) if kwargs else parse()
    game = Game(**yaml.safe_load(args.game))
    if args.dynamic:
        dynamic(game, args.output)
    if args.simulate:
        simulate(game, args.size, args.names, args.output)


if __name__ == "__main__":
    main()
