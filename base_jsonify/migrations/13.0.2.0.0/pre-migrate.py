# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    query = """ALTER TABLE "ir_exports_line" RENAME COLUMN "alias" TO "target";"""
    cr.execute(query)
