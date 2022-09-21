# -*- coding: utf-8 -*-
# from odoo import http


# class BaseModuleMigrationInfo(http.Controller):
#     @http.route('/module_migration_info/module_migration_info/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/module_migration_info/module_migration_info/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('module_migration_info.listing', {
#             'root': '/module_migration_info/module_migration_info',
#             'objects': http.request.env['module_migration_info.module_migration_info'].search([]),
#         })

#     @http.route('/module_migration_info/module_migration_info/objects/<model("module_migration_info.module_migration_info"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('module_migration_info.object', {
#             'object': obj
#         })
