# -*- coding: utf-8 -*-
# © 2015 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# © 2016 Tecnativa, S.L. - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, exceptions


class BestMatchedLanguageNotFoundError(exceptions.MissingError):
    def __init__(self, lang):
        msg = (_("Best matched language (%s) not found.") % lang)
        super(BestMatchedLanguageNotFoundError, self).__init__(msg)
        self.lang = lang
