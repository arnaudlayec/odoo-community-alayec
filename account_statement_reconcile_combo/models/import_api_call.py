# -*- coding: utf-8 -*-

from odoo import models, api

class ImportApiCall(models.Model):
    _inherit = ['import.api.call']

    @api.model
    def _get_reset_record_ids(self, lines):
        self.env["account.payment.register"].search([]).sudo().unlink() # delete wizards
        # exclude partners with other payments
        res = super()._get_reset_record_ids(lines)
        return res

        partner_ids = list(res.get("res.partner", []))
        if partner_ids:
            other_payments = self.env["account.payment"].search([
                ("id", "not in", list(res.get("account.payment", []))),
                ("partner_id", "in", partner_ids)
            ])
            other_invoices = self.env["account.move"].search([
                ("id", "not in", list(res.get("account.move", []))),
                '|', ("partner_id", "in", partner_ids), ("partner_shipping_id", "in", partner_ids)
            ])

            res["res.partner"] -= set(
                other_payments.mapped("partner_id") +
                other_invoices.mapped("partner_id") +
                other_invoices.mapped("partner_shipping_id")
            )

        return res
