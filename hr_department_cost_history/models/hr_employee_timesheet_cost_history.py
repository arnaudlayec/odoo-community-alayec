# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions

class HrEmployeeTimesheetCostHistory(models.Model):
    _inherit = ["hr.employee.timesheet.cost.history"]

    #===== Fields =====#
    department_id = fields.Many2one(
        readonly=True,
        comodel_name="hr.department",
        string='Department',
        ondelete='cascade',
    )
    employee_id = fields.Many2one(
        readonly=True,
        ondelete='cascade',
        help='If empty, department cost applies',
    )
