# -*- coding: utf-8 -*-

from odoo import models

class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'import.api.mixin']

    # def _get_import_config_default(self):
    #     return super()._get_import_config_default()
    
    # def _run_import_api(self, data, config, logger):
    #     """ Example:
    #     {
    #         "payment_type": "outbound" or "inbound",
    #         "partner_type": "customer" or "supplier",
    #             # customer: Receive money from invoice or send money to refund it
    #             # supplier: Send money to pay a bill or receive money to refund it
    #         "invoice": {},
    #         "amount": 10.00,
    #         "date": "2025-01-01",
    #         "memo": "Label",
    #         "state": "draft" or "in_process", "paid", "canceled", "rejected",
    #         "partner": {}, # same as `account.move`
    #         "currency": {}, # same as `account.move`
    #         "journal": {}, # same as `account.move`
    #         "payment_mode", # payment_method_line_id

    #         # roadmap
    #         "bank": # `partner_bank_id` (default to journal's `bank_account_id`)
    #             # par défaut : celui du journal pour les paiements sortants
    #             # sinon le 1er du partenaire, pour les paiements entrants
    #     }
    #     """
    #     for parsed_inv in data:
            

    # def _preprocess(self, parsed_pay):
    #     if not "partner_type" in parsed_pay:
    #         parsed_pay["partner_type"] = "customer" if in_out == "in" else "supplier"
