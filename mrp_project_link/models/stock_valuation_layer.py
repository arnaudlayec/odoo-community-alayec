# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command

class StockValuationLayer(models.Model):
    _inherit = ['stock.valuation.layer']

    project_id = fields.Many2one(
        comodel_name='project.project',
        compute='_compute_project_id',
        store=True,
        index=True,
    )

    @api.depends(lambda self: self._get_fields_project_id())
    def _compute_project_id(self):
        fields = [
            field for field in self._get_fields_project_id()
            if hasattr(self[field], 'project_id')
        ]
        for svl in self:
            for field in fields:
                project_id = svl[field].project_id
                if project_id:
                    svl.project_id = project_id
                    break
    
    def _get_fields_project_id(self):
        return [
            'stock_move_id',
            'stock_valuation_layer_id',
            'account_move_id',
        ]
    