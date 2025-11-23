# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrEmployeeTimesheetCostHistory(models.Model):
    _inherit = ["hr.employee.timesheet.cost.history"]
    _order = "starting_date DESC"

    workcenter_id = fields.Many2one(
        readonly=True,
        string='Workcenter',
        comodel_name="mrp.workcenter",
        ondelete='cascade',
    )
    employee_id = fields.Many2one(
        ondelete='cascade',
    )
