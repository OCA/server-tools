from contextlib import contextmanager
profile = None
"""The thread-shared profile object.
"""

enabled = False
"""Indicates if the whole profiling functionality is globally active or not.
"""


@contextmanager
def profiling():
    """Thread local profile management, according to the shared :data:`enabled`
    """
    if enabled:
        profile.enable()
    yield

    if enabled:
        profile.disable()
