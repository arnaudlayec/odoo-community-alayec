# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CommentWizard(models.TransientModel):
    _inherit = ['comment.wizard']

    def add_comment(self):
        """ Send notification on chatter on validation """
        res = super().add_comment()
        mail_values = self._get_chatter_validation_message()
        self.message_post(**mail_values)

        return res
    
    def _get_chatter_validation_message(self):
        status = dict(self._fields['validation_status'].selection).get(self.validation_status)
        return {
            'message_type': 'notification',
            'subtype_xmlid': 'mail.mt_note',
            'is_internal': True,
            'partner_ids': [],
            'body': _("Validation status: %s (%s)", status, self.comment),
        }
