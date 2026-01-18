# -*- coding: utf-8 -*-

from odoo import models, exceptions, _
from markupsafe import Markup

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'import.api.mixin']

    def _get_import_config_default(self):
        return super()._get_import_config_default() | {
            # INVOICES
            'invoices_confirm': True,
                # If False: invoice are imported as draft only
                # If True:  try to validate invoices right after import
            'invoices_origin': _("API call"),
            
            # Optional keys for `import_config` (of `account_invoice_import`)
            # ID will be transformed into Odoo records
            # "company": 1,
            # "single_line": True,
            # "label": "Label",
            # "journal": 1,
            # "product": 1,
            # "taxes": [1, 2],
            # "account": 1,
            
            # CONTACTS
            'contact_create_on_the_fly': True,
                # If False: the invoice will be created in draft and a warning will be raised in
                # the import. It will embed contact data so that a user can manually create the
                # contact from the invoice
            'contact_update_on_the_fly': False,
                # If True: if the contact data are matched with an existing one, they will be
                # erased with transmitted data
            'contact_update_do_not_erase': True,
                # if True and if `contact_update_on_the_fly` is True, the contact will be updated
                # *ONLY IF* they were not modified manually in Odoo (based on `write_uid`, i.e. last
                # user who modified the contact)
            
            # PRODUCTS **(ROADMAP)**
            # 'product_create': False,
                # Currently no other mode than `False` is supported **(ROADMAP)**
        }

    def _run_import_api(self, data, config, logger):
        """ Largely inspired from `account.invoice.import.import_invoices()` """
        Import = self.env['account.invoice.import']
        Payment = self.env['account.payment']
        company = self.env.company
        import_config = self._get_import_config(config)
        
        for parsed_inv in data:
            # Some initialization
            if not "chatter_msg" in parsed_inv:
                parsed_inv["chatter_msg"] = []

            # Get, create or update partner
            partner = self._match_or_import_partner(Import, parsed_inv, config, logger)
            if partner:
                # Prevent glitch with existing invoices
                existing_inv = Import._invoice_already_exists(
                    parsed_inv, partner.commercial_partner_id, company.id
                )
                if existing_inv:
                    logger._add_line(
                        _("Invoice not imported because it already exists (ID %d number %s)",
                            existing_inv.id, existing_inv.name
                        ),
                        parsed_inv, field='invoice_number', flush=True,
                    )
                    continue

                import_config = partner._convert_to_import_config(company)
            
            payments_data = parsed_inv.pop("payments", {})
            
            # Create invoice
            invoice = Import.create_invoice(
                parsed_inv,
                import_config,
                origin=parsed_inv.get("origin", config.get("invoices_origin")),
            )
            invoice.external_id = parsed_inv.get("external_id")

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
            
            logger._flush_lines(parsed_inv, invoice)

            # if payments_data:
            #     invoice._import_payments_data(payments_data, config, logger)

    def _get_import_config(self, config):
        """ Return default `import_config` based on `config`
            This is required if the partner is not found/created.
            It transform ID into Odoo records
        """
        keys_to_record = {
            "company": "res.company",
            "journal": "account.journal",
            "product": "product.product",
            "taxes": "account.tax",
            "account": "account.account",
        }
        import_config = config
        for key, model in keys_to_record.items():
            if key in import_config:
                import_config[key] = self.env[model].browse(import_config[key])
        return import_config

    def _match_or_import_partner(self, Import, parsed_inv, config, logger):
        """ 1. Try and find existing
            2. If not found: create
            3. If found:     update
        """
        if not "partner" in parsed_inv:
            return False
        # 1. match for existing
        partner = self.env["business.document.import"]._match_partner(
            parsed_inv["partner"],
            parsed_inv["chatter_msg"],
            raise_exception=False,
        )
        # 2. create
        vals = {}
        Import._prepare_create_invoice_no_partner(parsed_inv, import_config={}, vals=vals)
        partner_data = vals.get("import_partner_data", {})
        if not partner and partner_data and config.get("contact_create_on_the_fly"):
            try:
                partner = self.env['res.partner'].create(partner_data)
            except exceptions.ValidationError as e:
                logger._add_line(
                    _("Cannot create partner. Embedding its data to the invoice, "
                      "waiting for its creation by an end-user. Details:\n %s", e),
                    parsed_inv, field="partner",
                )
        # 3. update
        elif partner and config.get("contact_update_on_the_fly"):
            is_erasing = bool(partner.write_uid != self.env.uid)
            if not is_erasing or not bool(config.get("contact_update_do_not_erase")):
                vals_update = {field: value for field, value in partner_data.items() if partner[field] != value}
                if vals_update:
                    partner.update(vals_update)
                    partner.message_post(body=Markup(_(
                        "Partner updated when importing external invoice %s by API.",
                        parsed_inv.get("external_id", ""),
                    )))
        if partner:
            # To speed-up next match
            parsed_inv["partner"] = {"recordset": partner}
        return partner

    def _import_payments_data(self, payments_data, config, logger):
        """ Import payments of a just imported invoice """
        for parsed_pay in payments_data:
            parsed_pay = self._payments_apply_defaults(parsed_pay)
        self.env["account.payment"]._run_import_api(payments_data, config, logger)
    
    def _payments_apply_defaults(self, parsed_pay):
        """ Apply default data for payments based on imported invoice """
        parsed_pay["invoice"] = {"recordset": self}
        if not "partner" in parsed_pay:
            parsed_pay["partner"] = {"recordset": self.partner_id}
        if not "currency" in parsed_pay:
            parsed_pay["currency"] = {"code": self.currency_id.code}
        if not "payment_type" in parsed_pay:
            move_type = self.move_type.split("_")[0]
            if move_type in ["out", "in"]:
                parsed_pay["payment_type"] = "inbound" if move_type == "out" else "outbound"
        if not "date" in parsed_pay:
            parsed_pay["date"] = self.date
        if not "memo" in parsed_pay:
            parsed_pay["memo"] = self.env['account.payment.register']\
                ._get_communication(self.line_ids)
        return parsed_pay
