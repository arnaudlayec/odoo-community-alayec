# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression

class AccountMoveBudgetLine(models.Model):
    _inherit = ["account.move.budget.line"]

    #===== Default: when user arrive on the form with `default_xxx` context keys =====#
    @api.model
    def default_get(self, default_fields):
        vals = super().default_get(default_fields)

        if not self._no_empty_fields(vals):
            template_line = self._get_matching_template_lines([vals])
            vals = self._prefill_fields(template_line, vals)

        return vals
    
    #===== CRUD (create): create() ORM programmtic calls =====#
    @api.model_create_multi
    def create(self, vals_list):
        template_lines = self._get_matching_template_lines(vals_list)
        for vals in vals_list:
            vals = self._prefill_fields(template_lines, vals)
        
        return super().create(vals_list)

    #===== Onchange (modification) =====#
    @api.onchange('account_id', 'analytic_account_id', 'partner_id')
    def _onchange_prefill(self):
        template_lines = self._get_matching_template_lines()
        for line in self:
            line._prefill_fields(template_lines)
    
    #===== Logics (search/copy) =====#
    def _get_copied_fields(self):
        return self._get_searchable_fields() + ['name']
    
    def _get_searchable_fields(self):
        return ['account_id', 'analytic_account_id', 'partner_id']
    
    def _get_key(self, vals, key):
        """ read key in `vals`, which is a dict or recordset """
        return bool(key in vals) and (
            vals[key].id if hasattr(vals[key], 'id') # `vals` is a record and `vals[key]` a M2o field
            else vals[key] # dict or non-M2o field
        )
    
    def _no_empty_fields(self, vals):
        return all(k in vals and vals[k] for k in self._get_copied_fields())
    

    def _prefill_fields(self, template_lines, vals={}):
        """ Fetch `template` line in `template_lines`
            and copy template values in `self` or `vals`
            without erasing the existing ones
        """
        vals = vals or self
        if not vals:
            return {}

        # Get the template line (if any)
        key = self._get_search_pattern(vals)
        template = self._get_by_pattern(template_lines, key)
        if not template:
            return vals

        # Prefill empty vals (if any)
        for field in self._get_copied_fields():
            if not field in vals or not vals[field]:
                vals[field] = template[field]
        
        return vals
    
    def _get_by_pattern(self, template_lines, search_key):
        """ Given the `search_key` like (a, b, c), search
            the item in `template_lines` whose key matches
            `search_key`, ignoring any False a, b or c
        """
        for key, vals in template_lines.items():
            if all(sk is False or sk == k for sk, k in zip(search_key, key)):
                return vals
        return False


    def _get_search_pattern(self, vals={}):
        """ :option self: from onchange
            :option vals_list: from create and default_get

            Return: tuple, like `key` of `_get_matching_template_lines` output
        """
        vals = vals or self
        return tuple([self._get_key(vals, key) for key in self._get_searchable_fields()])


    def _get_matching_template_lines(self, vals_list={}):
        """ According to values already set in the line, find the 1st matching template line
            and return the budget line values

            :option self: from onchange
            :option vals_list: from create and default_get
            :return: [
                (account_id, analytic_id, partner_id): vals
            ]
        """
        copied_keys = self._get_copied_fields()
        search_keys = self._get_searchable_fields()
        vals_list = vals_list or self

        # 1. Prepare search domain
        domain = []
        for vals in vals_list:
            # don't try templating if all target vals are already set
            if self._no_empty_fields(vals):
                continue

            # search for a template line matching **the set** search fields of real line
            domain_part = [
                (key, '=', self._get_key(vals, key))
                for key in search_keys
                if key in vals and vals[key]
            ]
            domain = expression.OR([domain, domain_part])
        
        res = {}
        if not domain:
            return res
        
        # 2. Search, with read_group to get only 1st results
        Template = self.env['account.move.budget.line.template'].sudo()
        fields_agg = [f'{key}:array_agg' for key in set(copied_keys) - set(search_keys)]
        rg_result = Template.read_group(domain=domain, groupby=search_keys, fields=fields_agg, lazy=False)

        # 3. Format output
        for x in rg_result:
            key = tuple([x[search_key] and x[search_key][0] for search_key in search_keys])
            vals = (
                {search_key: x[search_key] and x[search_key][0] for search_key in search_keys}
                | {field: x[field] and x[field][0] for field in set(copied_keys) - set(search_keys)}
            )
            res[key] = vals

        return res
