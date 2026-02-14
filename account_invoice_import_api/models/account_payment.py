# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions, _
from markupsafe import Markup

import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'import.api.mixin']
    
    def _get_api_config_default(self):
        return self.env["account.move"]._get_api_config_default()
    
    def _run_import_api(self, data, config):
        payments = self.env["account.payment"]
        logger = config["logger"]
        existing_external_refs = {
            x["external_ref"]: x["id"]
            for x in self.search_read([("external_ref", "!=", False)], ["external_ref"])
        }

        for pay_dict in data:
            if not pay_dict:
                continue
            
            # Existing payment
            external_ref = pay_dict.get("external_ref")
            if external_ref and external_ref in existing_external_refs:
                logger._add_line_warning(
                    _("Payment not imported because it already exists (ID %d, External Ref. %s)",
                        existing_external_refs[external_ref], external_ref
                    ),
                    pay_dict, field='external_ref', flush=True,
                )
                continue
            
            # Create payment
            payment = self.create_payment(
                pay_dict,
                config,
                config["origin"]
            )
            payments |= payment
            if external_ref:
                existing_external_refs[external_ref] = fields.first(payment).id

        if self._context.get("import_api_model") != "account.move":
            payments._postprocess_import_api()

    def create_payment(self, pay_dict, config, origin):
        pay_dict = self._pre_process_import_pay_dict(pay_dict, config)
        wizard_vals = self._prepare_payment_register_vals(pay_dict, config)
        if not wizard_vals:
            return
        invoice = pay_dict["invoice"]["recordset"]
        payments = self._import_invoice_payment(invoice, wizard_vals, pay_dict, config)
        if payments:
            payments._post_process_import_payment(pay_dict, config, origin)
        return payments

    def _import_invoice_payment(self, invoice, wizard_vals, pay_dict, config):
        """ Payment creation logic, sticking Odoo UI process
            using the wizard `account.payment.register`
        """
        _logger.debug("Payments vals for payment register wizard: %s", wizard_vals)
        Wizard = self.env["account.payment.register"].with_context({
            "active_model": "account.move",
            "active_ids": invoice.id,
        })
        wizard = Wizard.create(wizard_vals)

        # memo
        if not "memo" in pay_dict and not wizard.communication:
            wizard._compute_communication()

        payments = wizard._create_payments()
        _logger.info("Payment IDs %s created", payments.ids)
        return payments

    def _pre_process_import_pay_dict(self, pay_dict, config):
        """ Defaults and guessings, like a `default_get` """
        if pay_dict.get("pre-processed"):
            return pay_dict
        pay_dict["logger"] = config.get("logger")
        
        pay_dict["pre-processed"] = True
        if "chatter_msg" not in pay_dict:
            pay_dict["chatter_msg"] = []
        
        if not "payment_type" in pay_dict:
            pay_dict["payment_type"] = "inbound"
            pay_dict["chatter_msg"].append(
                _("Unknown payment type, setting Inbound as default.")
            )
        if not "partner_type" in pay_dict:
            pay_dict["partner_type"] = "customer" if pay_dict["payment_type"] == "inbound" else "supplier"
        
        if not "amount" in pay_dict:
            pay_dict["amount"] = 0.0
            pay_dict["chatter_msg"].append(
                _("Unknown amount, setting 0.0 as default.")
            )
        
        # Partner
        partner_dict = pay_dict.get("partner")
        if partner_dict:
            partner_dict.setdefault("chatter_msg", [])
            bdio = self.env["business.document.import"]
            partner = bdio._match_partner(
                partner_dict,
                partner_dict["chatter_msg"],
                raise_exception=False,
            )
            if not partner:
                partner = bdio._create_or_update_partner(partner, partner_dict, config)
                pay_dict["partner"] = {"recordset": partner} # Speed-up next match

        return pay_dict

    def _prepare_payment_register_vals(self, pay_dict, config):
        """ Logic of parsing `pay_dict` to `vals`
            Example of 'pay_dict': view demo data
        """
        logger = config["logger"]
        bdio = self.env["business.document.import"]

        # Partner
        partner = None
        if pay_dict.get("partner"):
            partner = self.env["business.document.import"]._match_partner(
                pay_dict["partner"],
                pay_dict["chatter_msg"],
                raise_exception=False,
            )
        
        # Invoice
        invoice = None
        if pay_dict.get("invoice"):
            invoice = bdio._match_invoice(
                pay_dict.get("invoice"),
                pay_dict["chatter_msg"],
                partner=partner,
                company=config["company"],
                raise_exception=False,
            )
            pay_dict["invoice"] = {"recordset": invoice}
        if not invoice:
            logger._add_line_warning(
                _("Invoice not found: cannot import payments."),
                pay_dict, field="invoice", flush=True,
            )
            return {}
        if not partner:
            partner = invoice.partner_id
        
        # Journal (required)
        if pay_dict.get("journal"):
            journal = bdio._match_journal(
                pay_dict["journal"],
                pay_dict["chatter_msg"],
                company=config["company"],
                raise_exception=False,
            )
        else:
            journal = config.get("journal")
        field_pay = pay_dict["payment_type"] + "_payment_method_line_ids"
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
                    ).get(pay_dict["payment_type"])
                )
            )

        # Currency (required)
        if not pay_dict.get("currency"):
            pay_dict["currency"] = {
                "recordset": invoice.currency_id or journal.currency_id
            }
        currency = bdio._match_currency(
            pay_dict["currency"],
            pay_dict["chatter_msg"],
            config["company"],
            raise_exception=False,
        )
        
        # Payment method line
        if pay_dict.get("payment_method"):
            payment_method_line = bdio._match_payment_method_line(
                pay_dict["payment_method"],
                pay_dict["chatter_msg"],
                type=pay_dict["payment_type"],
                journal=journal,
                company=config["company"],
                raise_exception=False,
            )
        else:
            payment_method_line = fields.first(journal[field_pay])
        
        # Bank account
        partner_bank = None
        if pay_dict.get("iban"):
            bank_create = config.get("payment_bank_create")
            partner_bank = bdio._match_partner_bank(
                partner,
                pay_dict["iban"],
                pay_dict.get("bic"),
                pay_dict["chatter_msg"],
                create_if_not_found=(
                    bank_create if bank_create != None else
                    config["company"].invoice_import_create_bank_account
                ),
            )

        return {
            "company_id": config["company"].id,
            "payment_type": pay_dict["payment_type"],
            "partner_type": pay_dict["partner_type"],
            "amount": pay_dict["amount"],
            "payment_date": pay_dict.get("date"),
            "communication": pay_dict.get("memo"),

            "currency_id": currency and currency.id,
            "journal_id": journal and journal.id,
            "partner_id": partner and partner.id,
            "payment_method_line_id": payment_method_line and payment_method_line.id,
            "partner_bank_id": partner_bank and partner_bank.id,
        }

    def _post_process_import_payment(self, pay_dict, config, origin):
        """ Possible hook """
        self.external_ref = pay_dict.get("external_ref")
        
        invoice = pay_dict["invoice"]["recordset"]
        if config.get("payment_confirm") and invoice.state == "posted":
            self.action_validate()

        bdio = self.env["business.document.import"]
        for payment in self:
            bdio.post_create_or_update(pay_dict, payment)
            payment.message_post(
                body=Markup(
                    _(
                        "This payment has been created automatically."
                        "Origin: <strong>%s</strong>.",
                        origin or _("unspecified"),
                    )
                )
            )

    def _postprocess_import_api(self):
        """ Bank statement lines might have been imported *before* the
            invoice. In such case, we want to re-play auto-reconcile models
        """
        self.journal_id._auto_reconcile()
