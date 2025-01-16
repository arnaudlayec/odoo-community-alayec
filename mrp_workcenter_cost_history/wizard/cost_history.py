# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HrEmployeeTimesheetCost(models.TransientModel):
    _inherit = ["hr.employee.timesheet.cost.wizard"]

    workcenter_id = fields.Many2one(
        comodel_name="mrp.workcenter",
        string="Work Center",
        ondelete="cascade",
    )
    employee_id = fields.Many2one(
        # either workcenter or employee is required
        required=False
    )

    def update_employee_cost(self):
        """ Overwrites to route between:
            * department cost update (new)
            * or default to original
        """
        if self.workcenter_id:
            return self.update_workcenter_cost()
        
        return super().update_employee_cost()
    
    def update_workcenter_cost(self):
        self.ensure_one()
        
        # Log the cost in workcenter's history and eliminate/replace any next logs by this one
        domain_bad = [("starting_date", ">=", self.starting_date)]
        bad_costs = self.workcenter_id.cost_history_ids.filtered_domain(domain_bad)
        costs = self.workcenter_id.cost_history_ids - bad_costs
        self.workcenter_id.sudo().write({
            "costs_hour": self.hourly_cost, # (!) workcenter field is `costs_hour` but wizard's is `hourly_cost`
            "cost_history_ids": [
                fields.Command.set(costs.ids),
                fields.Command.create({
                    "workcenter_id": self.workcenter_id.id,
                    "currency_id": self.currency_id.id,
                    "hourly_cost": self.hourly_cost,
                    "starting_date": self.starting_date,
                }),
            ],
        })
        
        # Recompute workorder analytic entry total
        self.workcenter_id.workorder_ids._create_or_update_analytic_entry()
