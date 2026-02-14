# -*- coding: utf-8 -*-

from odoo import models, api

class ImportApiCall(models.Model):
    _inherit = ['import.api.call']

    @api.model
    def _get_reset_record_ids(self, lines):
        """ We need proper reset logic:
            1. Order: Payments -> Invoice -> Contacts
            2. Cancel invoices
            3. Ignore contacts that cannot be deleted
        """
        mapped_ids = super()._get_reset_record_ids(lines)
        
        invoice_ids = list(mapped_ids.get("account.move", []))
        invoices = self.env["account.move"].browse(invoice_ids).exists()

        # payments: add invoices', cancel & delete
        payment_ids = mapped_ids.get("account.payment", set())
        payment_ids |= set(invoices.matched_payment_ids.ids)
        payments = self.env["account.payment"].browse(payment_ids).exists()
        payments.filtered(lambda x: x.state in ["paid", "in_process"]).action_draft()
        payments.unlink()

        # invoices: cancel & delete
        invoices.filtered(lambda x: x.state == "posted").button_draft()
        invoices.unlink()
        invoices.invalidate_model([])

        # partners: ignore those having *other* invoices
        self.env["account.payment.register"].search([]).sudo().unlink()
        partner_ids = list(mapped_ids.get("res.partner", []))
        partners = self.env["res.partner"].search([
            ("id", "in", partner_ids),
            ("invoice_ids", "=", False),
        ])
        partners.unlink()

        return {
            k: v for k, v in mapped_ids.items()
            if k not in ["account.move", "account.payment", "res.partner"]
        }
