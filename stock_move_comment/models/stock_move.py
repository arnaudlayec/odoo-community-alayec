from odoo import models, fields

class StockMove(models.Model):
    _inherit = ['stock.move']

    comment = fields.Char(string='Comment')

    def _prepare_procurement_values(self):
        """Allow  to cascade the values when a child move is created from a rule"""
        return super()._prepare_procurement_values() | {
            "comment": self.comment,
        }
