# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command

class StockMove(models.Model):
    _inherit = ['stock.move']

    project_id = fields.Many2one(
        comodel_name='project_id',
        string='Project'
    )

    def _get_new_picking_values(self):
        return super()._get_new_picking_values() | {
            'project_id': len(self.project_id) == 1 and self.project_id.id
        }