# -*- coding: utf-8 -*-

from odoo import models, fields

class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ['mrp.production', 'project.default.mixin']

    def _prepare_procurement_group_vals(self, values):
        return super()._prepare_procurement_group_vals(values) | {
            'project_id': self.project_id.id
        }
