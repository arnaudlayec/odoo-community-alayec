# -*- coding: utf-8 -*-

from odoo import models, api

class ImportApiCall(models.Model):
    _inherit = ['import.api.call']

    @api.model
    def _get_reset_record_ids(self, lines):
        self.env["account.payment.register"].search([]).sudo().unlink() # delete wizards
        return super()._get_reset_record_ids(lines)
