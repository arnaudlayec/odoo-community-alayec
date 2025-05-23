# -*- coding: utf-8 -*-

from odoo import fields
from odoo.tests import SingleTransactionCase, common

class TestPurchaseOrderLineInput_Base(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env["project.project"].create(
            {"name": "Test"}
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test", "purchase_general_discount": 10.0}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "service"}
        )
        order_form = common.Form(cls.env["purchase.order"])
        order_form.project_id = cls.project
        order_form.partner_id = cls.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom = cls.product.uom_id
            line_form.product_qty = 1
            line_form.price_unit = 1000.00

class TestPurchaseOrderLineInput(TestPurchaseOrderLineInput_Base):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def test_01_default_partner_discount(self):
        self.order.onchange_partner_id()
        self.assertEqual(
            self.order.general_discount,
            fields.first(self.project.purchase_discount_ids).discount
        )
