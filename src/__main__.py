"""Run package with `python -m $pkg_name`.
Help on system arguments with the `-h` or `--help` flag.
"""
import argparse
from os.path import join, dirname
import yaml

from . import Game, dynamic, liquidate, simulate


def load(data):
    """Extract data from file descriptor if needed."""
    if isinstance(data, dict):
        return data
    return yaml.safe_load(data)


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
        help="show dynamic programming value")
    parser.add_argument(
        '-k', '--liquidate',
        action='store_true',
        help="show equivalent liquidation values")
    parser.add_argument(
        '-s', '--simulate',
        action='store_true',
        help="run game simulations")
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
    game = Game(**load(args.game))
    if args.dynamic:
        dynamic(game, args.output)
    if args.liquidate:
        liquidate(game, args.output)
    if args.simulate:
        simulate(game, args.size, args.names, args.output)

main()
