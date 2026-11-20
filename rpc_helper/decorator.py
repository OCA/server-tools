# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


def disable_rpc(*config):
    """Decorate classes to disable RPC calls.

    Possible values:

    * none, block all methods
    * *("$method_name1", "$method_name2"), blocks calls to specific methods
    """

    def _decorator(target):
        target._disable_rpc = ("all",) if len(config) == 0 else config
        return target

    return _decorator
