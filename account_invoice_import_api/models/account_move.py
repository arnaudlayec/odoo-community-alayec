# -*- coding: utf-8 -*-

from odoo import models, api, fields, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'import.api.mixin']

    @api.model
    def _get_api_config_default(self):
        """ Specifications in demo data """
        return super()._get_api_config_default() | {
            # INVOICES
            'invoice_confirm': True,
            # CONTACTS
            'contact_create_on_the_fly': True,
            'contact_update_on_the_fly': True,
            'contact_update_do_not_erase': True,
            # PAYMENTS
            "payment_confirm": True,
            "payment_bank_create": None,
            # PRODUCTS
            # 'product_create': False, # ROADMAP
        }

    @api.model
    def _run_import_api(self, data, config):
        """ Largely inspired from `account.invoice.import.import_invoices()` """
        aii = self.env['account.invoice.import']
        bdio = self.env["business.document.import"]
        invoices = self.env["account.move"]
        logger = config["logger"]

        for parsed_inv in data:
            # Some initialization
            if not parsed_inv:
                continue
            if not isinstance(parsed_inv, dict):
                raise exceptions.UserError(
                    _("Wrong data format, %s", parsed_inv)
                )
            parsed_inv.setdefault("chatter_msg", [])
            parsed_inv["logger"] = logger

            # Get+update or create partner
            partner_dict = parsed_inv.get("partner", {})
            partner_dict.setdefault("chatter_msg", [])
            partner = self.env["business.document.import"]._match_partner(
                partner_dict,
                partner_dict["chatter_msg"],
                raise_exception=False,
            )
            partner = bdio._create_or_update_partner(partner, partner_dict, config)
            existing_inv = None
            if partner:
                # Speed-up next match
                parsed_inv["partner"] = {"recordset": partner}
                config |= partner._convert_to_import_config(self.env.company)
                # Prevent glitch with existing invoices
                existing_inv = aii._invoice_already_exists(
                    parsed_inv, partner.commercial_partner_id, self.env.company.id
                )
            if existing_inv:
                logger._add_line_warning(
                    _("Invoice not imported because it already exists (ID %d number %s)",
                        existing_inv.id, existing_inv.name
                    ),
                    parsed_inv, field='invoice_number', flush=True,
                )
                continue

            # Create invoice
            invoices |= aii.create_invoice(
                parsed_inv,
                config,
                origin=parsed_inv.get("origin", config.get("origin")),
            )

        invoices._postprocess_import_api()

    def _import_payments_data(self, payments_data, config):
        """ Import payments of a just imported invoice
            (called at invoice post-process)
        """
        Payment = self.env["account.payment"]
        for pay_dict in payments_data:
            pay_dict["invoice"] = {"recordset": self}
            payments = Payment.create_payment(
                pay_dict, config, pay_dict.get("origin", self.invoice_origin)
            )

            if payments:
                self.preferred_payment_method_line_id = fields.first(payments).payment_method_line_id

    def _postprocess_import_api(self):
        journals = self.preferred_payment_method_line_id.journal_id
        journals._auto_reconcile()
