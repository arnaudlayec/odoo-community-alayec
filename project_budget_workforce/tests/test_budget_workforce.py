# -*- coding: utf-8 -*-

from odoo import Command, exceptions, fields
from odoo.tests.common import Form, TransactionCase

from odoo.addons.project_budget.tests.test_project_budget import TestAccountMoveBudgetProject

class TestBudgetWorkforce(TestAccountMoveBudgetProject):
    
    BUDGET_DATERANGE = 300.0
    HOUR_COST_22 = 30.0
    HOUR_COST_23 = 40.0
    AMOUNT = BUDGET_DATERANGE/2 * HOUR_COST_22 + BUDGET_DATERANGE/2 * HOUR_COST_23

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # New line in 'workforce' mode
        cls.analytic_workforce = cls.analytic.copy({
            'name': 'Analyic Account Test Workforce',
            'budget_type': 'service'
        })
        cls.line_workforce = cls.line_amount.copy({
            'type': 'workforce',
            'analytic_account_id': cls.analytic_workforce.id
        })

        # Date-ranged values per department, linked to the analytic account
        cls.History = cls.env['hr.employee.timesheet.cost.history'].sudo()
        cls.histories = cls.History.create([
            {
                'analytic_account_id': cls.analytic_workforce.id,
                "currency_id": cls.env.company.currency_id.id,
                "hourly_cost": cls.HOUR_COST_22,
                "starting_date": '2022-01-01',
            }, {
                'analytic_account_id': cls.analytic_workforce.id,
                "currency_id": cls.env.company.currency_id.id,
                "hourly_cost": cls.HOUR_COST_23,
                "starting_date": '2023-01-01',
            }
        ])
        cls.history2022, cls.history2023 = cls.histories

    #===== hr.employee.timesheet.cost.history =====#
    def test_01_cost_date_to(self):
        """ Ensure `date_to` is well computed """
        self.assertEqual(str(self.history2022.date_to), '2022-12-31')
        self.assertEqual(self.history2023.date_to, False)

    def test_02_line_credit(self):
        """ Test the correct valuation of budget line following dpt cost history """
        self.line_workforce.qty_debit = self.BUDGET_DATERANGE
        self.assertEqual(self.line_workforce.debit, self.AMOUNT)

    def test_03_change_valuation(self):
        """ Test change of valuation (@depends trigger) """
        self.history2022.hourly_cost = self.HOUR_COST_22 + 1.0
        self.assertTrue(self.line_workforce.debit != self.AMOUNT)

    def test_04_history_unlink_only_analytic(self):
        """ Test unlink is prevented of classic "history" lines
            (employees, departments, workcenters) and allowed
            when users unlink "analytic" lines
        """
        employee = self.env["hr.employee"].create({'name': 'Test Employee'})
        self.new_timesheet_cost_wizard(employee, 15.0, '2024-01-01')
        history_employee = self.History.search([('employee_id', '!=', False)])

        with self.assertRaises(exceptions.ValidationError):
            history_employee.unlink()
        
        try:
            self.histories.unlink()
        except:
            self.fail('Should be OK to delete "analytic" histories')

    def new_timesheet_cost_wizard(self, employee, cost, date_from):
        """Create a new wizard for this test's employee."""
        wizard = Form(
            self.env["hr.employee.timesheet.cost.wizard"].with_context(
                default_employee_id=employee.id,
                default_hourly_cost=cost,
                default_starting_date=date_from,
            )
        )
        wizard_result = wizard.save()
        wizard_result.update_employee_cost()
    