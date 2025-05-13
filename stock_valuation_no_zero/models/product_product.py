# -*- coding: utf-8 -*-

from odoo import api, models, exceptions, _
from odoo.tools import float_is_zero

class ProductProduct(models.Model):
    _inherit = ['product.product']

    @api.constrains('standard_price')
    def _check_standard_price_no_zero(self):
        """ Check that standard_price is not zero """
        # product.product creation from product.template
        if self._context.get('create_product_product'):
            return
        
        zero_standard_price = self.filtered(lambda product:
            not product.standard_price or float_is_zero(
                product.standard_price,
                precision_rounding=product.uom_id.rounding
            )
        )
        print('product', self)
        print('product.standard_price', self.standard_price)
        print('product.uom_id.rounding', self.uom_id.rounding)
        print('self._context', self._context)

        if zero_standard_price:
            raise exceptions.ValidationError(_(
                "Zero cost is not permitted. Products:\n"
                "%s", "\n" . join(zero_standard_price.mapped('display_name'))
            ))

    @api.model_create_multi
    def create(self, vals_list):
        """ Forces check of constrains else it's passed"""
        res = super().create(vals_list)
        res._check_standard_price_no_zero()
        return res
