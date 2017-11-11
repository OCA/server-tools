# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def uninstall_hook(cr, registry):
    cr.execute("""SELECT id FROM ir_act_window
               WHERE res_model = 'mass.editing.wizard'""")
    for res in cr.dictfetchall():
        cr.execute("DELETE FROM ir_act_window WHERE id = '%s'" % res.get('id'))
    return True
