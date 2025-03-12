# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = ['account.move']

    @api.depends('move_type')
    def _compute_invoice_default_sale_person(self):
        """ Since `invoice_user_id` is used for validation process, it must not be
            empty else it will trigger a User Error from `account_move_tier_validation`.
            This happens for `account.move` created other than from SO or PO (e.g. HR expense)
        """
        super()._compute_invoice_default_sale_person()

        for move in self:
            if not move.invoice_user_id:
                move.invoice_user_id = self.env.user

    def _post(self, soft=True):
        move = super()._post(soft)
        move.message_unsubscribe([move.partner_id.id])
        return move
