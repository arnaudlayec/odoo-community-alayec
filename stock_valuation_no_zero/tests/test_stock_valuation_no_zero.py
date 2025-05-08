# -*- coding: utf-8 -*-

from odoo import exceptions
from odoo.tests import common, tagged

@tagged('post_install', '-at_install')
class TestStockValuationNoZero(common.SingleTransactionCase):

    STANDARD_PRICE = 10.0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_01_product_standard_price(self):
        """ Test that a product with a zero standard price
            cannot be created
        """
        Product = self.env['product.product']

        # Should fail
        vals = {'name': 'Product Test 01', 'detailed_type': 'product'}
        with self.assertRaises(exceptions.ValidationError):
            Product.create(vals)
        
        # Should succeed
        vals['standard_price'] = self.STANDARD_PRICE
        try:
            self.product = Product.create(vals)
        except:
            self.fail("Product should be creatable with a standard price")

    def test_02_product_standard_price(self):
        """ Test that a product with a zero standard price
            cannot be created
        """
        Svl = self.env['stock.valuation.layer']

        # Should fail
        vals = {'product_id': self.product.id}
        with self.assertRaises(exceptions.ValidationError):
            Svl.create(vals)
        
        # Should succeed
        vals['unit_cost'] = self.STANDARD_PRICE
        try:
            Svl.create(vals)
        except:
            self.fail("Stock Valuation Layer should be creatable with a unit cost")
