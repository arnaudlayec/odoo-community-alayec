# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import re

class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ['purchase.order', 'project.default.mixin']

    #===== Fields =====#
    project_id = fields.Many2one(
        # not reqiured because of replenishment (stock.warehouse.orderpoint)
        required=False
    )
    project_discount_id = fields.Many2one(
        comodel_name='purchase.project.discount',
        compute='_compute_project_discount'
    )

    #===== Compute, Onchange =====#
    @api.depends('project_id', 'partner_id')
    def _compute_project_discount(self):
        for order in self:
            order.project_discount_id = order.project_id.purchase_discount_ids.filtered(
                lambda x: x.partner_id._origin == order.partner_id.commercial_partner_id._origin
            )

    @api.onchange("project_id")
    def onchange_partner_id(self):
        """ Set default discount per vendor *AND PROJECT* """
        po_project_discount = self.filtered(lambda x: x.project_discount_id)
        for order in po_project_discount:
            order.general_discount = order.project_discount_id.discount

        po_super = self - po_project_discount
        return super(PurchaseOrder, po_super).onchange_partner_id()
    
    #===== Logics =====#
    def button_confirm(self):
        self._set_notes_discount()
        return super().button_confirm()
    
    def _set_notes_discount(self):
        """ Update Terms & Conditions with project's discount """
        discount = self.project_discount_id
        if not discount:
            return

        line = '\n' if self.notes else ''
        percent = '{}%' . format(discount.discount) if discount.discount else ''
        contract = _('contract n.o. %s', discount.contract_ref) if discount.contract_ref else ''
        comma = ', ' if percent and contract else ''
        self.notes = (
            (self.notes or '') + line +
            _("General discount: ") + percent + comma + contract
        )

