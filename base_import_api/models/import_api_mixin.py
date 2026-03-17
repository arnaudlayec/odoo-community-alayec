# -*- coding: utf-8 -*-

from odoo import modules, models, fields, api, tools, exceptions, _
from odoo.tools.misc import str2bool

from lxml import etree
import json
import re

import logging
_logger = logging.getLogger(__name__)

class ImportApiMixin(models.AbstractModel):
    _name = 'import.api.mixin'
    _description = "Import API mixin"
    _inherit = ['mail.thread']

    external_ref = fields.Char(
        string='External Ref.',
        help="Reference in the external tool, when synchronized. "
             "1 External Ref. should have only 1 Odoo ID, and reverse.",
        readonly=True,
    )

    #===== API Endpoint =====#
    @api.model
    def import_api(self, payload_arg, logger=None) -> dict:
        """ :arg `payload_arg`: JSON string, expected format:
            {
                'config': {}, # dict
                'data': ..., # any type, usually 'vals_list' format
            }
            :arg logger: for `action_replay`
        """
        self = self.with_context(import_api_model=self._name) # can be useful for for inheritance

        if isinstance(payload_arg, dict):
            payload = payload_arg
        elif isinstance(payload_arg, str):
            pattern = re.compile('//.+') # to remove JSON comments
            payload = json.loads(pattern.sub('', payload_arg))
        else:
            raise exceptions.ValidationError(_(
                "Payload must a be a JSON string or a Python dict, %s given.",
                type(payload_arg)
            ))

        logger = logger or self.env['import.api.call']._init(self._name, payload)
        config = self._process_payload_config(payload)
        config["logger"] = logger

        try:
            # Import with a new cursor, to keep 'logger' and previous transaction
            with modules.registry.Registry(self.env.cr.dbname).cursor() as new_cr:
                new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                new_self = self.with_env(new_env).with_company(config["company"])
                new_self._run_import_api(
                    data=payload.get('data') or {},
                    config=config
                )
        except Exception as e:
            if config["api_raise_exception"]:
                raise Exception(e)
            else:
                logger._add_line(
                    _("Unmanaged error during import. Details:\n%s", e),
                )

        logger._finish()
        return logger._get_api_response(config)

    @api.model
    def _run_import_api(self, data, config):
        """ Holds import logic. Should loop on "data" dict.
            TO INHERITE
        """
        pass
    
    def _process_payload_config(self, payload):
        """ 1. Get config from the payload,
            2. Apply defaults
            3. Convert ID keys into Odoo records
        """
        config = payload.get('config') or {}
        # Defaults
        for k, v in self._get_api_config_default().items():
            if not k in config:
                config[k] = v
        # Convert ID keys to records
        for key, model in self._get_import_config_keys_to_model().items():
            if key in config:
                config[key] = self.env[model].browse(config[key])
        return config
    @api.model
    def _get_api_config_default(self):
        """ Can be inherited """
        return {
            "api_report_format": "plain",
            "api_raise_exception": False,
            'origin': _("API call"),
            "company": self.env.company.id,
        }
    def _get_import_config_keys_to_model(self):
        return {
            "company": "res.company",
            "journal": "account.journal",
            "product": "product.product",
            "taxes": "account.tax",
            "account": "account.account",
            "payment": "account.payment",
        }


    #===== Front-end management =====#
    def fields_get(self, allfields=None, attributes=None):
        """ Make imported records readonly for end-users if configured
            as such (by default: they remain writable)
        """
        res = super().fields_get(allfields=allfields, attributes=attributes)
        if all([not bool(rec.external_ref) for rec in self]) and not self._context.get('test_mode'):
            return res

        IrConfig = self.env['ir.config_parameter'].sudo()
        api_readonly = str2bool(IrConfig.get_param('import_api.readonly_records', default='False'))
        if api_readonly:
            for field in res:
                res[field]['readonly'] = True

        return res

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """ Inherite dynamically 'tree', 'form' and 'search' views """
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        items = self._get_view_items().get(view_type, {})
        if items:
            View = self.env["ir.ui.view"]
            arch = etree.XML(res["arch"])
            all_models = res["models"].copy() # {modelname(str) ➔ fields(tuple)}
            for item in items:
                return self._get_view_add(
                    res, View, arch, all_models,
                    xpath=item['xpath'],
                    template=item.get('template', ''),
                    element=item.get('element', ''),
                    options=item.get('options', {}),
                )
        return res

    @api.model
    def _get_view_items(self):
        return {
            "form": [{
                "xpath": "//div[@role='alert']",
                "template": "base_import_api.import_api_banner",
            }],
            "list": [{
                "xpath": "//list",
                "element": "field",
                "options": {
                    "name": "external_ref",
                    "optional": "hide",
                }
            }],
            "search": [{
                "xpath": "//field[last()]",
                "element": "field",
                "options": {"name": "external_ref"}
            }],
        }
    
    @api.model
    def _get_view_add(self, res, View, arch, all_models, xpath, template='', element='', options={}):
        """ Add template or fields in 'tree', 'form', 'search', ... views
            Either pass args:
            - `template`: xmlid
            - or `element` and `option`: like 'field' and {'name': 'user_id', 'widget': 'many2one_avatar'}
        """
        root_node = arch.xpath(xpath)
        if not root_node:
            return res
        node = root_node[0]

        # place `new_node`
        new_node = None
        # generate new_node, from `template` or `element`, and place it
        if template:
            # generate
            str_element = self.env["ir.qweb"]._render(template)
            new_node = etree.fromstring(str_element)
            _, new_models = View.postprocess_and_fields(new_node, self._name)
            # place it
            for new_element in new_node:
                node.addnext(new_element)
        elif element:
            # generate & place it
            new_node = etree.SubElement(node, element, options)
            _, new_models = View.postprocess_and_fields(new_node, self._name)
        if new_node is None:
            _logger.warning(
                "`_get_view_add` called but no `new_node` generated: nothing added (%s, %s)."
                % (template, element)
            )
            return res

        _merge_view_fields(all_models, new_models)

        res["arch"] = etree.tostring(arch)
        res["models"] = tools.misc.frozendict(all_models)
        return res

def _merge_view_fields(all_models: dict, new_models: dict):
    """Merge new_models into all_models. Both are {modelname(str) ➔ fields(tuple)}."""
    for model, view_fields in new_models.items():
        if model in all_models:
            all_models[model] = tuple(set(all_models[model]) | set(view_fields))
        else:
            all_models[model] = tuple(view_fields)
