# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = ['account.move']

    review_ids = fields.One2many(tracking=True)

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

    # def validate_tier(self):
    #     """ Send notification on chatter on validation """
    #     res = super().validate_tier()
    #     mail_values = self._get_chatter_message(byproducts, unknown, consu, report_binary)
    #     self.production_id.message_post(**mail_values)

    #     return res
    
    # def _get_chatter_message(self, byproducts, unknown, consu, report_binary):
    #     return {
    #         'message_type': 'notification',
    #         'subtype_xmlid': 'mail.mt_note',
    #         'is_internal': True,
    #         'partner_ids': [],
    #         'body': _(
    #             "<ul>"
    #                 "<li><strong>%(byproducts)s</strong> final products</li>"
    #                 "<li><strong>%(components)s</strong> components added</li>"
    #                 "<li><strong>%(consu)s</strong> consumable (to order separatly)</li>"
    #                 "<li><strong>%(substituted)s</strong> substituted references</li>"
    #                 "<li><strong>%(ignored)s</strong> explicitely ignored</li>"
    #                 "<li><strong>%(unknown)s</strong> unknown products</li>"
    #             "</ul>",
    #             byproducts=len(byproducts),
    #             components=len(self.product_ids),
    #             consu=len(consu),
    #             substituted=len(self.substituted_product_ids),
    #             ignored=len(self.ignored_product_ids),
    #             unknown=len(unknown),
    #         ),
    #         'attachments': [] if not report_binary else [
    #             (_('Component & products report'), report_binary)
    #         ]
    #     }
