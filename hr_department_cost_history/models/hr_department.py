# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrDepartment(models.Model):
    _inherit = ["hr.department"]

    hourly_cost = fields.Monetary(
        string='Hourly Cost',
        currency_field='currency_id',
        groups="hr.group_hr_user",
        default=0.0,
    )
    timesheet_cost_history_ids = fields.One2many(
        comodel_name="hr.employee.timesheet.cost.history",
        inverse_name="department_id",
        copy=False,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id',
        readonly=True
    )
