# -*- coding: utf-8 -*-

from odoo import models

class ProductTemplate(models.Model):
    _inherit = ['product.template']

    def copy(self, default=None):
        """ Forces check of constrains else it's passed"""
        self.product_variant_ids._check_standard_price_no_zero()
        return super().copy(default)
