# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions

class ProductTemplate(models.Model):
    _inherit = ["product.template"]

    budget_ok = fields.Boolean(
        string='Can be used in Budget',
        default=False
    )
    budget_lines_ids = fields.One2many(
        comodel_name='account.move.budget.line',
        inverse_name='product_tmpl_id'
    )

    #===== Constrains =====#
    @api.constrains('uom_id', 'type')
    def _constrain_uom_type_budget(self):
        """ Cannot change `uom` and `type` if they are budgets """
        if self.budget_lines_ids.ids:
            raise exceptions.ValidationError(_(
                'Cannot change Unit of Measure neither Product Type as there are'
                ' already account move budgets on this product.'
            ))
    
    #===== Logics (variant creation from template) =====#
    def _prepare_variant_values(self, combination):
        """ Pre-fill variant `date_from` with the one on attribute's value """
        return super()._prepare_variant_values(combination) | {
            'date_from': combination.product_attribute_value_id.date_from
        }
    
    #===== Valuation logics of a qty, using variant's default_price =====#
    def _value_qty(self, qty, budget_id):
        """
            :option qty: Quantity to multiply by valuation logic
            :option budget_id: record of `account.move.budget`, for total date range
        """
        self.ensure_one()
        self = self.with_context(active_test=False).sudo()

        if len(self.product_variant_ids.ids) == 1: # only 1 variant: fix price
            return qty * self.standard_price
        else:
            return self._calculate_total_valuation(
                qty,
                [budget_id.date_from, budget_id.date_to],
                [(x.date_from, x.date_to, x.standard_price) for x in self.product_variant_ids]
            )
    
    def _calculate_total_valuation(self, budget_qty, budget_period, valuation_list):
        """
        Calculate the total valuation for a0 `budget_qty` as per valuation planning
        in `valuation_list`, during the period `buget_period`.

        :param budget_qty: Total budget to value.
        :param budget_period: Tuple (start_date, end_date) of the budget period.
        :param valuation_list: List of tuples (start_date, end_date, unitary_value).
        :return: Total valuation in euros.
        """
        budget_start, budget_end = budget_period
        if budget_start == budget_end or not budget_start or not budget_end or not budget_qty or not valuation_list:
            return 0

        total_days = (budget_end - budget_start).days + 1
        total_valuation = 0.0

        for period_start, period_end, unitary_value in valuation_list:
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
                total_valuation += weight_of_period * budget_qty * unitary_value

        return total_valuation
