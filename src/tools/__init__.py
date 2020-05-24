"""Generic tools, here adapted for multiprocessing.
* `report` to present data
* `chrono` to time function execution
* `progress` to show progress in a closed loop
"""
from .progress import Bar, track
from .report import report, table
from .timer import Clock, chrono
