#  @author: Alexis de Lattre <alexis.delattre@akretion.com>

from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = ['purchase.order']

    access_group_id = fields.Many2one(
        comodel_name='purchase.access.group',
        string="Purchase group",
        default=lambda self: self.env.user.context_purchase_access_group_id,
        ondelete='restrict',
        check_company=True
    )

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        vals['access_group_id'] = self.access_group_id.id or False
        return vals


class PurchaseReport(models.Model):
    _inherit = ['purchase.report']

    access_group_id = fields.Many2one(
        comodel_name='purchase.access.group',
        string="Purchase group",
        readonly=True
    )

    def _select(self):
        select_str = super()._select()
        select_str += ", po.access_group_id"
        return select_str

    def _group_by(self):
        group_by_str = super()._group_by()
        group_by_str += ", po.access_group_id"
        return group_by_str
