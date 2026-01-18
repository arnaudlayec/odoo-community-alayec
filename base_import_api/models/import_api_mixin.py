# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.tools.misc import str2bool

from lxml import etree

import logging
_logger = logging.getLogger(__name__)

class ImportApiMixin(models.AbstractModel):
    _name = 'import.api.mixin'
    _description = "Import API mixin"
    _inherit = ['mail.thread']

    external_id = fields.Char(
        string='External ID',
        help='Reference in the external tool, when synchronized',
        readonly=True,
    )

    #===== API Endpoint =====#
    def import_api(self, payload:dict) -> dict:
        """ `payload` expected format:
            {
                'config': {}, # dict
                'data': ..., # any type
            }
        """
        self = self.with_context(import_api=True) # for inheritance (not used here)
        logger = self.env['import.api.call']._init(self._name, payload)

        # config: get it from the payload and apply defaults
        config = payload.get('config', {})
        for k, v in self._get_import_config_default().items():
            if not k in config:
                config[k] = v

        # launch the import
        company = self.env['res.company'].browse(config.get("company"))
        self.with_company(company)._run_import_api(
            payload.get('data', {}), config, logger
        )

        logger._finish()
        return logger._get_api_response()

    def _run_import_api(self, data, config):
        """ TO INHERITE """
        pass
    
    def _get_import_config_default(self):
        """ Can be inherited """
        return {
            "company": self.env.company.id,
        }
    
    #===== Front-end management =====#
    def fields_get(self, allfields=None, attributes=None):
        """ Make imported records readonly for end-users if configured
            as such (by default: they remain writable)
        """
        res = super().fields_get(allfields=allfields, attributes=attributes)
        if all([not bool(rec.external_id) for rec in self]) and not self._context.get('test_mode'):
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
    def _get_view_items(self):
        return {
            "form": [{
                "xpath": "//div[hasclass('oe_title')]",
                "template": "base_import_api.import_api_banner",
            }],
            "list": [{
                "xpath": "//list",
                "element": "field",
                "options": {
                    "name": "external_id",
                    "optional": "hide",
                }
            }],
            "search": [{
                "xpath": "//field[last()]",
                "element": "field",
                "options": {"name": "external_id"}
            }],
        }
    def _get_view_add(self, res, View, arch, all_models, xpath, template='', element='', options={}):
        """ Add template or fields in 'tree', 'form', 'search', ... views
            Either pass args:
            - `template`: xmlid
            - or `element` and `option`: like 'field' and {'name': 'user_id', 'widget': 'many2one_avatar'}
        """
        root_node = arch.xpath(xpath)

        # place `new_node`
        for node in root_node:
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
