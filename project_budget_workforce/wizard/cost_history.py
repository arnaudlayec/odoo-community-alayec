# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HrEmployeeTimesheetCost(models.TransientModel):
    _inherit = ["hr.employee.timesheet.cost.wizard"]

    def update_employee_cost(self):
        return super(
            HrEmployeeTimesheetCost,
            self.with_context(allow_unlink_cost_history=1)
        ).update_employee_cost()
    