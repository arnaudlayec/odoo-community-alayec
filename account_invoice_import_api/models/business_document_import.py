# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.osv import expression

class BusinessDocumentImport(models.AbstractModel):
    _inherit = ["business.document.import"]

    #==============================================
    #================== MATCHING ==================
    #==============================================
    @api.model
    def _match_invoice(
        self, invoice_dict, chatter_msg, partner=None, company=None,
        raise_exception=True
    ):
        if not invoice_dict:
            invoice_dict = {}
        amo = self.env["account.move"]
        invoice = self._direct_match(invoice_dict, amo)
        if invoice:
            return invoice

        if invoice_dict.get("move_type"):
            domain_base = [
                ("move_type", "=", invoice_dict["move_type"])
            ]
        else:
            domain_base = [
                (
                    "move_type",
                    "in",
                    ["out_invoice", "out_refund", "in_invoice", "in_refund"]
                )
            ]
        
        domain_ref = domain_partner = domain_company = []
        if invoice_dict.get("ref"):
            domain_ref = [
                '|',
                ("name", "=", invoice_dict["ref"]),
                ("invoice_number", "=", invoice_dict["ref"]),
            ]
        if partner:
            domain_partner = [
                ("commercial_partner_id", "=", partner.id)
            ]
        if company:
            domain_company = [
                ("company_id", "=", company.id)
            ]
        
        domains = [
            domain_ref + domain_partner + domain_company,
            domain_ref + domain_company,
            domain_ref,
            domain_partner + domain_company,
            domain_partner,
        ]
        for domain in domains:
            if domain:
                invoice = amo.search(domain_base + domain, limit=1)
                if invoice:
                    return invoice

        self.user_error_wrap(
            "_match_invoice",
            invoice_dict,
            _(
                "Odoo couldn't find any invoice corresponding to the "
                "following information:\n"
                "Type: %(type)s\n"
                "Reference: %(reference)s\n"
                "Partner: %(partner)s\n"
                "Company: %(company)s\n",
                type=invoice_dict.get("type") or "",
                reference=invoice_dict.get("reference") or "",
                partner=invoice_dict.get("partner") or "",
                company=invoice_dict.get("company") or "",
            ),
            chatter_msg,
            raise_exception,
        )
        
        return None

    @api.model
    def _match_payment_method_line(
        self, payment_method_dict, chatter_msg, type=None, journal=None,
        company=None, raise_exception=True
    ):
        if not payment_method_dict:
            payment_method_dict = {}
        pml = self.env["account.payment.method.line"]
        payment_method_lines = self._direct_match(payment_method_dict, pml)
        if payment_method_lines:
            return payment_method_lines

        # Code domains
        domain = []
        if payment_method_dict.get("code"):
            domain = expression.OR(
                [
                    domain,
                    [("code", "=", payment_method_dict["code"])]
                ]
            )
        if payment_method_dict.get("unece_code"):
            domain = expression.OR(
                [
                    domain,
                    [("unece_code", "=", payment_method_dict["unece_code"])]
                ]
            )
        
        # Search within a journal
        if journal:
            if type: # 'inbound' or 'outbound'
                payment_method_lines = journal[type + "_payment_method_line_ids"]
            else:
                payment_method_lines = (
                    journal.inbound_payment_method_line_ids |
                    journal.outbound_payment_method_line_ids
                )
        # Search by accounting configs
        else:
            if company:
                domain = [
                    ("company_id", "=", company.id)
                ]
            payment_method_lines = pml.search(domain)
        
        # 'type' arg mandatory if type is ambiguous
        if len(set(payment_method_lines.mapped("payment_type"))) > 1 and not type:
            assert type
        
        if type:
            payment_method_lines = payment_method_lines.filtered(
                lambda x: x.payment_type == type
            )

        if payment_method_lines:
            return payment_method_lines[0]
        
        self.user_error_wrap(
            "_match_payment_method_line",
            payment_method_dict,
            _(
                "Odoo couldn't find any payment method line corresponding to the "
                "following information:\n"
                "Payment type: %(payment_type)s\n"
                "Code: %(journal)s\n"
                "UNECE code: %(journal)s\n"
                "Journal: %(journal)s\n"
                "Company: %(company)s\n",
                payment_type=type or "",
                code=payment_method_dict.get("code") or "",
                unece_code=payment_method_dict.get("unece_code") or "",
                journal=journal.display_name if journal else "",
                company=company.display_name if company else "",
            ),
            chatter_msg,
            raise_exception,
        )

        return None
    