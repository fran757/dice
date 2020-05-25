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
        self.solved = True

    def value(self, *, bonus=False):
        """Get expected value with optimal strategy (compute it if needed)."""
        if not self.solved:
            self.run()
        if bonus:
            return self.scores[0, 0, 1:]
        return self.scores[0, 0, 1]
