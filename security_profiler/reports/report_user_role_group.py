# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ReportUsersProfilerSessions(models.AbstractModel):
    _name = 'report.security_profiler.res_users_profiler_sessions_report'
    _description = 'Users Profiler Sessions Report'

    @api.model
    def get_report_values(self, docids, data=None):

        def snakecase_model_name(string):
            string = string.replace(".", "_")
            return string

        docs = []
        for session_id in docids:
            # session
            session = self.env['res.users.profiler.sessions'].browse(
                session_id)
            # role name
            role_name = session.user_role_name.lower().strip().replace(
                ".", "_").replace(" ", "_")

            # security group
            model_data = self.env['ir.model.data'].sudo().search_read(
                [('model', '=', 'res.groups'),
                 ('res_id', 'in', session.implied_groups.ids)],
                ['module', 'name', 'res_id'])
            xml_ids = ["%s.%s" % (d['module'], d['name']) for d in model_data]
            ref_xml_ids = ','.join(["(4,ref(%s))" % x for x in xml_ids])
            implied_ids = ""
            if ref_xml_ids:
                implied_ids = """
        <field name="implied_ids" eval="[%s]"/>""" % ref_xml_ids
            group_id = "group_user_profiler_%s" % role_name
            security = """
    <record id="%s" model="res.groups">
        <field name="name">User Profiler - %s</field>%s
        <field name="category_id" ref="base.module_category_hidden"/>
    </record>
""" % (group_id, session.user_role_name, implied_ids)

            # access rights
            res_models = {}
            for profiled_access in session.profiled_accesses_ids.filtered(
                    lambda a: a.new_access):
                if profiled_access.res_model in res_models:
                    res_models[profiled_access.res_model] = [
                        res_models[profiled_access.res_model][
                            0] or profiled_access.count_read,
                        res_models[profiled_access.res_model][
                            1] or profiled_access.count_write,
                        res_models[profiled_access.res_model][
                            2] or profiled_access.count_create,
                        res_models[profiled_access.res_model][
                            3] or profiled_access.count_unlink,
                    ]
                else:
                    res_models[profiled_access.res_model] = [
                        bool(profiled_access.count_read),
                        bool(profiled_access.count_write),
                        bool(profiled_access.count_create),
                        bool(profiled_access.count_unlink),
                    ]
            accesses = ""
            for res_model in res_models:
                snake_model = snakecase_model_name(res_model)
                module = self.env[res_model]._original_module
                accesses += """
access_security_profiler_%s_%s,security_profiler_%s %s,""" \
"""%s.model_%s,group_%s,%s,%s,%s,%s""" % (
                    snake_model, role_name, snake_model, role_name, module,
                    snake_model, group_id, res_models[res_model][0],
                    res_models[res_model][1],
                    res_models[res_model][2],
                    res_models[res_model][3],
                )

            # actions
            actions = ""
            for profiled_action in session.profiled_actions_ids.filtered(
                    lambda a: a.new_action):
                actions += """
    <record id="%s" model="%s">
        <field name="groups_id" eval="[(4,ref(%s))]"/>
    </record>
""" % (profiled_action.action.xml_id, profiled_action.action_type, group_id)

            # menus
            menus = session.profiled_menus_ids.filtered(
                lambda m: m not in session.implied_menus)
            model_data = self.env['ir.model.data'].sudo().search_read(
                [('model', '=', 'res.groups'),
                 ('res_id', 'in', menus.mapped('groups_id').ids)],
                ['module', 'name', 'res_id'])
            g_dict = {d['res_id']: "%s.%s" % (d['module'], d['name'])
                      for d in model_data}
            model_data = self.env['ir.model.data'].sudo().search_read(
                [('model', '=', 'ir.ui.menu'),
                 ('res_id', 'in', menus.ids)],
                ['module', 'name', 'res_id'])
            menus = ""
            for d in model_data:
                menu = self.env['ir.ui.menu'].sudo().browse(d['res_id'])
                menu_groups = menu.groups_id
                if not menu_groups:
                    while not menu_groups:
                        if menu.parent_id:
                            menu = menu.parent_id
                            menu_groups = menu.groups_id
                        else:
                            break
                    g_list = [g_dict[g.id] for g in menu_groups]
                else:
                    g_list = []
                ref_groups = ','.join(
                    ["(4,ref(%s))" % x for x in g_list] + [
                        "(4,ref(%s))" % group_id])
                menus += """
    <record id="%s.%s" model="ir.ui.menu">
        <field name="groups_id" eval="[%s]"/>
    </record>
""" % (d['module'], d['name'], ref_groups)

            # doc
            doc = {
                'date': fields.Date.context_today(self),
                'session': session,
                'security': security,
                'accesses': accesses,
                'actions': actions,
                'menus': menus,
            }
            docs.append(doc)

        return {
            'doc_ids': docids,
            'doc_model': 'res.users.profiler.sessions',
            'docs': docs,
        }
