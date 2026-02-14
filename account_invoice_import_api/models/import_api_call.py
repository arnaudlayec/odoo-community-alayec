# -*- coding: utf-8 -*-

from odoo import models, api

class ImportApiCall(models.Model):
    _inherit = ['import.api.call']

    @api.model
    def _get_reset_record_ids(self, lines):
        lines = lines.sorted("model") # account.move, account.payment, res.partner
        self.env["account.payment.register"].search([]).sudo().unlink() # delete wizards

        mapped_ids = super()._get_reset_record_ids(lines)
        
        # cancel invoices, add *all* payments to be deleted
        invoice_ids = list(mapped_ids.get("account.move", []))
        invoices = self.env["account.move"].browse(invoice_ids).exists()
        invoices.filtered(lambda x: x.state == "posted").button_draft()
        payment_ids = mapped_ids.setdefault("account.payment", set())
        payment_ids |= set(invoices.matched_payment_ids.ids)
        
        return mapped_ids
