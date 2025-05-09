# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, exceptions, _
from odoo.tools import float_is_zero

class StockValuationLayer(models.Model):
    _inherit = ['stock.valuation.layer']

    @api.constrains('unit_cost')
    def _check_unit_cost_no_zero(self):
        """ Check that unit cost is not 0.00€ """
        zero_unit_cost = self.filtered(lambda svl:
            svl.quantity > 0 and (
                not svl.unit_cost or
                float_is_zero(svl.unit_cost, precision_rounding=svl.product_id.uom_id.rounding)
            )
        )
        if zero_unit_cost:
            raise exceptions.ValidationError(_(
                "Valuating products move with zero unit cost is not accepted. "
                "Products:\n"
                "%s", "\n" . join(zero_unit_cost.product_id.mapped('display_name'))
            ))
