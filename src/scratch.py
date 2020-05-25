from functools import partial
import numpy as np
import yaml

from .model import Game
from .dynamic import Solver


def main():
    """Solve sample game, report buying conditions and expected score.
    DEPRECATED.
    """
    with open("src/game.yaml") as file:
        game = Game(**yaml.safe_load(file))
    solver = Solver(game)
    solver.run()
    if game.rule:
        print(np.where(solver.selling == 1))
    else:
        buying = np.where(solver.buying[:, :, 1:] == 1)
        for step in set(buying[0]):
            print(step, [state[1:] for state in zip(*buying) if state[0] == step])
    # print(np.round(solver.scores[0, 0, 1], 2))
    print(*map(partial(round, ndigits=4), solver.scores[0, 0, :]))


def horizons():
    """For which horizon is it never interesting to buy in a (5, 10) game ?
    DEPRECATED.
    """
    for horizon in range(1, 8):
        game = Game(5, horizon)
        solver = Solver(game)
        solver.run()
        print(horizon, len(np.where(solver.buying > 0)))


if __name__ == "__main__":
    main()
