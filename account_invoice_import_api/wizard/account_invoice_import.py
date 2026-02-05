# -*- coding: utf-8 -*-

from odoo import api, models, Command, _

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
        """ Add management of additionnal `parsed_inv` data keys
            to invoice `vals`
        """
        vals = super()._prepare_create_invoice_vals(parsed_inv, import_config)
        
        # 'name' & 'external_ref'
        external_ref = parsed_inv.get("external_ref")
        vals["external_ref"] = external_ref
        if "name" in parsed_inv:
            vals["name"] = parsed_inv["name"]

        # addresses (invoice & delivery)
        for address_type in ["invoice", "delivery"]:
            self._substitute_invoice_addresses(parsed_inv, vals, address_type, import_config)
        
        return vals
    
    def _substitute_invoice_addresses(self, parsed_inv, vals, address_type, import_config):
        """ Add support for `address_delivery` and `address_invoice` keys
            in `parsed_inv`.
            
            (!) We do not handle the use-case where partner is not found/created
                and its data are saved in `import_parner_data`. In such case,
                (delivery|invoice) address data are lost.
        """
        address_field = (
            "partner_shipping_id" if address_type == "delivery" else
            "partner_id" if address_type == "invoice" else None
        )
        address_dict = parsed_inv.get("address_" + address_type)
        bdio = self.env["business.document.import"]
        partner = self.env["res.partner"].browse(vals.get("partner_id"))
        if not address_dict or not partner:
            return

        matched_address = bdio._match_partner_address(
            address_dict, partner, address_type, parsed_inv["chatter_msg"],
            raise_exception=False,
        )
        if not matched_address: # not found (and so, != partner)
            address_dict.update({
                "type": address_type,
                "parent_id": partner.id,
            })
            new_address = bdio._create_or_update_partner(
                matched_address, parsed_inv, import_config, "address_" + address_type
            )
            if new_address:
                vals[address_field] = new_address.id
        elif matched_address.id != partner.address_get([address_type]).get(address_type):
            vals[address_field] = matched_address.id
        # else, this is OK to let Odoo choose default addresses on invoice
