#  @author: Alexis de Lattre <alexis.delattre@akretion.com>

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = ['account.move']

    access_group_id = fields.Many2one(
        comodel_name='purchase.access.group',
        string="Purchase group",
        default=lambda self: self.env.user.context_purchase_access_group_id,
        ondelete='restrict'
    )


class AccountInvoiceReport(models.Model):
    _inherit = ["account.invoice.report"]

    access_group_id = fields.Many2one(
        comodel_name='purchase.access.group',
        string="Purchase group",
        readonly=True,
    )

    def _select(self):
        select_str = super()._select()
        select_str += ", move.access_group_id"
        return select_str
