
from odoo import models, api
from odoo.tools import float_compare

from .product_product import TRANSITION_LAST_MO_ID

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.depends('quantity_done')
    def _compute_is_done(self):
        """ Overrwrite native field to order & color move_raw_ids by `is_done` """
        super()._compute_is_done()
        prec = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for move in self:
            comp = float_compare(move.quantity_done, move.product_uom_qty, precision_digits=prec)
            move.is_done = bool(comp >= 0)

    def _quantity_done_compute(self):
        """When PREP-pickings' moves are updated, trigger update of components lines"""
        super()._quantity_done_compute()
        moves_pickings = self.filtered(
            lambda x:
                not x.raw_material_production_id and
                not x.production_id
        )
        mos = moves_pickings.group_id.mrp_production_ids.filtered(
            # transitory mode
            lambda x: x.id > TRANSITION_LAST_MO_ID
        )
        date_from, date_to = False, False
        for mo in mos:
            date_to = mo.date_finished
            mo.move_raw_ids._update_qty_done_2steps(date_from, date_to)
            date_from = mo.date_finished # for next loop

    def _update_qty_done_2steps(self, date_from, date_to):
        """Update the MO's components 'quantity_done'
        as the sum of PREP-picking's 'Done'"""
        components = self.filtered(lambda x: x.state != "cancel")
        for component in components:
            moves_prep = component._get_prep_moves_2steps(date_from, date_to)
            component.quantity_done = sum(moves_prep.mapped("quantity_done"))

    def _get_prep_moves_2steps(self, date_from, date_to):
        """For a given component, return moves of PREP pickings
        :args `date_from` and `date_to`: in case of MO backorders, used to
                                         split pickings' moves between MOs
        """
        self.ensure_one()
        pickings = self.raw_material_production_id.picking_ids

        # Filter only the pickings's move of this MO, according to:
        # - picking's "Scheduled date (date)""
        # - mo's `finished_date`
        domain = []
        if date_from:
            domain += [("date", ">", date_from)]
        if date_to:
            domain += [("date", "<", date_to)]
        if domain:
            pickings = pickings.filtered_domain(domain)

        return pickings.move_ids.filtered(
            lambda x: x.state == "done" and
                      x.product_id == self.product_id
        )

    @api.model
    def _is_manual_consumption(self):
        """Helps not updating 'Consumed' qty of components
        when modifying MO's 'qty_producing'"""
        self.ensure_one()
        return (
            self.raw_material_production_id or
            super()._is_manual_consumption()
        )

    def _update_quantity_done(self, _):
        """We do not want to update 'Consumed' qty of components
        when modifying components's 'product_uom_qty'"""
        return

    #===== Transitory =====#
    def write(self, vals):
        """ For MO's components, ensure `product_uom_qty` is >= `quantity_done`
            Because `product_uom_qty` is used for for stock forecast
            (just do like when the `stock.move` is validated)
        """
        res = super().write(vals)

        raw_material_ids = self.filtered(
            lambda x:
                x.raw_material_production_id and
                # transitory mode
                x.raw_material_production_id.id <= TRANSITION_LAST_MO_ID
        )
        raw_material_ids._synch_product_uom_qty_done()
        raw_material_ids.product_id.stock_quant_ids.check_negative_qty() # ALY - 2025-08-21 : to be removed when `mrp_raw_material_confirmation` is ready

        return res
    
    def _synch_product_uom_qty_done(self):
        """ Updates any `product_uom_qty` >= `quantity_done` to `quantity_done` """
        for move in self:
            if move.quantity_done > move.product_uom_qty:
                move.product_uom_qty = move.quantity_done

    #===== Legacy =====#
    # def unlink(self):
    #     """ *Delete* button is always displayed for `move_raw_ids` and behaves like:
    #         - unlinks `move_raw_ids` if possible ;
    #         - else (if move is `done`), sets qty to 0 instead
    #     """
    #     move_raw_ids = self.filtered('raw_material_production_id')
    #     to_cancel = move_raw_ids.filtered(lambda x: x.state != 'cancel')
    #     to_unlink = self - to_cancel

    #     # Unlink normally if possible (or if not raw material)
    #     super(StockMove, to_unlink).unlink()
        
    #     if to_cancel:
    #         # Not cancellable components: quantity_done = 0
    #         to_zero = to_cancel.filtered(lambda x: x.state == 'done')
    #         to_zero.quantity_done = 0.0

    #         # If components can be canceled: cancel & delete
    #         (to_cancel - to_zero)._action_cancel()
    #         super(StockMove, to_cancel - to_zero).unlink()
