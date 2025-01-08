# -*- coding: utf-8 -*-

from odoo import models, fields

class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ['mrp.production', 'project.default.mixin']
    _rec_name = 'display_name'

    description = fields.Char(
        string='Description'
    )
    
    def _compute_display_name(self):
        for mo in self:
            mo.display_name = '[{}] {}' . format(self.name, self.description) 

    #===== `project_id` on `move_ids` =====#
    def _get_move_raw_values(self, product_id, product_uom_qty, product_uom, operation_id=False, byproduct_id=False, cost_share=0):
        return super()._get_move_raw_values(product_id, product_uom_qty, product_uom, operation_id, bom_line) | {
            'project_id': self.project_id.id
        }

    def _get_move_finished_values(self, product_id, product_uom_qty, product_uom, operation_id=False, byproduct_id=False, cost_share=0):
        return super()._get_move_finished_values(product_id, product_uom_qty, product_uom, operation_id, byproduct_id, cost_share) | {
            'project_id': self.project_id.id
        }
