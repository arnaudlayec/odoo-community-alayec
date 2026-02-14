# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.osv import expression
from markupsafe import Markup

class BusinessDocumentImport(models.AbstractModel):
    _inherit = ["business.document.import"]

    #==============================================
    #================== INHERITE ==================
    #==============================================
    @api.model
    def _match_partner_email(self, partner_dict, chatter_msg, domain, order):
        """ Neutralize matching partner by email address,
            we cannot afford it in B2C use-case
        """
        return

    @api.model
    def post_create_or_update(self, parsed_dict, record, doc_filename=None):
        res = super().post_create_or_update(parsed_dict, record, doc_filename)
        logger = parsed_dict.get("logger")
        if logger:
            logger._flush_lines(parsed_dict, record)
        return res

    #=============================================
    #================== PARTNER ==================
    #=============================================
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
            address).

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
                domain = expression.AND([domain, [(x, "=", vals[x])]])
            record = self.env[model].search(domain)
            if record:
                vals[rpo_field] = fields.first(record).id

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
    def _create_or_update_partner(self, partner, partner_dict, config):
        bdio = self.env["business.document.import"]
        logger = config["logger"]
        partner_dict["logger"] = logger
        partner_vals = bdio._prepare_partner_vals(partner_dict, partner_dict["chatter_msg"])

        if not partner and config.get("contact_create_on_the_fly"):
            if not partner_vals.get("name") and partner_vals.get("email"):
                partner_vals["name"] = partner_vals["email"]
            # create
            if partner_vals.get("name"):
                partner = self.env['res.partner'].create(partner_vals)
                self._update_partner_fiscal_position(partner)
                logger._add_line_success(partner_dict, partner, capture_msg=True)
                bdio.post_create_or_update(partner_dict, partner)
            else:
                logger._add_line_warning(
                    _("Missing partner's name or email to create it on the fly."),
                    partner_dict
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
                    if "country_id" in vals_update:
                        self._update_partner_fiscal_position(partner)
                    partner.message_post(body=Markup(_(
                        "Partner info updated when importing external invoice %s by API.",
                        partner_dict.get("external_ref", ""),
                    )))

        return partner
    
    def _update_partner_fiscal_position(self, partner):
        fpos = self.env["account.fiscal.position"]._get_fiscal_position(partner)
        if partner.property_account_position_id != fpos:
            partner.property_account_position_id = fpos
