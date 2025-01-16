# -*- coding: utf-8 -*-

from odoo import models, fields

class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ['mrp.production', 'project.default.mixin']

    project_id = fields.Many2one(
        required=False # required in the view only, not ORM
    )