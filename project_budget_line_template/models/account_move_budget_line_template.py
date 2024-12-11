# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMoveBudgetLine(models.Model):
    _name = "account.move.budget.line.template"
    _description = "Account Move Budget Line Template"
    _order = "sequence"

    sequence = fields.Integer(
        # for priority between budget lines
        string='Priority'
    )
    name = fields.Char(
        string="Label"
    )
    account_id = fields.Many2one(
        comodel_name="account.account",
        string="Account",
        ondelete="cascade",
        domain=[("deprecated", "=", False)]
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        ondelete="cascade"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="account_id.company_id",
        string="Company",
        store=True,
        readonly=True,
        ondelete="cascade"
    )
