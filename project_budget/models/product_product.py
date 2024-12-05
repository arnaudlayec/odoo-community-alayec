# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import date_utils

class ProductProduct(models.Model):
    _inherit = ["product.product"]

    standard_price_date_ranged = fields.Boolean(
        compute='_compute_standard_price_date_ranged',
        help='If activated, the standard cost is only applicable between Date From and Date To'
    )
    date_from = fields.Date(
        string='Date From',
        help='For budgets, date from which this variant becomes'
             ' the reference one for the product cost (until next one).'
    )
    date_to = fields.Date(
        string='Date To',
        compute='_compute_date_to'
    )

    _sql_constraints = [(
        "date_from_per_tmpl",
        "UNIQUE (date_from, product_tmpl_id)",
        "Another variant already has the same start date (for cost valuation in budgets)."
    )]

    #===== Compute =====#
    @api.depends('product_template_attribute_value_ids.attribute_line_id.attribute_id.values_date_ranged')
    def _compute_standard_price_date_ranged(self):
        """ A variant's cost is date-ranged depending if it has >=1 attributes with date-ranged values """
        attribute_ids = self.product_template_attribute_value_ids.attribute_line_id.attribute_id
        attribute_ids_date_ranged = attribute_ids.filtered('values_date_ranged')
        template_ids_date_range = attribute_ids_date_ranged.product_tmpl_ids.ids

        for product in self:
            product.standard_price_date_ranged = product.product_tmpl_id.id in template_ids_date_range

    @api.depends('product_tmpl_id.product_variant_ids.date_from')
    def _compute_date_to(self):
        """ `date_to` is either: `date_from - 1 day` of next variant or False if no next variant """
        # if not date_from, can't compute date_to
        no_date_from = self.filtered(lambda x: not x.date_from)
        no_date_from.date_to = fields.Date.today()
        self = self - no_date_from
        if not self.ids: # early quit for perf., if already finished
            return
        
        rg_result = self.read_group(
            domain=[('product_tmpl_id', 'in', self.product_tmpl_id.ids)],
            groupby=['product_tmpl_id'],
            fields=['dates_from:array_agg(date_from)']
        )
        mapped_dates_from = {x['product_tmpl_id'][0]: x['dates_from'] for x in rg_result}
        for variant in self:
            dates_from = mapped_dates_from.get(variant.product_tmpl_id.id, []) # all `date_from` of siblings
            next_date_from = [date for date in dates_from if date > variant.date_from]
            variant.date_to = date_utils.subtract(min(next_date_from), days=1) if next_date_from else False

    #===== Buttons & actions =====#
    def button_open_attributes(self):
        """ From variant list view, open attribute's form (if single) or attributes' list (if several) """
        attribute_ids = self.product_template_attribute_value_ids.attribute_line_id.attribute_id

        if len(attribute_ids.ids) == 1:
            attribute_id = fields.first(attribute_ids)
            action = {
                'view_mode': 'form',
                'name': attribute_id.name,
                'res_id': attribute_id.id
            }
        else:
            action = {
                'view_mode': 'tree',
                'name': _('Attributes'),
                'domain': [('id', 'in', self.attribute_ids.ids)],
                'context': {'_default_values_date_ranged': True}
            }

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.attribute'
        } | action
