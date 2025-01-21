# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from collections import defaultdict
from datetime import datetime

class MrpWorkcenterProductivity(models.Model):
    """ Calculate the cost of each productivity record and store it """

    _inherit = ["mrp.workcenter.productivity"]

    #===== Fields =====#
    currency_id = fields.Many2one(
        related='company_id.currency_id'
    )
    cost = fields.Monetary(
        string='Cost',
        compute='_compute_cost',
    )

    @api.depends('date_start', 'date_end') # also triggered by `cost_history` wizard (new `workcenter.costs_hour` history)
    def _compute_cost(self):
        # build valuation table
        workcenter_costs = defaultdict(dict)
        for x in self.workcenter_id.cost_history_ids:
            workcenter_costs[x.workcenter_id.id][x.starting_date] = x.hourly_cost

        for productivity in self:
            productivity.cost = productivity._calculate_cost(workcenter_costs)

    def _calculate_cost(self, workcenter_costs):
        """ Calculate the cost for the productivity period (`date_start` to `date_end`)
            based on the hourly cost history.

            :arg `workcenter_costs` (dict): valuation table
            :return (float): total cost for the given productivity record/period
        """
        self.ensure_one()

        if not self.date_start or not self.date_end:
            return 0.0  # No duration to calculate cost for

        # Get cost history for the current workcenter
        cost_history = workcenter_costs.get(self.workcenter_id.id, {})
        sorted_costs = sorted(cost_history.items(), key=lambda x: x[0]) # sort by starting_date

        # Initialize variables
        total_cost = 0.0
        prod_start = self.date_start
        remaining_hours = (self.date_end - self.date_start).total_seconds() / 3600  # in hours (use to break the loop)
        for n, (date_cost, hourly_cost) in enumerate(sorted_costs):
            # Cost period
            next_cost = n+1 < len(sorted_costs) and sorted_costs[n+1]
            cost_start = datetime.combine(date_cost, datetime.min.time())
            cost_end = next_cost and datetime.combine(next_cost[0], datetime.min.time())
            
            # Overlap between cost & productivity
            start = max(cost_start, prod_start)
            end = min(cost_end, self.date_end) if cost_end else self.date_end
            overlap = end - start

            # Value any productivity *before* the 1st cost, with this 1st cost
            if prod_start < cost_start:
                overlap += cost_start - prod_start
            
            overlap_hours = overlap.total_seconds() / 3600
            
            # No overlap
            if overlap_hours <= 0:
                continue

            # Add cost for this period
            total_cost += overlap_hours * hourly_cost
            remaining_hours -= overlap_hours

            # Update prod_start to the end of this period
            prod_start = end

            # Break if there is no more duration left to calculate
            if remaining_hours <= 0:
                break

        # Return the total cost calculated
        return total_cost
