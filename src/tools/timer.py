"""Record execution times of functions."""

import atexit
from functools import wraps
from multiprocessing import Value
from time import time

from .report import report


class Clock:
    """Record and report total execution time of function.
    Instance registration by function qualname.
    If no report is called, times will be reported upon kernel exit.
    """
    _known = {}

    @classmethod
    def provide(cls, name):
        """Provide clock for named function.
        If not already registered, create one.
        """
        if not cls._known:
            atexit.register(cls.report)
        if name not in cls._known:
            cls._known[name] = cls()
        return cls._known[name]

    def __init__(self):
        self.reset()
        self.locked = False

    def __enter__(self):
        """Provide lock to block recursion recording."""
        locked = self.locked
        self.locked = True
        return locked

    def __exit__(self, *args):
        pass

    def reset(self):
        """Reset counters."""
        self.calls = Value('i', 0)
        self.total = Value('d', 0)

    def record(self, value, locked=False):
        """Append value to record."""
        with self.calls.get_lock():
            self.calls.value += 1
        if not locked:
            with self.total.get_lock():
                self.total.value += value
            self.locked = False

    @classmethod
    def retrieve(cls):
        """Retrieve clock records into single dictionary and reset them."""
        records = {}
        for name, instance in cls._known.items():
            if instance.calls.value:
                records.update({name: (instance.calls.value, instance.total.value)})
                instance.reset()
        return records

    @classmethod
    def report(cls, output=None):
        """Report clock records."""
        records = cls.retrieve()
        if not records:
            return
        message = "{key:<20} (x{value[0]:<6}): {value[1]:.3f} s"
        report("Clock", records, message, output)


def chrono(fun):
    """Clock decorator : register `fun` execution time.
    Closure preserves method identity.
    """
    clock = Clock.provide(fun.__qualname__)

    @wraps(fun)
    def timed(*args, **kwargs):
        with clock as lock:
            before = time()
            value = fun(*args, **kwargs)
            now = time()
            clock.record(now - before, lock)
        return value
    return timed
