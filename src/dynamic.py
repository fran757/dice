"""Solve game by dynamic programming."""

from dataclasses import replace
import numpy as np

from .model import State
from .tools import chrono


def proba(dice, score):
    """Compute probability for maximum score among dice."""
    return (score**dice - (score-1)**dice)/6**dice


class Solver:
    """Game solver.
    :scores: expected score from (step, score, dice)
    :buying: buying decision from (step, score, dice)
    :midscores: expected score from (step, score, dice, roll)
    :selling: selling decision from (step, score, dice, roll)
    :solved: marker for whether the solver has been run
    """
    _instances = {}

    def __new__(cls, game=None):
        if not game:
            return super().__new__(cls)
        if game not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[game] = instance
        return cls._instances[game]

    def __init__(self, game):
        self.game = game
        lucky = self.lucky(game.time, game.rule)
        most = (game.limit or game.time + 1) + 1
        self.scores = np.zeros((game.time + 1, lucky, most))
        self.buying = np.zeros_like(self.scores[:-1])
        if game.rule:
            self.selling = np.zeros((game.time, lucky, most, 7))
            self.midscores = np.zeros((game.time, lucky, most, 7))
        self.scores[-1] = np.arange(lucky).repeat(most, 0).reshape(lucky, -1)
        if game.liquid:
            self.scores[-1, :, 1:] += \
                np.repeat(game.liquid, lucky).reshape(game.limit, lucky).T
        self.solved = False

    @staticmethod
    def lucky(time, rule):
        """Maximum possible score with given time and game rule.
        (loose for safety)
        """
        return 6 * (1 + rule) * time + 1

    def sell(self, step, state, roll):
        """Compute whether a dice should be sold, with associated scores."""
        if not self.game.rule:
            return False
        if self.solved:
            return self.selling[step, state.score, state.dice, roll]
        dice, score = state.dice, state.score
        decision = gain = 0
        for choice in range(1 + (dice >= 2)):
            if (potential := self.scores[
                    step + 1,
                    score + (1 + choice) * roll,
                    dice - choice]) >= gain:
                decision, gain = choice, potential
        self.midscores[step, score, dice, roll] = gain
        self.selling[step, score, dice, roll] = decision
        return decision

    def buy(self, step, state):
        """Compute whether to buy dice, with associated scores."""
        if self.solved:
            return self.buying[step, state.score, state.dice]
        dice, score = state.dice, state.score
        game = self.game
        decision, gain = 0, 0
        right = score > game.price and (not game.limit or dice < game.limit)
        for choice in range(1 + right):
            potential = 0
            for roll in range(1, 7):
                if self.game.rule:
                    target = self.midscores[
                        step,
                        score - self.game.price * choice,
                        dice + choice,
                        roll
                    ]
                else:
                    target = self.scores[
                        step + 1,
                        score - self.game.price * choice + roll,
                        dice + choice
                    ]
                potential += proba(dice + choice, roll) * target
                if potential > gain:
                    decision, gain = choice, potential
        self.scores[step, score, dice] = gain
        self.buying[step, score, dice] = decision
        return decision

    @chrono
    def run(self):
        """Compute best decisions and expected scores for reachable situations
        (represented by the iterable `states`).
        """
        # print([x1-x0 for x1, x0 in zip(self.game.liquid[1:], self.game.liquid[:-1])])
        if self.game.time > 10 and self.game.limit:
            midpoint = int(self.game.time / 2)
            endgame = Solver(replace(self.game, time=midpoint))
            endgame.run()
            opening = Solver(replace(self.game, time=midpoint, liquid=endgame.scores[0, 0, 1:]))
            opening.run()
            self.scores = np.concatenate((opening.scores, endgame.scores))
            # self.buying = np.concatenate((opening.buying, endgame.buying))
            # if self.game.rule:
            #     self.selling = np.concatenate((opening.selling, endgame.selling))
            self.solved = True
            return

        for step in range(self.game.time)[::-1]:
            score = self.lucky(step, self.game.rule)
            dice = (self.game.limit or step + 1) + 1
            states = [State(*s)
                      for s in zip(*np.mgrid[:dice, :score].reshape(2, -1))]
            for state in states:
                for roll in range(1, 7):
                    self.sell(step, state, roll)
            for state in states:
                self.buy(step, state)
            # if not step % 10:
            #     print(self.scores[step, 0, 1] - self.scores[step + 10, 0, 1])
            #     scores = self.scores[step, 0, 1:]
            #     print([v-u for u,v in zip(scores[:-1], scores[1:])])
        self.solved = True

    @property
    def value(self):
        """Get optimal value (compute it if needed)."""
        if not self.solved:
            self.run()
        return self.scores[0, 0, 1]


# def main():
#     """Solve sample game, report buying conditions and expected score."""
#     from functools import partial
#     import yaml
#     with open("game.yaml") as file:
#         game = Game(**yaml.safe_load(file)["game"])
#     solver = Solver(game)
#     solver.run()
#     if game.rule:
#         print(np.where(solver.selling == 1))
#     else:
#         buying = np.where(solver.buying[:, :, 1:] == 1)
#         for step in set(buying[0]):
#             print(step, [state[1:] for state in zip(*buying) if state[0] == step])
#     # print(np.round(solver.scores[0, 0, 1], 2))
#     print(*map(partial(round, ndigits=4), solver.scores[0, 0, :]))


# def horizons():
#     """For which horizon is it never interesting to buy in a (5, 10) game ?"""
#     for horizon in range(1, 6):
#         game = Game(5, horizon)
#         solver = Solver(game)
#         solver.run()
#         print(horizon, np.where(solver.buying > 0))


# if __name__ == "__main__":
#     from .model import Game
#     main()
