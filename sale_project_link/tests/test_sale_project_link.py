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
            'partner_id': cls.partner.id
        })
        cls.order.order_line = [
            Command.create({'product_id': cls.product.id}),
            Command.create({'product_id': cls.product.id}),
        ]

    #----- sale.order (sequence & fields) -----#
    def test_01_seq_sale_order_no_project(self):
        """ Test creation of sale order with no project (optional field) """
        order_no_project = self.order.copy({'project_id': False})
        self.assertTrue(order_no_project.name)
    
    def test_02_seq_project_tmpl(self):
        """ Test the project's specific sequence for its Sales Order """
        self.assertTrue(self.project.sale_order_sequence_id.id)

        self.seq_tmpl = self.env.ref('sale_project_link.seq_sale_order_project_template')
        self.assertEqual(
            self.project.sale_order_sequence_id.prefix,
            self.project.sequence_code + self.seq_tmpl.prefix
        )

    def test_03_seq_sale_prefix(self):
        """ Test if sale order sequence follow's project code """
        self.assertTrue(self.order.name.startswith(self.project.sequence_code))

    def test_04_sale_fields_from_project(self):
        """ Test syncho of project fields to sale order """
        self.assertEqual(self.order.partner_id.id, self.project.partner_id.id)

    #----- sale.order.line (project analytic) -----#
    def test_05_analytic_order_line(self):
        """ Test if project's analytic is well set automatically on sale order line """
        self.assertTrue(self.project.analytic_account_id in self.order.order_line.analytic_ids)

        with self.assertRaises(exceptions.ValidationError):
            self.order.order_line._replace_analytic(
                replaced_ids=self.project.ids,
                added_id=self.project.copy({'name': 'Test Project 002'}).id
            )

    #----- project.project -----#
    def test_06_project_sale_total(self):
        """ Test project's totals """
        self.assertEqual(self.project.sale_order_count, 1)
        self.assertEqual(self.project.sale_order_sum, self.PRODUCT_PRICE * 2)

    #----- account.move -----#
    def test_07_invoice(self):
        """ Test project transfer to invoice """
        move = self.order._create_invoices()
        self.assertEqual(move.project_id, self.project)
        self.assertEqual(move.line_ids.project_id, self.project)
