"""Simple representation of game rules and state."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Game:
    """Represent game rules: dice price, total time,
    whether dice selling is allowed, dice limit and dice liquidation bonus.
    """
    price: int
    time: int
    rule: bool = False
    limit: int = 0
    liquid: Tuple[int] = ()

    def __post_init__(self):
        """Make liquidation prices a tuple to be hashable.
        Check that the dice limit complies with liquidation data.
        """
        if self.limit and not any(self.liquid):
            super().__setattr__("liquid", (0,) * self.limit)
        elif len(self.liquid) > 0:
            assert len(self.liquid) == self.limit, len(self.liquid)
            super().__setattr__("liquid", tuple(self.liquid))


@dataclass
class State:
    """Encode game state with dice count and current score."""
    dice: int
    score: int
