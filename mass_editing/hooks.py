# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def uninstall_hook(cr, registry):
    """Delete the actions that were created with mass_editing when
    the module is uninstalled"""
    cr.execute("""DELETE FROM ir_act_window
                  WHERE res_model = 'mass.editing.wizard'""")
    return True
