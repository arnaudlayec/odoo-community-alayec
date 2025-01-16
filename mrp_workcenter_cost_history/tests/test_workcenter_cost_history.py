# -*- coding: utf-8 -*-

from odoo import Command, exceptions, fields
from odoo.tests.common import Form, SingleTransactionCase
from freezegun import freeze_time

from datetime import date, datetime, timedelta

class TestWorkcenterCostHistory(SingleTransactionCase):

    SMALL_COST = 40.0
    BIG_COST = 50.0
    SMALL_DATE = date(2024, 1, 1) # 1st january
    MIDDLE_DATE = date(2024, 2, 1) # 1st february
    BIG_DATE = date(2024, 3, 1) # 1st march

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Costs history
        cls.Wizard = cls.env["hr.employee.timesheet.cost.wizard"]

        # Analytic
        cls.plan = cls.env['account.analytic.plan'].create({'name': 'Test Plan 001'})
        cls.analytic = cls.env['account.analytic.account'].create({
            'name': 'Account Test 001',
            'plan_id': cls.plan.id,
        })

        # Manufacturing
        cls.product = cls.env['product.product'].create({
            'name': 'Product Test 01',
            'type': 'product',
            'tracking': 'none',
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
            'uom_po_id': cls.env.ref('uom.product_uom_unit').id
        })

        cls.production = cls.env['mrp.production'].create({
            'name': 'Test Production 01',
            'product_id': cls.product.id,
        })
        cls.workcenter = cls.env['mrp.workcenter'].create({
            'name': 'Test Workcenter 01',
            'costs_hour_account_id': cls.analytic.id
        })
        cls.workorder = cls.env['mrp.workorder'].create({
            'name': 'Test Workorder 01',
            'production_id': cls.production.id,
            'workcenter_id': cls.workcenter.id,
            'product_uom_id': cls.product.uom_id.id
        })

        # Productivity
        cls.productivity = cls.env['mrp.workcenter.productivity'].create([{
            'date_start': cls.MIDDLE_DATE,
            'date_end': cls.MIDDLE_DATE + timedelta(days=2), # 48h
            'workcenter_id': cls.workcenter.id,
            'workorder_id': cls.workorder.id,
            'loss_id': cls.env.ref('mrp.block_reason7').id
        }])
    
    def new_workcenter_cost_wizard(self, cost=None, date_from=None):
        """ Create a new wizard for the test workcenter """
        wizard = Form(
            self.Wizard.with_context(
                default_workcenter_id = self.workcenter.id,
                default_hourly_cost = cost or self.SMALL_COST,
                default_starting_date = date_from or self.MIDDLE_DATE,
            )
        )
        wizard_result = wizard.save()
        wizard_result.update_employee_cost()

    # ---- Costs histories ----
    def test_01_workcenter_history(self):
        """ Ensure basic write on workcenter cost with wizard are kept in history """
        self.new_workcenter_cost_wizard()
        self.assertEqual(self.workcenter.costs_hour, self.SMALL_COST)

    def test_02_bad_costs_workcenter(self):
        """ Ensure bad costs are cleaned """
        self.new_workcenter_cost_wizard(self.BIG_COST, self.SMALL_DATE)
        
        self.assertEqual(self.workcenter.costs_hour, self.BIG_COST)
        self.assertEqual(len(self.workcenter.cost_history_ids), 1)

    # ---- Valuation ----
    def _test_cost(self, cost):
        self.assertEqual(self.productivity.cost, self.productivity.duration/60 * cost)
        self.assertEqual(
            self.workorder.wc_analytic_account_line_id.amount,
            self.productivity.duration/60 * cost
        )
    
    def test_03_valuation_after_productivity(self):
        # Cost valuation after productivity => we value, better than 0€
        self._test_cost(self.BIG_COST)
        
    def test_04_valuation_before_productivity(self):
        # Cost valuation before productivity => valued normally too
        self.new_workcenter_cost_wizard(self.SMALL_COST, self.SMALL_DATE)
        self._test_cost(self.SMALL_COST)
        
    def test_05_valuation_before_and_after_productivity(self):
        # Cost valuation before & after productivity => same than previous
        self.new_workcenter_cost_wizard(self.BIG_COST, self.BIG_DATE)
        self._test_cost(self.SMALL_COST)
        
    def test_06_valuation_within_productivity(self):
        # Productivity valued with 2 costs
        self.new_workcenter_cost_wizard(self.SMALL_COST, self.MIDDLE_DATE)
        self.new_workcenter_cost_wizard(self.BIG_COST, self.MIDDLE_DATE + timedelta(days=1))
        self._test_cost((self.SMALL_COST + self.BIG_COST) / 2)
