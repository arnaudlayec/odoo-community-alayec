# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProductAttribute(models.Model):
    _inherit = ["product.attribute"]

    values_date_ranged = fields.Boolean(
        string='Date-ranged values?',
        help='For budgets, if the products with this attribute are used to value'
             ' a budget per date range.',
        default=False
    )

class ProductAttributeValue(models.Model):
    _inherit = ["product.attribute.value"]

    date_from = fields.Date(
        string='Date',
        help='For budgets, date from which the variant with this attribute becomes'
             ' the reference one for the product cost.'
    )
