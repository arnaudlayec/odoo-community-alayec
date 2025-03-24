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
                move.project_id = move[field].project_id
                if move.project_id:
                    break
    
    def _get_fields_project_id(self):
        """ Fields (in order) in which to lookup `project_id`
            Useful when `project_id` may come from different origins
        """
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
