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

    @api.constrains('workcenter_id', 'employee_id')
    def _constrain_workcenter_employee(self):
        """ Ensure either workcenter or employee is set """
        orphans = self.filtered(lambda x: not x.workcenter.id and not x.employee_id.id)
        if len(orphans):
            raise exceptions.ValidationError(_(
                'Either Employee or Work Center is required on cost history.'
            ))

    def update_employee_cost(self):
        """ Overwrites to route between:
            * employee cost update (original), or
            * workcenter cost update (new)
        """
        if self.employee_id:
            return super().update_employee_cost()
        elif self.workcenter:
            return self.update_workcenter_cost()
    
    def update_workcenter_cost(self):
        self.ensure_one()
        
        # Log the cost in workcenter's history and eliminate/replace any next logs by this one
        domain_bad = [("starting_date", ">=", self.starting_date)]
        bad_costs = self.workcenter.cost_history_ids.filtered_domain(domain_bad)
        costs = self.workcenter.cost_history_ids - bad_costs
        self.workcenter.sudo().write({
            "costs_hour": self.hourly_cost,
            "cost_history_ids": [
                fields.Command.set(costs.ids),
                fields.Command.create({
                    "workcenter": self.workcenter.id,
                    "currency_id": self.currency_id.id,
                    "hourly_cost": self.hourly_cost,
                    "starting_date": self.starting_date,
                }),
            ],
        })
        
        # Recompute timesheets for all workcenter's
        domain = [
            ("workcenter_id", "in", self.workcenter_id.ids),
            ("date", ">=", self.starting_date),
        ]
        productivity_ids = self.env["mrp.workcenter.productivity"].search(domain)
        productivity_ids.costs_hour = self.hourly_cost

        update des timesheets
        quid mrp_workorder._create_or_update_analytic_entry
