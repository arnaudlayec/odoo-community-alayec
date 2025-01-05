# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpWorkCenter(models.Model):
    _inherit = ["mrp.workcenter"]

    productivity_tracking = fields.Selection([
        ('global', "Global"),
        ('unit', "Quantitative")
    ], string="Productivity Tracking", default='global', required=True)
    tracking_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure'
    )
