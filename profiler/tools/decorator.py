# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import base64
import io
import logging
import os
import random
import tempfile
import time
from functools import wraps

try:
    import yappi
except ImportError:
    yappi = None

_logger = logging.getLogger(__name__)


def profiled(sample_rate=0.05):
    """
    Decorator to profile a function with yappi and store results in database.

    Args:
        sample_rate (float): Percentage of calls to profile (default: 0.05 = 5%)

    Usage:
        @profiled()
        def my_function(self):
            # Your code here
            pass

        @profiled(sample_rate=0.01)  # Profile 1% of calls
        def another_function(self):
            # Your code here
            pass
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Skip profiling based on sample rate
            if random.random() > sample_rate:
                return func(*args, **kwargs)

            if yappi is None:
                _logger.warning("yappi not installed, skipping profiling")
                return func(*args, **kwargs)

            start_time = time.time()
            previous_clock_type = yappi.get_clock_type()
            use_wall_clock = previous_clock_type != "wall"
            if use_wall_clock:
                yappi.set_clock_type("wall")
            yappi.start()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                yappi.stop()
                duration = time.time() - start_time

                # Get function stats
                func_stats = yappi.get_func_stats()

                # Generate statistics text
                s = io.StringIO()
                func_stats.print_all(out=s)
                stats_text = s.getvalue()

                # Save to pstats format (compatible with gprof2dot, snakeviz, etc.)
                stats_binary = None
                stats_callgrind = None
                try:
                    # Create a temporary file to save stats
                    fd, temp_path = tempfile.mkstemp(suffix=".pstats")
                    try:
                        func_stats.save(temp_path, type="pstat")
                        # Read the binary data
                        with open(temp_path, "rb") as f:
                            stats_binary = f.read()
                    finally:
                        os.close(fd)
                        os.unlink(temp_path)
                except Exception as e:
                    _logger.warning("Failed to serialize pstats: %s", e)

                try:
                    fd, temp_path = tempfile.mkstemp(suffix=".callgrind")
                    try:
                        func_stats.save(temp_path, type="callgrind")
                        with open(temp_path, "rb") as f:
                            stats_callgrind = f.read()
                    finally:
                        os.close(fd)
                        os.unlink(temp_path)
                except Exception as e:
                    _logger.warning("Failed to serialize callgrind: %s", e)

                # Clear yappi stats for next profiling session
                yappi.clear_stats()

                if use_wall_clock:
                    try:
                        yappi.set_clock_type(previous_clock_type)
                    except Exception as e:
                        _logger.warning("Failed to restore yappi clock type: %s", e)

                # Store in database
                try:
                    _store_profile_in_db(
                        func.__name__,
                        stats_text,
                        duration,
                        args,
                        stats_binary,
                        stats_callgrind,
                    )
                except Exception as e:
                    _logger.error(
                        "Failed to store profile for %s: %s", func.__name__, e
                    )

        return wrapper

    return decorator


def _store_profile_in_db(
    func_name, stats_text, duration, args, stats_binary=None, stats_callgrind=None
):
    """Store profile data in database."""
    # Try to get the environment from function arguments
    env = None
    if args and hasattr(args[0], "env"):
        env = args[0].env
    elif args and hasattr(args[0], "_name"):
        # For model methods
        env = args[0].env

    if not env:
        _logger.warning("Cannot store profile for %s: no environment found", func_name)
        return

    # Create a new cursor to avoid transaction rollback issues
    with env.registry.cursor() as new_cr:
        new_env = env(cr=new_cr)
        try:
            values = {
                "name": func_name,
                "stats_text": stats_text,
                "duration": duration,
            }
            if stats_binary:
                # Encode to base64 for Binary field storage
                values["stats_binary"] = base64.b64encode(stats_binary)
            if stats_callgrind:
                values["stats_callgrind"] = base64.b64encode(stats_callgrind)
            new_env["profiler.result"].create(values)
        except Exception as e:
            _logger.error("Error storing profile: %s", e)
            new_cr.rollback()
