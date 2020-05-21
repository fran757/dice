"""Progress bar utility."""

from dataclasses import dataclass
from functools import wraps
from multiprocessing import Value


def track(fun):
    """Enable tracking by a progress bar.
    This needs to be done before runtime
    to allow pickling in multiprocessing.
    """
    @wraps(fun)
    def tracked(*args, **kwargs):
        Bar.advance()
        return fun(*args, **kwargs)
    return tracked


@dataclass
class Bar:
    """Knowing estimated computation time (can be any unitless arbitrary value),
    update a loading bar on each call given current remaining time.
    """
    width = 50
    _instance = None

    def __new__(cls, *args):
        cls._instance = super().__new__(cls)
        cls._instance.__init__(*args)
        return cls._instance

    def __init__(self, total, message="Progress"):
        self.total = total
        self.message = message
        self.advanced = Value('i', 0)
        self.buffer = Value('i', 0)

    def __enter__(self):
        pass

    @classmethod
    def advance(cls):
        """Advance loading bar, draw if buffer reaches 1% of total."""
        self = cls._instance
        if self is None:
            return
        with self.buffer.get_lock():
            self.buffer.value += 1
        if self.buffer.value / self.total < 1 / 100:
            return
        with self.advanced.get_lock():
            self.advanced.value += self.buffer.value
        self.buffer.value = 0
        ratio = min(self.advanced.value / self.total, 1)
        display = f"{'█' * round(self.width * ratio):-<{self.width}}"
        print(f"{self.message:<10}: |{display}| {100 * ratio:.0f}% Complete", end="\r")

    def __exit__(self, exception, value, traceback):
        print(" " * (self.width + 30), end='\r')