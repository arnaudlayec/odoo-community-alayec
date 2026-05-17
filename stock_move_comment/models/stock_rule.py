from odoo import models

class StockRule(models.Model):
    _inherit = ['stock.rule']

    def _get_custom_move_fields(self):
        """Allow  to cascade the values when a child move is created from a rule"""
        return super()._get_custom_move_fields() + [
            "comment"
        ]
