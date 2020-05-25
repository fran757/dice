from dataclasses import replace

from .dynamic import Solver
from .simulate import Simulator
from .strategy import Strategy
from .tools import Bar, report, table


def dynamic(game, output=None):
    """Show expected value with dynamic programming."""
    print("optimal value: ", round(Solver(game).value(), 4), file=output)


def liquidate(game, output=None):
    """Compute liquidation values equivalent to game and add them in."""
    prices = Solver(game).value(bonus=True)
    data = {
        "dice": [d + 1 for d in range(game.limit)],
        "bonus": [str(round(s, 2)) for s in prices]}
    table("Liquidation", data, output)
    return replace(game, liquid=prices)


def simulation(game, size, names, output=None):
    """Run game simulation with given sample size and strategy names."""
    simulator = Simulator(game)
    strategies = Strategy.retrieve(*names)
    scores = {}
    for name, strategy in strategies.items():
        with Bar(size, name):
            scores[name] = simulator.run(size, strategy)
    message = "{key:<10}: {value[0]:.2f} - {value[1]:.2f}"
    report("Scores", scores, message, output)
