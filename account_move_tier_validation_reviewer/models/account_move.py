# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

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

    def validate_tier(self):
        """ Send notification on chatter on validation """
        res = super().validate_tier()
        mail_values = self._get_chatter_validation_message()
        self.message_post(**mail_values)

        return res
    
    def _get_chatter_validation_message(self):
        return {
            'message_type': 'notification',
            'subtype_xmlid': 'mail.mt_note',
            'is_internal': True,
            'partner_ids': [],
            'body': _("Validation status: %s", self.validation_status),
        }
