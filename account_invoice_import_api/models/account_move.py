# -*- coding: utf-8 -*-

from odoo import models, exceptions, _
from markupsafe import Markup

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'import.api.mixin']

    def _get_api_config_default(self):
        return super()._get_api_config_default() | {
            # Optional keys for `import_config` (see `account_invoice_import`)
            # ID will be transformed into Odoo records
            # "company": 1,
            # "single_line": True,
            # "label": "Label",
            # "journal": 1,
            # "product": 1,
            # "taxes": [1, 2],
            # "account": 1,

            # INVOICES
            'invoices_confirm': True,
                # If False: invoice are imported as draft only
                # If True:  try to validate invoices right after import
            
            # CONTACTS
            'contact_create_on_the_fly': True,
                # If False: the invoice will be created in draft and a warning will be raised in
                # the import. It will embed contact data so that a user can manually create the
                # contact from the invoice
            'contact_update_on_the_fly': True,
                # If True: if the contact data are matched with an existing one, they will be
                # erased with transmitted data
            'contact_update_do_not_erase': True,
                # if True and if `contact_update_on_the_fly` is True, the contact will be updated
                # *ONLY IF* they were not modified manually in Odoo (based on `write_uid`, i.e. last
                # user who modified the contact)

            # PAYMENTS
            "payment_bank_create": True,
                # If different than None, it overrides company's
                # setting `invoice_import_create_bank_account`
            'payment_state': 'paid',
                # Target payment state
                # Within 'draft' (default), 'in_process', 'paid'
            
            # PRODUCTS
            # 'product_create': False, # ROADMAP
                # Currently no other mode than `False` is supported
        }

    def _run_import_api(self, data, config):
        """ Largely inspired from `account.invoice.import.import_invoices()` """
        aii = self.env['account.invoice.import']
        bdio = self.env["business.document.import"]
        logger = config["logger"]

        for parsed_inv in data:
            # Some initialization
            if not "chatter_msg" in parsed_inv:
                parsed_inv["chatter_msg"] = []

            # Get+update or create partner
            partner = self.env["business.document.import"]._match_partner(
                parsed_inv.get("partner", {}),
                parsed_inv["chatter_msg"],
                raise_exception=False,
            )
            partner = bdio._create_or_update_partner(partner, parsed_inv, config)
            existing_inv = None
            if partner:
                # Speed-up next match
                parsed_inv["partner"] = {"recordset": partner}
                # Prevent glitch with existing invoices
                existing_inv = aii._invoice_already_exists(
                    parsed_inv, partner.commercial_partner_id, self.env.company.id
                )
                config |= partner._convert_to_import_config(self.env.company)
            if existing_inv:
                logger._add_line(
                    _("Invoice not imported because it already exists (ID %d number %s)",
                        existing_inv.id, existing_inv.name
                    ),
                    parsed_inv, field='invoice_number', flush=True,
                )
                continue

            # Create invoice
            payments_data = parsed_inv.pop("payments", [])
            invoice = aii.create_invoice(
                parsed_inv,
                config,
                origin=parsed_inv.get("origin", config.get("origin")),
            )

            # Confirm
            if config.get('invoices_confirm'):
                if not invoice.partner_id:
                    logger._add_line(
                        _("Cannot confirm the invoice because of empty contact"),
                        parsed_inv, field="partner",
                    )
                else:
                    try:
                        invoice.action_post()
                    except exceptions.ValidationError as e:
                        logger._add_line(
                            _("Cannot confirm the invoices. Details:\n %s", e),
                            parsed_inv, flush=True,
                        )
            
            # Payments
            if payments_data:
                invoice._import_payments_data(payments_data, config)

            logger._flush_lines(parsed_inv)

    def _import_payments_data(self, payments_data, config):
        """ Import payments of a just imported invoice """
        for parsed_pay in payments_data:
            wizard = self.env["account.payment.register"]
            parsed_pay.update({
                "invoice": {"recordset": self},
                "memo": wizard._get_communication(self.line_ids),
            })
            if not parsed_pay.get("partner") and self.partner_id:
                parsed_pay["partner"] = {"recordset": self.partner_id}
        self.env["account.payment"]._run_import_api(payments_data, config)
