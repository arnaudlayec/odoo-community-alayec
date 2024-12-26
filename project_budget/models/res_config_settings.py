# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    # Analytic Plan
    analytic_budget_plan_id = fields.Many2one(
        comodel_name='account.analytic.plan',
        string="Analytic Plan for Project Budgets",
        readonly=False,
        related='company_id.analytic_budget_plan_id',
    )
