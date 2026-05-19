# Copyright 2026 Arnaud LAYEC (Akretion) <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import threading

from odoo import models

from .product_product import TRANSITION_LAST_MO_ID

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        """When PREP-pickings' moves are confirmed, trigger the
        update of related MO's components 'quantity_done'"""
        res = super()._action_done()

        mos = self.group_id.mrp_production_ids
        # transitory mode
        test_mode = (
            getattr(threading.current_thread(), 'testing', False) or
            self.env.registry.in_test_mode()
        )
        mos = mos.filtered(lambda x: x.id > TRANSITION_LAST_MO_ID or test_mode)

        date_from, date_to = False, False
        for mo in mos:
            date_to = mo.date_finished
            mo.move_raw_ids._update_qty_done_2steps(date_from, date_to)
            date_from = mo.date_finished # for next loop

        return res
