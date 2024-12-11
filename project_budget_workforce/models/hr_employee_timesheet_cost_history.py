# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import date_utils

class HrEmployeeTimesheetCostHistory(models.Model):
    _inherit = ["hr.employee.timesheet.cost.history"]

    #===== Fields =====#
    analytic_account_id = fields.Many2one(
        # related-like field to employee's or department's analytic
        comodel_name="account.analytic.account",
        compute='_compute_analytic_account_id',
        store=True
    )
    date_to = fields.Date(
        string='Date To',
        compute='_compute_date_to'
    )

    #===== Compute =====#
    @api.depends(
        'employee_id', 'employee_id.analytic_account_id',
        'department_id', 'department_id.analytic_account_id',
    )
    def _compute_analytic_account_id(self):
        for history in self:
            history.analytic_account_id = (
                history.department_id.analytic_account_id or
                history.employee_id.analytic_account_id
            )

    @api.depends(
        'department_id.timesheet_cost_history_ids.starting_date',
        'employee_id.timesheet_cost_history_ids.starting_date',
    )
    def _compute_date_to(self):
        """ `date_to` is either:
            * `starting_date - 1 day` of next entry in cost history, or
            * False if no next entry
        """
        # if not starting_date, can't compute date_to (should never happen)
        no_starting_date = self.filtered(lambda x: not x.starting_date)
        no_starting_date.date_to = fields.Date.today()
        self = self - no_starting_date
        if not self.ids: # early quit for perf., if already finished
            return
        
        # Get `starting_date`, per employee or department
        rg_result = self.sudo().read_group(
            domain=['|',
                ('employee_id', 'in', self.employee_id.ids),
                ('department_id', 'in', self.department_id.ids),
            ],
            groupby=['employee_id', 'department_id'],
            fields=['starting_dates:array_agg(starting_date)'],
            lazy=False
        )
        mapped_data = {'employee': {}, 'department': {}}
        for x in rg_result:
            field = 'department' if x['department_id'] and x['department_id'][0] else 'employee'
            mapped_data[field][x[field + '_id'][0]] = x['starting_dates']

        for entry in self:
            field = 'department' if entry.department_id.id else 'employee'
            dates_from = mapped_data[field].get(entry[field + '_id'].id, []) # all `starting_date` of siblings entry
            next_starting_date = [date for date in dates_from if date and date > entry.starting_date]
            entry.date_to = date_utils.subtract(min(next_starting_date), days=1) if next_starting_date else False
    
    
    #===== Button =====#
    def button_open_department_or_employee(self):
        """ On history costs tree view from Accounting app, to open Department or Employee form """

        model = 'department' if self.department_id.id else 'employee'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.' + model,
            'res_id': self[model + '_id'].id,
            'view_mode': 'form',
            'name': self[model + '_id'].name,
            'context': {'display_analytic': True}
        }
    