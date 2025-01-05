# -*- coding: utf-8 -*-

from odoo.tests import common

class TestMrpProjectLink(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.project = cls.env['project.project'].name_create('Project Test 01')
        cls.product = cls.env['product.product'].create({
            'name': 'Product Test 01',
            'type': 'product',
            'tracking': 'none',
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
            'uom_po_id': cls.env.ref('uom.product_uom_unit').id
        })

    def test_workorder_count(self):
        self.assertEqual(self.project.workorder_count, 0)

        self.env['mrp.production'].create({
            'product_id': self.product.id,
            'project_id': self.project.id
        })

        self.assertEqual(self.project_workorder_count, 1)
