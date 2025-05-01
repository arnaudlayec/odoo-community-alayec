# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import date

class HrEmployee(models.Model):
    _inherit = ['hr.employee']

    hourly_cost = fields.Monetary(compute='_compute_hourly_cost', store=True)

    @api.depends('department_id')
    def _compute_hourly_cost(self):
        """ Align employee's hourly cost to department's when changing its department """
        self._align_hourly_cost_to_department()

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
        mapped_timesheet_ids = {
            x.employee_id.id: x 
            for x in self.env["account.analytic.line"].sudo().search(domain)
        }
        for employee in self:
            timesheet_ids = mapped_timesheet_ids.get(employee.id)
            if timesheet_ids:
                timesheet_ids._timesheet_postprocess({"employee_id": employee.id})
