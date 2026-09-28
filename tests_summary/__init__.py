# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch
from collections import defaultdict
import logging
import re
import os

from odoo.tools import config
from odoo.service.server import preload_registries
from odoo.modules.registry import Registry


class Colorize:
    colors = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")

    def __init__(self, logger):
        self.active = os.name == "posix" and all(
            isinstance(handler, logging.StreamHandler)
            and hasattr(handler.stream, "fileno")
            and os.isatty(handler.stream.fileno())
            for handler in logger.handlers
        )

    def bold(self, text):
        if not self.active:
            return text
        return f"\033[1m{text}\033[0m"

    def color(self, text, color, bold=False):
        if not self.active:
            return text
        return (
            f"\033[{30 + self.colors.index(color)}{';1' if bold else ''}m{text}\033[0m"
        )

    def __getattr__(self, attr):
        if attr in self.colors:
            return lambda text, bold=False: self.color(text, attr, bold)
        return super().__getattr__(attr)


def maybe_pluralize(n, singular, plural=None):
    return f"{n} {singular if n == 1 else (plural or singular + 's')}"


module_re = re.compile(r"odoo\.addons\.(\w+)")


def get_module(test):
    if hasattr(test, "test_module"):
        return test.test_module
    for key in ("description", "test_description", "test_id"):
        if hasattr(test, key):
            match = module_re.search(getattr(test, key))
            if match:
                return match.group(1)
    return "unknown (%s)" % repr(test)


def get_test_name(test):
    if hasattr(test, "_testMethodName"):
        name = ""
        if hasattr(test, "test_class"):
            name += test.test_class + "."
        name += test._testMethodName
        return name
    for key in ("description", "test_description", "test_id"):
        if getattr(test, key, False):
            return getattr(test, key)
    return "unknown (%s)" % repr(test)


def preload_registries_and_display_test_results(dbnames):
    _logger = logging.getLogger(__name__)
    rc = preload_registries(dbnames)
    c = Colorize(_logger)
    types = {
        "errors": "error",
        "failures": "failure",
        "skipped": "skip",
        "expectedFailures": "expected failure",
        "unexpectedSuccesses": "unexpected success",
    }
    colors = {
        "errors": "red",
        "failures": "red",
        "skipped": "yellow",
        "expectedFailures": "green",
        "unexpectedSuccesses": "cyan",
    }
    for db in dbnames:
        report = Registry.registries[db]._assertion_report

        modules_infos = defaultdict(list)
        for type_ in types:
            for test_info in getattr(report, type_):
                test, info = (
                    test_info
                    if isinstance(test_info, tuple) and len(test_info) == 2
                    else (test_info, "Success")
                )
                modules_infos[get_module(test)].append(
                    {"type": type_, "info": info, "test": test}
                )

        message = "\n\n" + c.bold(f"Database {db}: ") + f"{report.testsRun} tests run"
        for type_, type_name in types.items():
            if getattr(report, type_):
                message += ", " + c.color(
                    maybe_pluralize(len(getattr(report, type_)), type_name),
                    colors[type_],
                    True,
                )

        if len(modules_infos):
            message += f" in {maybe_pluralize(len(modules_infos), 'module')}."

        message += "\n\n"

        for module, infos in modules_infos.items():
            message += c.black("+" + "-" * (len(module) + 2) + "+", True) + "\n"
            message += c.black("| ", True) + c.bold(module) + c.black(" |", True) + "\n"
            message += c.black("+" + "-" * (len(module) + 2) + "+", True) + "\n"
            for type_, type_name in types.items():
                type_infos = [info for info in infos if info["type"] == type_]
                if type_infos:
                    message += (
                        c.color(
                            maybe_pluralize(len(type_infos), type_name) + ":",
                            colors[type_],
                            True,
                        )
                        + "\n"
                    )
                    for info in type_infos:
                        message += (
                            c.black(
                                " - "
                                + (
                                    (info["test"].__module__.split(".")[-1] + ":")
                                    if getattr(info["test"], "__module__", False)
                                    else ""
                                ),
                                True,
                            )
                            + c.bold(get_test_name(info["test"]) + ":")
                            + "\n"
                        )
                        message += info["info"].rstrip("\n") + "\n\n"

        getattr(_logger, "error" if report.errors or report.failures else "info")(
            message
        )

    return rc


if config["test_enable"]:
    patch(
        "odoo.service.server.preload_registries",
        preload_registries_and_display_test_results,
    ).start()
