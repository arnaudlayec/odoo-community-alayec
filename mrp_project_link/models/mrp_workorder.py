# -*- coding: utf-8 -*-

from odoo import models, fields

class MrpWorkOrder(models.Model):
    _inherit = ["mrp.workorder"]

    project_id = fields.Many2one(related='production_id.project_id', store=True)
    