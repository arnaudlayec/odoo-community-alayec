# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HrEmployeeTimesheetCost(models.TransientModel):
    _inherit = ["hr.employee.timesheet.cost.wizard"]

    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        ondelete="cascade",
    )
    employee_id = fields.Many2one(
        # either department or employee is required
        required=False
    )

    def update_employee_cost(self):
        """ Overwrites to route between:
            * department cost update (new)
            * or default to original
        """
        if self.department_id.id:
            return self._update_department_cost()
        
        return super().update_employee_cost()
    
    def _update_department_cost(self):
        self.ensure_one()
        
        # Log the cost in department's history and eliminate/replace any next logs by this one
        domain_bad = [("starting_date", ">=", self.starting_date)]
        bad_costs = self.department_id.timesheet_cost_history_ids.filtered_domain(domain_bad)
        costs = self.department_id.timesheet_cost_history_ids - bad_costs
        self.department_id.sudo().write({
            "hourly_cost": self.hourly_cost,
            "timesheet_cost_history_ids": [
                fields.Command.set(costs.ids),
                fields.Command.create({
                    "department_id": self.department_id.id,
                    "currency_id": self.currency_id.id,
                    "hourly_cost": self.hourly_cost,
                    "starting_date": self.starting_date,
                }),
            ],
        })
        
        # Set the costs on all employees (with *NO* writting in employee's history table)
        self.department_id.member_ids._align_hourly_cost_to_department(
            starting_date=self.starting_date
        )
