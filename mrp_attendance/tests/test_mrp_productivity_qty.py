# -*- coding: utf-8 -*-

from odoo.tests import common, tagged, Form
from datetime import timedelta

@tagged('post_install', '-at_install')
class TestMrpProductivityQuantity(common.SingleTransactionCase):

    QTY_PRODUCTION = 10.0
    HOURS_EXPECTED = 100.0
    UNIT_TIME_AVG = HOURS_EXPECTED / QTY_PRODUCTION # 10h/unit

    HOURS_DONE = 20 # 20h => perf -100%
    QTY_DONE = 1
    UNIT_TIME_REAL = HOURS_DONE / QTY_DONE # 20h done for 1 unit
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Workcenters
        cls.workcenter = cls.env['mrp.workcenter'].create([{
            # don't test 'global' tracking (nothing much to test)
            'name': 'Test Workcenter Unit 01',
            'productivity_tracking': 'unit',
            'product_uom_id': cls.env.ref('uom.product_uom_unit').id,
        }])
        
        # Production
        cls.product = cls.env['product.product'].create({
            'name': 'Product Test 01',
            'type': 'product',
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
            'uom_po_id': cls.env.ref('uom.product_uom_unit').id
        })
        cls.production = cls.env['mrp.production'].create({
            'name': 'Test Production 01',
            'product_id': cls.product.id,
        })

        # Workorder
        cls.workorder = cls.env['mrp.workorder'].create({
            'name': 'Test Workorder 01',
            'production_id': cls.production.id,
            'workcenter_id': cls.workcenter.id,
            'duration_expected': cls.HOURS_EXPECTED * 60,
            'qty_production': cls.QTY_PRODUCTION,
            'productivity_tracking': cls.workcenter.productivity_tracking,
            'product_uom_id': cls.workcenter.product_uom_id.id,
        })

        # Productivity
        cls.productivity = cls.env['mrp.workcenter.productivity'].create({
            'duration': cls.HOURS_DONE * 60,
            'workcenter_id': cls.workcenter.id,
            'workorder_id': cls.workorder.id,
            'loss_id': cls.env.ref('mrp.block_reason7').id,
        })


    def test_01_productivity_date_start(self):
        """ Test compute date_end = date_start + duration """
        self.assertEqual(self.productivity.date_end, self.productivity.date_start + timedelta(hours=self.HOURS_DONE))

    def test_02_qty_produced(self):
        """ Test if:
            1. Sum is OK at workorder level from productivity (_compute_qty_produced)
            2. Finishing workorder doesn't change `qty_produced` (button_finish)
        """
        self.productivity.qty_production = self.QTY_DONE
        self.assertEqual(self.workorder.qty_produced, self.QTY_DONE)

        self.workorder.button_finish()
        self.assertEqual(self.workorder.qty_produced, self.QTY_DONE)

    def test_03_wo_performance(self):
        """ Test workorder performance calculation:
            (example) 1 productivity of 20h to produce 1 unit => 10h lost => -100%
        """
        self.assertEqual(self.workorder.performance, -1 * (self.UNIT_TIME_REAL - self.UNIT_TIME_AVG) / self.UNIT_TIME_AVG * 100)
