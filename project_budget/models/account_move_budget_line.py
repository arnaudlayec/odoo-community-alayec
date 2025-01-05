# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

SELECTION_TYPE = [
    # `amount` is default feature of origin `account_move_budget` OCA module
    ('amount', 'Amount'),
    ('unit', 'Unit price'),
]

class AccountMoveBudgetLine(models.Model):
    _name = "account.move.budget.line"
    _inherit = ["account.move.budget.line", "account.move.budget.update.mixin"]
    _order = "seq_analytic, date desc, id desc"
    
    #===== Fields methods =====#
    def _default_analytic_account_id_domain(self):
        """ Limit selection of analytic account:
            1. to accountants only, depending user' permission
            2. to project-budget analytic account, depending on context
        """
        domain = []
        if self._context.get('default_project_id'):
            domain += [('is_project_budget', '=', True)]
        if not self.env.user.has_group('account.group_account_user'):
            domain += [('budget_only_accountant', '=', False)]

        return self.env['account.analytic.account'].search(domain)

    #===== Fields =====#
    analytic_account_id = fields.Many2one(
        domain="[('id', 'in', analytic_account_id_domain)]"
    )
    analytic_account_id_domain = fields.One2many(
        comodel_name='account.analytic.account',
        default=_default_analytic_account_id_domain,
        store=False
    )
    budget_id = fields.Many2one(
        domain="['|', ('project_id', '=', project_id), ('project_id', '=', False)]"
    )
    project_id = fields.Many2one(
        related='budget_id.project_id',
        store=True
    )
    seq_analytic = fields.Integer(
        related='analytic_account_id.sequence',
        store=True
    )
    type = fields.Selection(
        selection=SELECTION_TYPE,
        string='Type',
        required=True,
        precompute=True,
        compute='_compute_type', # follows' analytic budget_type
        store=True,
        readonly=False,
        help='- "Amount": Debit and Credit are filled in\n'
             '- "Unit": Qty Debit, Qty Credit and Unit Price are filled in, and\n'
             ' Debit and Credit are calculated accordingly'
    )
    budget_type = fields.Selection(
        # from analytic. Store for pivot view
        related='analytic_account_id.budget_type',
        store=True
    )
    # values
    standard_price = fields.Monetary(
        # only displayed/used if `unit`
        string='Unit price',
        currency_field='company_currency_id'
    )

    # debit & credit: h->€
    debit = fields.Monetary(
        compute='_compute_debit_credit',
        store=True,
        readonly=False
    )
    credit = fields.Monetary(
        compute='_compute_debit_credit',
        store=True,
        readonly=False
    )
    qty_debit = fields.Float(
        string='Debit (qty)',
        default=0.0
    )
    qty_credit = fields.Float(
        string='Credit (qty)',
        default=0.0
    )
    qty_balance = fields.Float(
        string='Balance (qty)',
        compute="_compute_debit_credit",
        readonly=True,
        store=True,
    )

    _sql_constraints = [(
        'unique_aac_per_project',
        'UNIQUE (analytic_account_id, project_id)',
        "A budget line is already set on this project to the same analytic account."
    )]


    #===== CRUD =====#
    def _trigger_depends(self, method, fields=[]):
        # [example] project_project.budget_line_sum
        # if 'balance' in fields or method in ['create', 'unlink']:
        #     recordset.project_id._compute_budget_line_sum()
        return super()._trigger_depends(method, fields)
    

    #===== Compute =====#
    @api.depends('analytic_account_id', 'analytic_account_id.budget_type')
    def _compute_type(self):
        """ Type (Create, Default, Onchange):
            default line type from analytic_account_id
        """
        for line in self:
            line.type = line.analytic_account_id._get_default_line_type() or 'amount'

    #===== Compute: valuation =====#
    @api.depends('standard_price', 'qty_debit', 'qty_credit')
    def _compute_debit_credit(self):
        for line in self:
            line._compute_debit_credit_one()
            line.qty_balance = line.qty_debit - line.qty_credit
            line.balance = line.debit - line.credit
    
    def _compute_debit_credit_one(self):
        self.ensure_one()
        if self.type == 'unit':
            self.debit = self.qty_debit * self.standard_price
            self.credit = self.qty_credit * self.standard_price


    #===== Button ======#
    def button_open_budget_line_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Budget line details'),
            'view_mode': 'form',
            'res_model': 'account.move.budget.line',
            'res_id': self.id,
            'context': {'default_type': 'unit'},
            'target': 'new'
        }
