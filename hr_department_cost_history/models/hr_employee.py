# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import date

class HrEmployee(models.Model):
    _inherit = ['hr.employee']

    def write(self, vals):
        """ Align employee's hourly cost to department's when changing its department """
        res = super().write(vals)
        if 'department_id' in vals:
            self._align_hourly_cost_to_department()
        return res
    
    def _align_hourly_cost_to_department(self, starting_date=None):
        """ [Inspired from OCA `hr_employee_cost_history/wizard/hr_employee_timesheet_cost_wizard.py`]
            Recalculates employee timesheet cost from a given date
            **without** writting in employee's history table
        """
        if not starting_date:
            starting_date = date.today()
        
        # Set the costs on all employees (with *NO* writting in employee's history table)
        self.hourly_cost = self.department_id.hourly_cost

        # Remove bad costs on employees
        domain_bad = [("starting_date", ">=", starting_date)]
        bad_costs = self.timesheet_cost_history_ids.filtered_domain(domain_bad)
        bad_costs.unlink()
        
        # Recompute timesheets
        domain = [
            ("employee_id", "in", self.ids),
            ("date", ">=", starting_date),
        ]
        rg_result = self.env['account.analytic.line']._read_group(
            domain, ['ids:array_agg(id)'], ['employee_id']
        )
        mapped_timesheets = {x['employee_id']: x['ids'] for x in rg_result}
        for employee in self:
            timesheet_ids = mapped_timesheets.get(employee.id)
            if timesheet_ids:
                timesheet_ids._timesheet_postprocess({"employee_id": employee.id})
