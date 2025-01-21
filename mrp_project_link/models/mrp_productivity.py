# -*- coding: utf-8 -*-

from odoo import models, fields

class MrpProductivity(models.Model):
    _inherit = ["mrp.workcenter.productivity"]

    project_id = fields.Many2one(related='production_id.project_id', store=True)
    