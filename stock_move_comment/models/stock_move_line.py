from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = ['stock.move.line']

    comment = fields.Char(related='move_id.comment')
