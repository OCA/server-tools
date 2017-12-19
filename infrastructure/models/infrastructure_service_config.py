# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class InfrastructureServiceConfig(models.Model):

    _name = 'infrastructure.service.config'
    _description = 'Infrastructure Service Configuration'

    description = fields.Char()
    service_id = fields.Many2one(
        string='Service',
        comodel_name='infrastructure.service',
        required=True,
        ondelete='cascade',
    )
    memory_uom_id = fields.Many2one(
        string='Memory Units',
        comodel_name='product.uom',
        default=lambda s: s.env.ref(
            'product_uom_technology.product_uom_gib',
        ),
        domain="[('category_id.name', '=', 'Information')]",
        help='This unit represents all memory and storage statistics for '
             'this record.',
    )
    memory_limit = fields.Float()
    memory_reservation = fields.Float()
    memory_swap = fields.Float()
    memory_swappiness = fields.Float(
        help='This is the percentage of anonymous pages that the host kernel '
             'can swap out.'
    )
    cpu_limit = fields.Float(
        help='Amount of available CPU resources that an instance can use.',
    )
    cpu_pin = fields.Char(
        help='Limit of the specific CPUs or cores that an instance can use. '
             'This is either a comma separated list or hyphen separated '
             'range of CPUs/cores that an instance can use. The first core '
             'of the first CPU is numbered 0. A valid value might be ``0-3`` '
             '(to use the first, second, third, and fourth CPU/core) or '
             '``1,3`` (to use the second and fourth CPU/core).',
    )
    cpu_shares = fields.Integer(
        default=1024,
        help='This is the service weight in respect to other services, '
             'allowing for it to use greater or lesser proportions of '
             'the host machine\'s CPU cycles. This is typically only '
             'enforced when CPU cycles are constrained.',
    )
    log_driver = fields.Char()
    log_option_ids = fields.Many2many(
        string='Log Options',
        comodel_name='infrastructure.option',
    )
    volume_option_ids = fields.Many2many(
        string='Data Volumes',
        comodel_name='infrastructure.option.system',
    )
    device_option_ids = fields.Many2many(
        string='Devices',
        comodel_name='infrastructure.option.system',
    )
    image_uid = fields.Char(
        help='This is the unique identifier for the image in the remote '
             'image repository. Examples would be the image name on Docker '
             'Hub or the name of the AMI.',
    )
    label_ids = fields.Many2many(
        string='Labels',
        comodel_name='infrastructure.option',
    )
    port_options_ids = fields.Many2many(
        string='Ports',
        comodel_name='infrastructure.option.system',
        context='{"default_value_2_join": "/"}',
    )
    is_privileged = fields.Boolean(
        help='Does this service have privileged access to the host?',
    )
    scale_max = fields.Float(
        default=1,
    )
