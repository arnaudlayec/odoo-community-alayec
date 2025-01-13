# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrEmployeeTimesheetCostHistory(models.Model):
    _inherit = ["hr.employee.timesheet.cost.history"]
    _order = "starting_date DESC"

    workcenter_id = fields.Many2one(
        comodel_name="mrp.workcenter",
        string='Workcenter',
        ondelete='cascade',
    )
    employee_id = fields.Many2one(
        ondelete='cascade',
    )
