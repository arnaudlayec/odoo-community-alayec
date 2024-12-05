# -*- coding: utf-8 -*-

from odoo import Command, exceptions, fields
from odoo.tests.common import Form, TransactionCase

from odoo.addons.project_budget.tests.test_project_budget import TestAccountMoveBudgetProject

class TestProjectBudgetTimesheet(TestAccountMoveBudgetProject):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.project.budget_line_ids._compute_debit_credit()
        cls.project._compute_budget_line_sum()
        cls.Task = cls.env['project.task']
        cls.task1 = cls.Task.create({
            'name': 'Task Test 01',
            'project_id': cls.project.id,
            'analytic_account_id': cls.analytic.id,
            'planned_hours': cls.BUDGET_DATERANGE / 2 # half of available budget
        })
        cls.task2 = cls.Task.create({
            'name': 'Task Test 02',
            'project_id': cls.project.id,
            'analytic_account_id': cls.analytic.id, # same budget type
            # no budget yet
        })

    def test_01_available_budget(self):
        remaining = self.BUDGET_DATERANGE/2# the other half
        self.assertEqual(self.task1.available_budget, remaining)
        self.assertEqual(self.task2.available_budget, remaining)

    def test_02_available_budget_with_2_tasks(self):
        self.task2.planned_hours = self.BUDGET_DATERANGE/3
        remaining = self.BUDGET_DATERANGE * (1/2 - 1/3)

        self.assertEqual(round(self.task1.available_budget, 2), round(remaining, 2))
        self.assertEqual(round(self.task2.available_budget, 2), round(remaining, 2))

    def test_03_budget_raise(self):
        # Test if it raises correctly if task2 tries to take all budget while task1 already has reserved some
        with self.assertRaises(exceptions.UserError):
            self.task2.planned_hours = self.BUDGET_DATERANGE
