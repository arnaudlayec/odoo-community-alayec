# -*- coding: utf-8 -*-

from odoo import Command
from odoo.tests import common, tagged

@tagged('post_install', '-at_install')
class TestMrpProjectLink(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.project = cls.env['project.project'].create({'name': 'Project Test 01'})
        cls.product = cls.env['product.product'].create({
            'name': 'Product Test 01',
            'type': 'product',
            'tracking': 'none',
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
            'uom_po_id': cls.env.ref('uom.product_uom_unit').id
        })

        cls.production = cls.env['mrp.production'].create({
            'product_id': cls.product.id,
            'project_id': cls.project.id,
            'move_raw_ids': [Command.create({
                'product_id': cls.product.id,
                'product_uom_qty': 50.0,
            })]
        })

    def test_01_workorder_count(self):
        """ Verify if project count of MO works fine """
        self.assertEqual(self.project.manufacturing_order_count, 1)

    def test_02_picking_project(self):
        """ Verify if project falls down to the picking and moves """
        pass
        # this test is missing; we should:
        # 1/ ensure 2-steps routes
        self.production.action_confirm()
        pickings = self.production.picking_ids
        self.assertEqual(pickings.project_id, self.project)
        self.assertEqual(pickings.move_ids.project_id, self.project)
