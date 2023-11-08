# Copyright 2023 FactorLibre (https://factorlibre.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


def get_field_unidecode(field):
    """i..e, 'field@?unidecode?'"""
    if field and "@?" in field and "?" in field:
        i = field.index("@?")
        j = field.index("?", i)
        cond = field[i + 2 : j]
        try:
            if cond or cond == "":
                return (field[:i], True)
        except Exception:
            return (field.replace("@?%s?" % cond, ""), False)
    return (field, False)
