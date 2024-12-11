# -*- coding: utf-8 -*-

from odoo import fields, exceptions
from odoo.tests.common import Form

from odoo.addons.hr_timesheet.tests.test_timesheet import TestCommonTimesheet


class TestProjectTaskAnalyticHr(TestCommonTimesheet):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.analytic_account.timesheetable = True
    

    def test_01_employee_analytic(self):
        """ Ensure analytic account set on department waterfalls to its employee """
        # department
        f = Form(self.env['hr.department'])
        f.name = 'Department Test 01'
        f.analytic_account_id = self.analytic_account
        department = f.save()

        # employee
        with Form(self.empl_employee) as f:
            f.department_id = department
        
        self.assertEqual(self.empl_employee._get_analytic_account_id(), self.analytic_account)
    
    def test_02_analytic_display_name(self):
        """ Ensure timesheetable display_name is well computed """
        char = self.analytic_account.display_name[-1]
        self.assertEqual(char, '🕓')
