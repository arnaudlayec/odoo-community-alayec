# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpWorkCenter(models.Model):
    _inherit = ["mrp.workcenter"]

    productivity_tracking = fields.Selection([
        ('none', "None"),
        ('global', "Global"),
        ('unit', "Quantitative")
    ], string="Productivity Tracking", default='none')
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
        help='Default unit of Work Order'
    )
