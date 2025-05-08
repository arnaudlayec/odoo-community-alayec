# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class StockMoveLine(models.Model):
    _inherit = ['stock.move.line']

    project_id = fields.Many2one(
        related='move_id.project_id',
        store=True,
    )
    picking_type_id = fields.Many2one(
        # for searchpanel group view
        store=True,
    )
