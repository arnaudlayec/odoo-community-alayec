# -*- coding: utf-8 -*-

from odoo import Command, exceptions, fields
from odoo.tests.common import Form, TransactionCase

from odoo.addons.hr_employee_cost_history.tests.test_hr_timesheet import HrEmployeeCostHistory

from datetime import date
from dateutil.relativedelta import relativedelta

class TestDepartmentCostHistory(HrEmployeeCostHistory):

    DEFAULT_COST = 45.0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Department
        cls.Department = cls.env['hr.department']
        cls.department = cls.Department.create({
            'name': 'Test Department 01',
            'member_ids': [Command.set(cls.employee.ids)]
        })
        cls.department2 = cls.Department.create({'name': 'Test Department 02'})

        # Costs history
        cls.Wizard = cls.env["hr.employee.timesheet.cost.wizard"]

    def new_department_cost_wizard(self, cost=None, date_from=None):
        """ Create a new wizard for the test department """
        wizard = Form(
            self.Wizard.with_context(
                default_department_id = self.department.id,
                default_hourly_cost = cost or self.DEFAULT_COST,
                default_starting_date = date_from or date.today(),
            )
        )
        wizard_result = wizard.save()
        wizard_result.update_employee_cost()
    

    def test_01_department_history(self):
        """ Ensure basic write on Department cost with wizard are kept in history """
        self.new_department_cost_wizard()
        self.assertEqual(self.department.hourly_cost, self.DEFAULT_COST)
    
    def test_02_cost_waterfall_employee(self):
        """ Ensure department hourly costs waterfalls to employees """
        self.new_department_cost_wizard()
        self.assertEqual(self.employee.hourly_cost, self.DEFAULT_COST)

    def test_03_bad_costs_department(self):
        """ Ensure bad costs are cleaned, on department and employees """
        new_cost = self.DEFAULT_COST - 10.0
        self.new_department_cost_wizard(
            new_cost,
            date.today() - relativedelta(days=10)
        )
        self.assertEqual(self.department.hourly_cost, new_cost)
        self.assertEqual(self.employee.hourly_cost, new_cost)
        self.assertEqual(len(self.department.timesheet_cost_history_ids), 1)

    def test_04_priority_closest_cost(self):
        """ Test co-existence of both employee and department costs,
            and priority over the closest
        """
        # Employee (oldest)
        employee_cost = 12.0
        self.new_timesheet_cost_wizard( # method in tests of other module `hr_employee_cost_history`
            self.employee,
            employee_cost,
            date.today() - relativedelta(days=10)
        )
        # Department (closest: should take priority)
        department_cost = 11.0
        self.new_department_cost_wizard(
            department_cost,
            date.today() - relativedelta(days=5)
        )
        self.assertEqual(self.employee.hourly_cost, department_cost)

    def test_05_employee_department_change(self):
        """ Test change of employee's department
            => employee's cost & history should align with department's
        """
        # Employee: set cost in future
        employee_cost, date_from = 12.0, date.today() - relativedelta(days=10)
        self.new_timesheet_cost_wizard(self.employee, employee_cost, date_from)
        
        # Employee's department: change it
        self.employee.department_id = self.department2

        # [Test] Employee's hourly_cost aligned to new department & no history in ftuure
        self.assertEqual(self.employee.hourly_cost, self.department2.department_cost)
        self.assertFalse(self.employee.timesheet_cost_history_ids.filtered_domain(
            [("date", ">=", date.today())]
        ))
