"""Game strategies."""


class Strategy:
    """Hold decision making logic.
    Register inherited classes to be accessed by name.
    """
    _registry = {}

    def __init_subclass__(cls):
        cls._registry[cls.__name__.lower()] = cls

    @classmethod
    def access(cls, name):
        """Access class instance by name, create it if unregistered."""
        if name not in cls._registry:
            globals()[name] = type(name, (cls,), {})
        return cls._registry[name]

    @classmethod
    def retrieve(cls, *names):
        """Get registered strategies by name in a dict.
        By default return whole registry.
        """
        if not names:
            return cls._registry
        selected = {}
        for name in names:
            if name not in cls._registry:
                continue
                # name = f"{name} (?)"
                # globals()[name] = type(name, (cls,), {})
            selected.update({name: cls._registry[name]})
        return selected

    def __init__(self, game):
        self.game = game

    @staticmethod
    def buy(step, state):
        """Decide whether to buy a new dice."""
        del step, state
        return False

    @staticmethod
    def sell(step, state, roll):
        """Decide whether to give up a dice."""
        del step, state, roll
        return False


def buy(fun):
    """Register function as buying strategy."""
    strategy = Strategy.access(fun.__name__)

    def wrapped(self, step, state):
        return fun(self.game, step, state)
    strategy.buy = wrapped


def sell(fun):
    """Register function as selling strategy."""
    strategy = Strategy.access(fun.__name__)

    def wrapped(self, step, state, roll):
        return fun(self.game, step, state, roll)
    strategy.sell = wrapped
