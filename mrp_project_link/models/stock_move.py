# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class StockMove(models.Model):
    _inherit = ['stock.move']

    project_id = fields.Many2one(
        comodel_name='project.project',
        compute='_compute_project_id',
    )

    @api.depends(lambda self: self._get_fields_project_id())
    def _compute_project_id(self):
        """ Compute `stock_move.project_id` from the fields listed in `_get_fields_project_id` """
        fields = self._get_fields_project_id()
        for move in self:
            for field in fields:
                project_id = move[field].project_id
                if project_id:
                    move.project_id = project_id
                    break
    
    def _get_fields_project_id(self):
        return [
            'picking_id',
            'created_production_id',
            'production_id',
            'raw_material_production_id'
        ]

class StockMoveLine(models.Model):
    _inherit = ['stock.move.line']

    project_id = fields.Many2one(
        related='move_id.project_id'
    )
