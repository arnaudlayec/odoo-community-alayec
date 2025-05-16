# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_compare

class PurchaseOrderLine(models.Model):
    _inherit = ['purchase.order.line']

    vendor_price_update = fields.Boolean(
        string='Vendor Price Update',
        compute='_compute_vendor_update',
    )
    vendor_discount_update = fields.Boolean(
        string='Vendor Discount Dpdate',
        compute='_compute_vendor_update',
    )

    #===== Compute =====#
    @api.depends('partner_id', 'product_id')
    def _compute_vendor_update(self):
        prec = self.env['decimal.precision'].precision_get('Product Price')
        purchase_discount = 'discount' in self
        
        fields = ['price:array_agg'] + (['discount:array_agg'] if purchase_discount else [])
        mapped_data = self._helper_get_vendor_data(fields)

        for line in self:
            key = (line.partner_id.id, line.product_id.id)
            data = mapped_data.get(key, {})
            price = data.get('price')

            line.vendor_price_update = bool(
                price and
                float_compare(price, line.price, precision_digits=prec) == 0
            )
            line.vendor_discount_update = purchase_discount and data.get('discount')

    def _helper_get_vendor_data(self, fields):
        rg_result = self.env['product.supplierinfo'].read_group(
            domain=[('partner_id', 'in', self.partner_id.ids), ('product_id', 'in', self.product_id.ids)],
            groupby=['product_id', 'partner_id'],
            fields=[field + ':array_agg' for field in fields]
        )
        return {
            (x['partner_id'][0], x['product_id'][0]):
            {field: bool(x[field]) and x[field][0] for field in fields}
            for x in rg_result
        }

    #===== Action ======#
    def action_update_supplierinfo_cost(self):
        self._update_supplierinfo_data('price', 'price_unit')
    
    def action_update_supplierinfo_discount(self):
        self._update_supplierinfo_data('discount', 'discount')
    
    def _update_supplierinfo_data(self, vendor_field, line_field):
        Vendor = self.env['product.supplierinfo']
        mapped_data = self._get_supplerinfo_mapped_ids()
        print('mapped_data', mapped_data)
        for line in self:
            vendor = Vendor.browse(mapped_data.get(line.id))
            if vendor:
                vendor[vendor_field] = line[line_field]

    def _get_supplerinfo_mapped_ids(self):
        """ Return best vendor id line for a given purchase order line
            :return: dict like {line.id: supplierinfo.id}
        """
        mapped_data = self._helper_get_vendor_data(['id'])
        return {
            line.id: mapped_data.get((line.partner_id.id, line.product_id.id), {}).get('id')
            for line in self
        }
