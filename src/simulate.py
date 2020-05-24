"""Run game simulations to compute strategy expectations."""

from dataclasses import dataclass
from itertools import repeat
from multiprocessing import Pool
from random import randint

import numpy as np
import scipy.stats as st

from .model import Game, State
from .tools import track, chrono


CORES = 3


@dataclass
class Simulator:
    """Simulate game."""
    game: Game

    @track
    @chrono
    def play(self, strategy):
        """Play one game with given strategy, return score."""
        state = State(1, 0)
        game = self.game
        for step in range(self.game.time):
            if state.score > game.price \
                    and strategy.buy(step, state) \
                    and (not game.limit or state.dice < game.limit):
                state.dice += 1
                state.score -= game.price
            if state.dice:
                roll = max([randint(1, 6) for _ in range(state.dice)])
                state.score += roll
                if game.rule and state.dice >= 2 \
                        and strategy.sell(step, state, roll):
                    state.dice -= 1
                    state.score += roll
        if game.liquid and state.dice:
            state.score += game.liquid[state.dice - 1]
        return state.score

    @chrono
    def run(self, size, strategy):
        """Compute 95% confidence interval on strategy score expectation,
        with given sample size.
        """
        with Pool(CORES) as pool:
            scores = pool.map(self.play, repeat(strategy(self.game), size))
        distribution = dict(loc=np.mean(scores), scale=st.sem(scores))
        return st.t.interval(.95, size - 1, **distribution)
