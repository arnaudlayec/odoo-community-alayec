# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import date_utils

class HrEmployeeTimesheetCostHistory(models.Model):
    _inherit = ["hr.employee.timesheet.cost.history"]

    #===== Fields =====#
    analytic_account_id = fields.Many2one(
        # related-like field to employee's, department's or workcenter's analytic
        comodel_name="account.analytic.account",
        compute='_compute_analytic_account_id',
        store=True
    )
    date_to = fields.Date(
        string='Date To',
        compute='_compute_date_to'
    )

    #===== Compute =====#
    # TO IMPROVE : we could use a related field to store employee_id, department_id, workcenter_id, etc...
    # to be agnostic of the model having a cost history and free the module manifest dependencies
    @api.depends(
        'employee_id', 'employee_id.analytic_account_id',
        'department_id', 'department_id.analytic_account_id',
        'workcenter_id', 'workcenter_id.costs_hour_account_id',
    )
    def _compute_analytic_account_id(self):
        for history in self:
            history.analytic_account_id = (
                history.department_id.analytic_account_id or
                history.employee_id.analytic_account_id or
                history.workcenter_id.costs_hour_account_id
            )

    @api.depends(
        'department_id.timesheet_cost_history_ids.starting_date',
        'employee_id.timesheet_cost_history_ids.starting_date',
        'workcenter_id.cost_history_ids.starting_date',
    )
    def _compute_date_to(self):
        """ `date_to` is either:
            * `starting_date - 1 day` of next history in cost history, or
            * False if no next history
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
                ('workcenter_id', 'in', self.workcenter_id.ids),
            ],
            groupby=['employee_id', 'department_id', 'workcenter_id'],
            fields=['starting_dates:array_agg(starting_date)'],
            lazy=False
        )
        mapped_data = {'employee_id': {}, 'department_id': {}, 'workcenter_id': {}}
        for x in rg_result:
            field = self._get_field(x)
            mapped_data[field][x[field][0]] = x['starting_dates']

        for history in self:
            field = self._get_field()
            dates_from = mapped_data[field].get(history[field].id, []) # all `starting_date` of siblings history
            next_starting_date = [date for date in dates_from if date and date > history.starting_date]
            history.date_to = date_utils.subtract(min(next_starting_date), days=1) if next_starting_date else False
    
    def _get_field(self, vals=None):
        is_dict = bool(vals)
        if not is_dict:
            vals = self
        
        for field in ['employee_id', 'department_id', 'workcenter_id']:
            if vals[field] and (is_dict and vals[field][0] or vals[field].id):
                return field
    
    #===== Button =====#
    def button_open_details(self):
        """ On history costs tree view from Accounting app, to open Department or Employee form """

        field = self._get_field()
        model = {
            'workcenter_id': 'mrp.workcenter',
            'department_id': 'hr.department',
            'employee_id': 'hr.employee',
        }.get(field)
        return {
            'type': 'ir.actions.act_window',
            'res_model': model,
            'res_id': self[field].id,
            'view_mode': 'form',
            'name': self[field].name,
            'context': {'display_analytic': True}
        }
    