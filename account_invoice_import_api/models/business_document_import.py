# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.osv import expression

class BusinessDocumentImport(models.AbstractModel):
    _inherit = ["business.document.import"]

    @api.model
    def _match_partner_email(self, partner_dict, chatter_msg, domain, order):
        """ Neutralize matching partner by email address,
            we cannot afford it in B2C use-case
        """
        return
    
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
    
    #===============
    #=== PARTNER ===
    #===============
    @api.model
    def _get_partner_address_dict(self, partner):
        """ Convert `res.partner` record to a parsed-data dict like:
            {
                "street": "546 route de l'Épinette",
                "street2": "",
                "street3": "", # if `partner_address_street3` is installed
                "city": "POMMERÉVAL (76680)",
                "zip": "76680",
                "country_code": "FR",
                "state_code": "",
                "is_company": True, # if `_get_parsed_address_fields` is inherited
            }
        """
        # flipped magic_fields: partner's record -> partner_dict
        magic_fields = {
            # switch field/key
            field: (key, related_field, dependent_field)
            for key, (field, related_field, dependent_field)
            in self._get_magic_fields().items()
        }
        partner_dict = {}
        for field in self._get_partner_address_fields():
            if field in magic_fields:
                key, related_field, _ = magic_fields[field]
                partner_dict[key] = partner[field][related_field]
            else:
                partner_dict[field] = partner[field]
        return partner_dict
    
    @api.model
    def _prepare_partner_vals(self, partner_dict, chatter_msg={}, raise_exception=True):
        """ Convert partner's parsed data to vals for ORM methods.
            Generic: compatible with all partner kind (company, individual,
            address). Example:
            :arg partner_dict: {"country_code": "FR", "state_code": "49"}
            :return: vals={"country_id": 33, "state_id": 412}
        """
        vals = {}
        partner_dict = dict(partner_dict)
        magic_fields = self._get_magic_fields()
        rpo = self.env["res.partner"]
        
        for key, value in partner_dict.items():
            if isinstance(value, str):
                value = value.strip()
            
            # if 'key' is actually a rpo's field name
            # either not m2o (str, boolean, selection,...), or is m2o and int is given
            # this helps passing ID in the key like `country_id`
            if key in rpo._fields and (
                not isinstance(rpo[key], models.BaseModel) or isinstance(value, int)
            ):
                vals[key] = value
                continue

        # e.g. 'country_code' -> 'country_id'
        for key in magic_fields:
            value = partner_dict.get(key)
            if not value:
                continue
            rpo_field, related_field, dependant_fields = magic_fields[key]
            model = rpo[rpo_field]._name
            domain = [(related_field, "=", value)]
            for x in dependant_fields or {}:
                domain = expression.OR([domain, [(x, "=", vals[x])]])
            record = self.env[model].search(domain)
            if record:
                vals[rpo_field] = record.id
            
        return vals

    @api.model
    def _get_magic_fields(self):
        """ M2o fields searched through their related model's fields.
            Format:
            {
                "Key in parsed data dict":
                (
                    "Record field" (e.g. in `res.partner`)",
                    "Field in related model (e.g. in `res.country`)",
                    "Dependant field in origin model (e.g. in `res.partner`)",
                )
            }
        """
        return {
            "country_code": ("country_id", "code", None),
            "state_code": ("state_id", "code", ["country_id"]),
            "title_name": ("title", "name", None),
        }

    @api.model
    def _create_or_update_partner(self, partner, parsed_data, config, partner_key="partner"):
        bdio = self.env["business.document.import"]
        logger = config["logger"]
        partner_key = partner_key # for addresses
        partner_dict = parsed_data.get(partner_key, {})
        partner_vals = bdio._prepare_partner_vals(partner_dict, parsed_data["chatter_msg"])

        if not partner and config.get("contact_create_on_the_fly"):
            if not partner_vals.get("name") and partner_vals.get("email"):
                partner_vals["name"] = partner_vals["email"]
            # create
            if partner_vals.get("name"):
                partner = self.env['res.partner'].create(partner_vals)
                logger._add_line_success(partner_dict, partner, parsed_data["chatter_msg"])
            else:
                logger._add_line(
                    _("Missing partner's name or email to create it on the fly."),
                    parsed_data, field=partner_key,
                )

        # update
        elif partner and config.get("contact_update_on_the_fly"):
            is_erasing = bool(partner.write_uid.id != self.env.uid)
            if not is_erasing or not bool(config.get("contact_update_do_not_erase")):
                # verify first if there's actually need to update
                vals_update = {}
                for field, value in partner_vals.items():
                    db_value = partner[field].id if hasattr(partner[field], "id") else partner[field]
                    if value != db_value:
                        vals_update[field] = value
                if vals_update:
                    partner.update(vals_update)
                    partner.message_post(body=Markup(_(
                        "Partner info updated when importing external invoice %s by API.",
                        parsed_data.get("external_ref", ""),
                    )))

        return partner
