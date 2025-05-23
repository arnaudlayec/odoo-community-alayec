# -*- coding: utf-8 -*-

from odoo import models, fields
import base64

class ProjectTask(models.Model):
    _inherit = ["project.task"]

    all_attachment_ids = fields.One2many(
        # (!) `attachment_ids` is native (non-message)
        comodel_name='ir.attachment',
        inverse_name='res_id',
        string='Attachments',
        domain=lambda self: [('res_model', '=', self._name)],
    )

    def copy(self, default={}):
        """ Manage manually the copy `all_attachment_ids` because 3 fields of `ir.attachment`
            are not copied and must be re-compute after create()
        """
        record = super().copy(default)
        for origin in self.all_attachment_ids:
            attachment = origin.copy()
            attachment._set_attachment_data(lambda _: origin.raw)
            record.all_attachment_ids |= attachment
        return record
