# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountAnalyticAccount(models.Model):
    _inherit = ['account.analytic.account']

    timesheet_cost_history_ids = fields.One2many(
        comodel_name="hr.employee.timesheet.cost.history",
        inverse_name="analytic_account_id",
    )

    #===== Valuation logics of a qty, using `timesheet_cost_history_ids` =====#
    def _value_workforce(self, qty, budget_id):
        """ :arg qty: quantity to multiply by unit value logic
            :arg budget_id: for date_from and date_to
        """
        self.ensure_one()

        # cost history table ensuring unique entry per starting_date
        analytic_cost_history = {}
        for x in self.timesheet_cost_history_ids:
            analytic_cost_history[x.starting_date] = (
                x.starting_date,
                x.date_to,
                x.hourly_cost,
            )

        return self._calculate_total_valuation(
            qty,
            [budget_id.date_from, budget_id.date_to],
            analytic_cost_history.values()
        )
    
    def _calculate_total_valuation(self, qty, date_range, costs_per_dates):
        """
            Calculates the total valuation for a `qty` as per valuation planning
            in `costs_per_dates`, during the period `date_range`.

            :param qty: Total budget to value, in hour.
            :param date_range: Tuple (start_date, end_date) of the budget period.
            :param costs_per_dates: List of tuples (start_date, end_date, unitary_value).
            :return: Total valuation in euros.
        """
        budget_start, budget_end = date_range
        if budget_start == budget_end or not budget_start or not budget_end or not qty or not costs_per_dates:
            return 0

        total_days = (budget_end - budget_start).days + 1
        total_valuation = 0.0

        for period_start, period_end, unitary_value in costs_per_dates:
            # Determine the overlap between the budget period and the valuation period
            if not period_start:
                # Ignore the valuation period if not date start
                continue
            overlap_start = max(budget_start, period_start)
            # Last valuation period (i.e. `date_to` to False) values all the remaining budget
            overlap_end = min(budget_end, period_end) if period_end else budget_end
            
            if overlap_start < overlap_end: # There is overlap
                overlap_days = (overlap_end - overlap_start).days + 1
                weight_of_period = overlap_days / total_days
                total_valuation += weight_of_period * qty * unitary_value

        return total_valuation
