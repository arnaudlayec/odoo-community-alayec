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

        cls.production = cls.env['mrp.production'].create({
            'product_id': cls.product.id,
            'project_id': cls.project.id
        })

    def test_01_workorder_count(self):
        self.assertEqual(self.project.manufacturing_order_count, 1)

    def test_02_picking_project(self):
        self.assertEqual(self.production.picking_ids.project_id, self.project)
