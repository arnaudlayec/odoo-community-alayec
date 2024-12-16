# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command

class PurchaseOrder(models.Model):
    _inherit = ['purchase.order']

    def _prepare_invoice(self):
        return super()._prepare_invoice() | {
            'invoice_user_id': self.user_id.id
        }
