# -*- coding: utf-8 -*-

from odoo import api, models, fields, exceptions, _

class StockPicking(models.Model):
    _inherit = ['stock.picking']

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project'
    )

    @api.onchange('project_id')
    def _onchange_project_id(self):
        for picking in self:
            picking.move_ids.project_id = picking.project_id
