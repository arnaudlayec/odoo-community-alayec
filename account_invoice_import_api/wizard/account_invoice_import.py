# -*- coding: utf-8 -*-

from odoo import api, models, exceptions, _
from odoo.tools.misc import format_amount

class AccountInvoiceImport(models.TransientModel):
    """ This inheritance was designed so it could be natively
        added into `account_invoice_import`
    """
    _inherit = ["account.invoice.import"]

    @api.model
    def _invoice_already_exists(self, parsed_inv, commercial_partner, company_id):
        """ Also verify existing invoice by 'name' """
        existing_inv = super()._invoice_already_exists(parsed_inv, commercial_partner, company_id)
        name = parsed_inv.get("name")
        if not existing_inv and name:
            existing_inv = self.env["account.move"].search(
                [("name", "=", name), ("state", "=", "posted")]
            )
        return existing_inv

    @api.model
    def _prepare_create_invoice_vals(self, parsed_inv, import_config):
        """ Add support of additionnal keys in `parsed_inv`:
            - name
            - external_ref
            - address_delivery
            - address_invoice, that may be set in `partner_id` instead of 'partner' key
        """
        vals = {}

        #== Before `super()` ==#
        # Addresses preprocess. Should be moved to `_pre_process_parsed_inv()` but we need `import_config`
        bdio = self.env["business.document.import"]
        for address_type in ["delivery", "invoice"]:
            self._pre_process_addresses(parsed_inv, address_type, import_config)
        
        # Set partner's fiscal position
        # This must be before invoice creation, so before super(),
        # so that line parsing is done with correct taxes,
        # but after all adress creations, for having both partner+delivery addresses
        partner = bdio._match_partner(
            parsed_inv.get("partner", {}),
            parsed_inv["chatter_msg"],
            raise_exception=False,
        )
        if partner and not partner.property_account_position_id:
            partner = partner.commercial_partner_id.with_company(import_config["company"])
            delivery_id = partner.address_get(["delivery"]).get("delivery")
            delivery = self.env["res.partner"].browse(delivery_id)
            afp = self.env["account.fiscal.position"]
            partner.property_account_position_id = afp._get_fiscal_position(partner, delivery)
        
        # invoice's `partner_shipping_id`
        if "address_delivery" in parsed_inv:
            delivery = bdio._match_shipping_partner(
                parsed_inv["address_delivery"], partner, parsed_inv["chatter_msg"]
            )
            if delivery:
                vals["partner_shipping_id"] = delivery.id
        
        vals |= super()._prepare_create_invoice_vals(parsed_inv, import_config)
        
        #== After `super()` ==#
        # 'name' & 'external_ref'
        external_ref = parsed_inv.get("external_ref")
        vals["external_ref"] = external_ref
        if "name" in parsed_inv:
            vals["name"] = parsed_inv["name"]
        
        # Force on the invoice a different invoice address than partner_id's default
        if "address_invoice" in parsed_inv:
            address_invoice = bdio._match_partner_address(
                parsed_inv["address_invoice"],
                partner,
                "invoice",
                parsed_inv["chatter_msg"],
                raise_exception=False,
            )
            if address_invoice:
                vals["partner_id"] = address_invoice.id
        
        return vals
    
    @api.model
    def _pre_process_addresses(self, parsed_inv, address_type, import_config):
        """ Add support for `address_delivery` and `address_invoice` keys
            in `parsed_inv`.
            
            (!) We do not handle the use-case where partner is not found/created
                and its data are saved in `import_parner_data`. In such case,
                (delivery|invoice) address data are lost.
        """
        assert address_type in ["delivery", "invoice"]
        parsed_key = "address_" + address_type
        address_dict = parsed_inv.get(parsed_key, {})
        address_dict.setdefault("chatter_msg", [])
        address_dict["logger"] = import_config.get("logger")
        bdio = self.env["business.document.import"]
        partner = bdio._match_partner(
            parsed_inv.get("partner", {}),
            parsed_inv["chatter_msg"],
            raise_exception=False,
        )
        if not address_dict or not partner:
            return
        
        matched_address = bdio._match_partner_address(
            address_dict,
            partner,
            address_type,
            address_dict["chatter_msg"],
            raise_exception=False,
        )
        created = False
        if not matched_address: # not found (and so, != partner) => create a new one
            address_dict.setdefault("chatter_msg", [])
            address_dict.update({
                "type": address_type,
                "parent_id": partner.id,
            })
            matched_address = bdio._create_or_update_partner(
                None, address_dict, import_config
            )
            created = True
        if created or matched_address.id != partner.address_get([address_type]).get(address_type):
            parsed_inv[parsed_key] = {"recordset": matched_address}
        # else, this is OK to let Odoo choose default addresses on invoice

    @api.model
    def _post_process_invoice(self, parsed_inv, import_config, invoice):
        invoice_confirm = import_config.get('invoice_confirm')
        logger = import_config.get("logger")

        res = super()._post_process_invoice(parsed_inv, import_config, invoice)
        if parsed_inv.get("type", "").startswith("out"):
            # On customer invoice, there must be exact match of amounts between
            #    Odoo and the source system. For instance, wrong fiscal position guessing
            #    or writing by the external system might lead to wrong taxes on invoice line.
            # This must be advertised and invoice won't be confirmed even with config
            #    "invoice_confirm", the same for vendor bill but without trying to force
            #    taxe total or create adjustment line.
            if parsed_inv["currency_rec"].compare_amounts(
                invoice.amount_total, parsed_inv["amount_total"]
            ):
                msg = _(
                    "The total amount of the imported invoice is "
                    " %(real_amount_total)s whereas the total amount computed "
                    "by Odoo is %(current_amount_total)s. It is the "
                    "consequence of a difference between the total tax amount of "
                    "the invoice (%(real_amount_tax)s) and the total tax amount "
                    "computed by Odoo (%(current_amount_tax)s). "
                    "This is often caused by wrong or missing taxes in invoice lines "
                    "due to a failure to find the tax in Odoo that correspond to the tax "
                    "of the imported invoice. The source of the error can be a wrongly "
                    "guessed fiscal position, a missing configuration of taxes on products, "
                    " or missing configuration of Default Taxes on the partner "
                    "(if there are no products on invoice lines).",
                    real_amount_total=format_amount(
                        self.env, parsed_inv["amount_total"], invoice.currency_id
                    ),
                    current_amount_total=format_amount(
                        self.env, invoice.amount_total, invoice.currency_id
                    ),
                    real_amount_tax=format_amount(
                        self.env,
                        parsed_inv["amount_total"] - parsed_inv["amount_untaxed"],
                        invoice.currency_id,
                    ),
                    current_amount_tax=format_amount(
                        self.env, invoice.amount_tax, invoice.currency_id
                    ),
                )
                if invoice_confirm:
                    msg = _("The invoice has been left unposted.\n") + msg
                    invoice_confirm = False # don't post
                logger._add_line_warning(msg, parsed_inv, invoice, field="amount_total")

        # Posting the invoice
        if invoice_confirm:
            if not invoice.partner_id:
                logger._add_line_warning(
                    _("Cannot confirm the invoice because of empty contact"),
                    parsed_inv, field="partner",
                )
            else:
                try:
                    invoice.action_post()
                except exceptions.ValidationError as e:
                    logger._add_line_warning(
                        _("Cannot confirm the invoices. Details:\n %s", e),
                        parsed_inv, flush=True,
                    )
        
        # Import invoice's payments
        payments_data = parsed_inv.get("payments")
        if payments_data:
            invoice._import_payments_data(payments_data, import_config)
        
        return res
