# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrEmployeeTimesheetCostHistory(models.Model):
    _inherit = ["hr.employee.timesheet.cost.history"]
    _order = "starting_date DESC"

    department_id = fields.Many2one(
        comodel_name="hr.department",
        string='Department'
    )
    employee_id = fields.Many2one(
        help='If empty, department cost applies'
    )
    