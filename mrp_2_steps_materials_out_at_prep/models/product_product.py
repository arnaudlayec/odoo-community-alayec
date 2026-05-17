from odoo import models
from odoo.osv import expression

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_domain_locations_new(self, location_ids):
        """Exclude locations of type 'production' from the calcultation
        of qty_available, thus making the validation of PREP 1-steps
        pickings having immediate effect on stock levels."""
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = (
            super()._get_domain_locations_new(location_ids)
        )
        domain_quant_loc = expression.AND([
            domain_quant_loc,
            [('location_id.usage', '!=', 'production')]
        ])
        return domain_quant_loc, domain_move_in_loc, domain_move_out_loc
