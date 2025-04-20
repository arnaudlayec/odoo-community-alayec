# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class StockMoveLine(models.Model):
    _inherit = ['stock.move.line']

    comment = fields.Char(related='move_id.comment')
