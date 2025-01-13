# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions, _

class StockMove(models.Model):
    _inherit = ['stock.move']

    project_id = fields.Many2one(
        related='picking_id.project_id'
    )

class StockMoveLine(models.Model):
    _inherit = ['stock.move.line']

    project_id = fields.Many2one(
        related='move_id.project_id'
    )
