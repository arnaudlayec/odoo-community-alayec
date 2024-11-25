# -*- coding: utf-8 -*-

from odoo import fields, exceptions, Command
from odoo.tests import common, Form

class TestSaleProjectLink(common.SingleTransactionCase):

    PRODUCT_PRICE = 10.0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Partner
        ResPartner = cls.env['res.partner']
        cls.partner = ResPartner.create({'name': 'Partner'})

        # Product
        Product = cls.env['product.product']
        cls.product = Product.create({
            'name': 'Product',
            'list_price': cls.PRODUCT_PRICE,
        })

        # Project
        cls.project = cls.env['project.project'].create({
            'name': 'Project Test 01',
            'sequence_code': 'Test-00001',
            'partner_id': cls.partner.id
        })

        # Sale Order
        cls.order = cls.env['sale.order'].create({
            'project_id': cls.project.id,
            'partner_id': cls.partner.id,
            'order_line': [
                Command.create({'product_id': cls.product.id}),
                Command.create({'product_id': cls.product.id}),
            ]
        })


    def test_01_seq_project_tmpl(self):
        """ Test the project's specific sequence for its Sales Order """
        self.assertTrue(self.project.sale_order_sequence_id.id)

        self.seq_tmpl = self.env.ref('sale_project_link.seq_sale_order_project_template')
        self.assertEqual(
            self.project.sale_order_sequence_id.prefix,
            self.project.sequence_code + self.seq_tmpl.prefix
        )

    def test_02_seq_sale_prefix(self):
        """ Test if sale order sequence follow's project code """
        self.assertTrue(self.order.name.startswith(self.project.sequence_code))

    def test_03_sale_fields_from_project(self):
        """ Test syncho of project fields to sale order """
        self.assertEqual(self.order.partner_id.id, self.project.partner_id.id)

    def test_04_project_sale_total(self):
        """ Test project's totals """
        self.assertEqual(self.project.sale_order_count, 1)
        self.assertEqual(self.project.sale_order_sum, self.PRODUCT_PRICE * 2)

    def test_05_seq_sale_order_no_project(self):
        """ Test creation of sale order with no project (optional field) """
        order_no_project = self.order.copy({'project_id': False})
        self.assertTrue(order_no_project.name)
