# -*- coding: utf-8 -*-

from odoo import models, fields

class WorkOrder(models.Model):
    _name = "mrp.production"
    _inherit = ['mrp.production', 'project.default.mixin']

    description = fields.Char(
        string='Description'
    )
    