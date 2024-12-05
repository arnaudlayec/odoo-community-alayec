# -*- coding: utf-8 -*-

from odoo import fields, exceptions
from odoo.tests.common import Form

from odoo.addons.hr_timesheet.tests.test_timesheet import TestCommonTimesheet


class TestProjectTaskAnalyticHr(TestCommonTimesheet):
    def test_01_employee_analytic(self):
        # department
        f = Form(self.env['hr.department'])
        f.name = 'Department Test 01'
        f.analytic_account_id = self.analytic_account
        department = f.save()

        # employee
        with Form(self.empl_employee) as f:
            f.department_id = department
        
        self.assertEqual(self.empl_employee._get_analytic_account_id(), self.analytic_account)
