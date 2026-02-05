# -*- coding: utf-8 -*-

from odoo import models, fields, Command, exceptions, _
from markupsafe import Markup

import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'import.api.mixin']
    
    def _get_api_config_default(self):
        return super()._get_api_config_default() | {
            # PAYMENTS
            "payment_bank_create": True,
                # If different than None, it overrides company's
                # setting `invoice_import_create_bank_account`

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
        }
    
    def _run_import_api(self, data, config):
        logger = config["logger"]
        external_refs = self.search([("external_ref", "!=", False)]).mapped("external_ref")
        for parsed_pay in data:
            # Existing payment
            external_ref = parsed_pay.get("external_ref")
            if external_ref and external_ref in external_refs:
                logger._add_line(
                    _("Payment not imported because it already exists (ID %d, External Ref. %s)",
                        external_refs[external_ref], external_ref
                    ),
                    parsed_pay, field='external_ref', flush=True,
                )
                continue
            
            # Import
            self.import_payment(parsed_pay, config, config["origin"])
            if external_ref:
                external_refs.append(external_ref)
            
            logger._flush_lines(parsed_pay)

    def import_payment(self, parsed_pay, config, origin):
        parsed_pay = self._pre_process_import_parsed_pay(parsed_pay, config)
        vals = self._prepare_payment_register_vals(parsed_pay, config)
        if not vals:
            return

        _logger.debug("Payments vals for creation: %s", vals)
        wizard = self.env["account.payment.register"].create(vals)
        payment = wizard._create_payments()
        payment._post_process_import_payment(parsed_pay, config)
        _logger.info("Payment ID %d created", payment.id)

        self.env["business.document.import"].post_create_or_update(parsed_pay, payment)
        payment.message_post(
            body=Markup(
                _(
                    "This payment has been created automatically."
                    "Origin: <strong>%s</strong>.",
                    origin or _("unspecified"),
                )
            )
        )
        return payment
    
    def _pre_process_import_parsed_pay(self, parsed_pay, config):
        """ Defaults and guessings """
        if parsed_pay.get("pre-processed"):
            return parsed_pay
        
        parsed_pay["pre-processed"] = True
        if "chatter_msg" not in parsed_pay:
            parsed_pay["chatter_msg"] = []
        
        if not "payment_type" in parsed_pay:
            parsed_pay["payment_type"] = "inbound"
            parsed_pay["chatter_msg"].append(
                _("Unknown payment type, setting Inbound as default.")
            )
        if not "partner_type" in parsed_pay:
            parsed_pay["partner_type"] = "customer" if parsed_pay["payment_type"] == "inbound" else "supplier"
        
        if not "amount" in parsed_pay:
            parsed_pay["amount"] = 0.0
            parsed_pay["chatter_msg"].append(
                _("Unknown amount, setting 0.0 as default.")
            )
        
        # Partner
        bdio = self.env["business.document.import"]
        partner = bdio._match_partner(
            parsed_pay.get("partner", {}),
            parsed_pay["chatter_msg"],
            raise_exception=False,
        )
        partner = bdio._create_or_update_partner(partner, parsed_pay, config)
        # Speed-up next match
        if partner:
            parsed_pay["partner"] = {"recordset": partner}
            
        return parsed_pay

    def _prepare_payment_register_vals(self, parsed_pay, config):
        """ Example:
        {
            "external_ref": 111,
            "payment_type": "outbound" or "inbound",
            "partner_type": "customer" or "supplier",
                // Optional, guessed from `payment_type`
                // customer: Receive money from invoice or send money to refund it
                // supplier: Send money to pay a bill or receive money to refund it
            "payment_method": {
                // Only required if 'journal' has more than 1 payment method
                // for the 'payment_type'.
                // If so, 1 or both of 'code' and 'unece_code' can be provided
                "code": "manual", // 'fr_lcr', 'manual', 'sepa_credit_transfer'
                "unece_code": 24, // 30
            },
            "amount": 10.00,
            "date": "2025-01-01",
            "invoice": {
                "name": "INV/2026/00001",
                "invoice_number": "25F06061"
            },
            "partner": {}, // see example in `account.move`
            "journal": {}, // see example in `account.move`

            // Optionnal
            "currency": {}, // see example in `account.move`
            "memo": "Label", // Computed from the invoice if not given
            "iban": "FR7630001007941234567890185",
            "bic": "BDFEFR2LCCB",
        }
        """
        logger = config["logger"]
        apr = self.env["account.payment.register"]
        bdio = self.env["business.document.import"]
        vals = {
            "company_id": config["company"].id,
            "payment_type": parsed_pay["payment_type"],
            "partner_type": parsed_pay["partner_type"],
            "amount": parsed_pay["amount"],
            "payment_date": parsed_pay.get("date"),
        }

        # Partner
        partner = None
        if parsed_pay.get("partner"):
            partner = self.env["business.document.import"]._match_partner(
                parsed_pay["partner"],
                parsed_pay["chatter_msg"],
                raise_exception=False,
            )
        
        # Invoice
        invoice = None
        if parsed_pay.get("invoice"):
            invoice = bdio._match_invoice(
                parsed_pay.get("invoice"),
                parsed_pay["chatter_msg"],
                partner=partner,
                company=config["company"],
                raise_exception=False,
            )
        if not invoice or invoice.state != "posted":
            logger._add_line(
                _("Invoice was not found or is unposted, thus payments "
                    "were not imported."),
                parsed_pay, field="invoice", flush=True,
            )
            return
        
        # Journal (required)
        journal = config.get("journal")
        field_pay = vals["payment_type"] + "_payment_method_line_ids"
        if not journal:
            journal = bdio._match_journal(
                parsed_pay["journal"],
                parsed_pay["chatter_msg"],
                company=config["company"],
                raise_exception=False,
            )
        if not journal:
            journals = self.env["account.journal"].search(
                [
                    ("company_id", "=", config["company"].id),
                    ("type", "in", ["bank", "cash", "credit"]),
                ],
                limit=1,
            )
            # see `account_journal.available_journal_ids`
            journal = fields.first(journals.filtered(field_pay))
        if not journal:
            raise exceptions.UserError(
                _(
                    "No journal with %(payment_type)s payment method in %(company)s.",
                    company=config["company"].display_name,
                    payment_type=dict(
                        self._fields["payment_type"]._description_selection(self.env)
                    ).get(vals["payment_type"])
                )
            )

        # Currency (required)
        currency = bdio._match_currency(
            parsed_pay.get("currency"),
            parsed_pay["chatter_msg"],
            config["company"],
            raise_exception=False,
        )
        if journal.currency_id and (not currency or currency == config["company"]):
            currency = journal.currency_id
        
        # Payment method line
        if parsed_pay.get("payment_method"):
            payment_method_line = bdio._match_payment_method_line(
                parsed_pay["payment_method"],
                parsed_pay["chatter_msg"],
                type=parsed_pay["payment_type"],
                journal=journal,
                company=config["company"],
                raise_exception=False,
            )
        else:
            payment_method_line = fields.first(journal[field_pay])

        # Bank account
        partner_bank = None
        if parsed_pay.get("iban"):
            bank_create = config.get("payment_bank_create")
            partner_bank = bdio._match_partner_bank(
                partner,
                parsed_pay["iban"],
                parsed_pay.get("bic"),
                parsed_pay["chatter_msg"],
                create_if_not_found=(
                    bank_create if bank_create != None else
                    config["company"].invoice_import_create_bank_account
                ),
            )
        
        vals |= {
            "memo": parsed_pay.get(
                "memo", apr._get_communication(invoice.line_ids)
            ),
            "currency_id": currency and currency.id,
            "journal_id": journal and journal.id,
            "partner_id": partner and partner.id,
            "line_ids": [Command.set(invoice.line_ids.ids)],
            "payment_method_line_id": payment_method_line and payment_method_line.id,
            "partner_bank_id": partner_bank and partner_bank.id,
        }

        return vals

    def _post_process_import_payment(self, parsed_pay, config):
        """ Payment confirmation """
        return
        self.action_post()
        self.action_validate()
        self.move_id.matched_payment_ids += self
