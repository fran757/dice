"""Dice game optimization."""

from .actions import dynamic, liquidate, simulation
from .dynamic import Solver
from .model import Game, State
from .simulate import Simulator
from .strategy import Strategy, buy, sell


class Passive(Strategy):
    """Just do nothing, never buy or sell."""


class Basic(Strategy):
    """Basic strategy as control subject."""
    expected = {}  # todo: handle parallel access

    def expect(self, dice):
        """Roll expectation for given number of dice.
        Computed values are cached for better speed.
        """
        if dice not in self.expected:
            value = 0
            for k in range(1, 7):
                value += k * (k**dice - (k - 1)**dice) / 6**dice
            self.expected[dice] = value
        return self.expected[dice]

    def buy(self, step, state):
        """Value a dice by the added expectancy."""
        delta = self.expect(state.dice + 1) - self.expect(state.dice)
        return delta * (self.game.time - step) > self.game.price

    def sell(self, step, state, roll):
        """Sell if it can buy the dice back immediately for profit."""
        del step, state
        return roll > self.game.price


@buy
def optimal_1e(game, step, state):
    """Optimal buying strategy implied from optimization results."""
    return state.score > game.price and step <= 4 and state.dice == 1


class Dynamic(Solver, Strategy):
    """Play using dynamic programming optimization."""

    def __init__(self, game):
        super().__init__(game)
        if not self.solved:
            self.run()
