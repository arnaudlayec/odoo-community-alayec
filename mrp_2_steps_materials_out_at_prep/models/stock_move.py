
from odoo import models, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _quantity_done_compute(self):
        """When PREP-pickings' moves are updated, trigger update of components lines"""
        super()._quantity_done_compute()
        moves_pickings = self.filtered(
            lambda x: not x.raw_material_production_id and not x.production_id
        )
        mos = moves_pickings.group_id.mrp_production_ids
        date_from, date_to = False, False
        for mo in mos:
            date_to = mo.date_finished
            mo.move_raw_ids._update_qty_done_2steps(date_from, date_to)
            date_from = mo.date_finished # for next loop

    def _update_qty_done_2steps(self, date_from, date_to):
        """Update the MO's components 'quantity_done'
        as the sum of PREP-picking's 'Done'"""
        for component in self:
            moves_prep = component._get_prep_moves_2steps(date_from, date_to)
            component.quantity_done = sum(moves_prep.mapped("quantity_done"))

    def _get_prep_moves_2steps(self, date_from, date_to):
        """For a given component, return moves of PREP pickings
        :args `date_from` and `date_to`:
            in case of backorders, are used to split pickings' moves between MO
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
            lambda x: x.product_id == self.product_id
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
