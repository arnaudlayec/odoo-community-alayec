# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMoveBudgetLine(models.Model):
    _name = "account.move.budget.line"
    _inherit = ["account.move.budget.line"]
    _order = "seq_analytic, date desc, id desc"

    #===== Fields =====#
    budget_id = fields.Many2one(
        domain="[('project_id', '=', project_id)]"
    )
    project_id = fields.Many2one(
        related='budget_id.project_id',
        store=True
    )
    seq_analytic = fields.Integer(
        related='analytic_account_id.sequence',
        store=True
    )
    partner_id = fields.Many2one(
        # default line's partner to project's
        related='project_id.partner_id', store=True, readonly=False, # follows project's partner
    )
    type = fields.Selection(
        # `standard` is default feature of origin `account_move_budget` OCA module
        selection=[
            ('standard', 'Direct valuation'),
            ('fix', 'Unit-price valuation'),
            ('date_range', 'Date-range valuation'),
        ],
        default='standard',
        required=True
    )
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        related='analytic_account_id.product_tmpl_id', store=True, readonly=False, # follows analytic account's product
        ondelete='restrict',
        domain="""[
            ('budget_ok', '=', True),
            '|', ('company_id', '=', False), ('company_id', '=', company_id)
        ]"""
    )
    name = fields.Char(
        related='product_tmpl_id.name', store=True, readonly=False, # follows product's name
    )
    # values
    standard_price = fields.Monetary(
        # only displayed/used if `fix`
        string='Line Value',
        currency_field='company_currency_id',
        help='Fix line value'
    )
    product_variant_ids = fields.One2many(
        # displayed/used if `fix` or `date_range`
        # if `date_range`: variants are used for valuation (if none: 0€)
        related='product_tmpl_id.product_variant_ids'
    )
    uom_id = fields.Many2one(
        related='product_tmpl_id.uom_id',
    )

    # debit & credit: h->€
    debit = fields.Monetary(
        compute='_compute_debit_credit',
        compute_sudo=True,
        store=True,
        readonly=False
    )
    credit = fields.Monetary(
        compute='_compute_debit_credit',
        compute_sudo=True,
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

    #===== Compute: prefilling =====#
    @api.onchange('product_tmpl_id')
    def _onchange_product_default_account_id(self):
        """ `account_id` is suggested as per product's accounting settings (expense account) """
        for line in self:
            line.account_id = line.product_tmpl_id._get_product_accounts().get('expense')

    #===== Compute: valuation =====#
    @api.depends(
        'qty_debit', 'qty_credit',
        'budget_id', 'budget_id.date_from', 'budget_id.date_to',
        'product_tmpl_id', 'product_tmpl_id.standard_price',
        'product_variant_ids', 'product_variant_ids.standard_price',  'product_variant_ids.date_from',
    )
    def _compute_debit_credit(self):
        for line in self:
            line.qty_balance = line.qty_debit - line.qty_credit

            if line.type == 'fix':
                line.debit = line.qty_debit * line.standard_price
                line.credit = line.qty_credit * line.standard_price
            elif line.type == 'date_range':
                line.debit = line._value_qty(line.qty_debit)
                line.credit = line._value_qty(line.qty_credit)
            
            line.balance = line.debit - line.credit
    
    def _value_qty(self, qty):
        self.ensure_one()
        return self.product_tmpl_id.id and self.product_tmpl_id._value_qty(qty, self.budget_id)

    #===== Button ======#
    def button_open_budget_line_form(self):
        return self.project_id.button_open_budget_lines() | {
            'name': 'Budget Line details',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }
