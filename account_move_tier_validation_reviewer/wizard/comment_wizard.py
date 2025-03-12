# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CommentWizard(models.TransientModel):
    _inherit = ['comment.wizard']

    def add_comment(self):
        """ Send notification in the chatter on validation """
        res = super().add_comment()

        record = self.env[self.res_model].browse(self.res_id)
        mail_values = self._get_chatter_validation_message(record)
        record.message_post(**mail_values)

        return res
    
    def _get_chatter_validation_message(self, record):
        status = dict(record._fields['validation_status'].selection).get(record.validation_status)
        return {
            'message_type': 'notification',
            'subtype_xmlid': 'mail.mt_comment',
            'is_internal': True,
            'partner_ids': [],
            'body': _("Validation status: %s (%s)", status, self.comment),
        }
