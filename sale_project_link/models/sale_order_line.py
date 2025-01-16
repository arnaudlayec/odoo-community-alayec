# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command
from collections import defaultdict

class SaleOrderLine(models.Model):
    _inherit = ['sale.order.line']
    
    project_id = fields.Many2one(
        related='order_id.project_id',
    )
    analytic_ids = fields.Many2many(
        comodel_name='account.analytic.account',
        compute='_compute_analytic_ids',
        string='Analytic Accounts'
    )

    #====== Constrain ======#
    @api.constrains('analytic_distribution')
    def _constrain_analytic_to_project(self):
        """ Prevent setting different project analytic than PO's project """
        project_plan = self.env.company.analytic_plan_id
        for line in self:
            to_verify = line.analytic_ids.filtered(lambda x: x.plan_id == project_plan)
            allowed = line.order_id.project_id.analytic_account_id

            if to_verify and allowed and to_verify != allowed:
                raise exceptions.ValidationError(_(
                    "The only allowed project in Analytic Distribution is the"
                    " sale order's one."
                ))

    #====== Compute ======#
    @api.depends('analytic_distribution')
    def _compute_analytic_ids(self):
        """ Gather analytic account selected in the line's analytic distribution """
        for line in self:
            new_distrib = line.analytic_distribution
            line.analytic_ids = new_distrib and [Command.set([int(x) for x in new_distrib.keys()])]

    @api.depends('order_id.project_id')
    def _compute_analytic_distribution(self):
        """ Apply to line's analytic the sale order's project analytic """
        res = super()._compute_analytic_distribution()
        self.order_id._onchange_project_id()
        return res
    
    #===== Business logics =====#
    def _replace_analytic(self, replaced_ids, added_id):
        """ Called from Sale Order
            :arg replaced_ids: `analytic_ids` to be replaced (to delete) in line analytic distribution
            :arg added_id:     single replacement `analytic_id` in place of `replaced_ids`
        """
        vals_added = {added_id: 100} if added_id else {}

        for line in self:
            if not line.display_type:
                kept = {} if not line.analytic_distribution else {
                    k: v for k, v in line.analytic_distribution.items()
                    if int(k) not in replaced_ids
                }
                line.analytic_distribution = kept | vals_added
