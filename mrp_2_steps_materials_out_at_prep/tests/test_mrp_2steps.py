# Copyright 2026 Arnaud LAYEC (Akretion) <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import RedirectWarning
from odoo.addons.mrp.tests.common import TestMrpCommon


def _validate_picking(picking, qty_done_per_move=None):
    """Helper: set quantity_done on each move and validate the picking.

    :param picking: stock.picking record
    :param qty_done_per_move: dict {move: qty} or None (uses demand qty for all)
    """
    for move in picking.move_ids:
        qty = (qty_done_per_move or {}).get(move, move.product_uom_qty)
        move.quantity_done = qty
    picking._action_done()


class TestMrp2StepsMaterialsOutAtPrep(TestMrpCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # --- Dedicated 2-steps warehouse ---
        cls.warehouse_2s = cls.env['stock.warehouse'].create({
            'name': 'Test 2-Steps WH',
            'code': 'T2S',
            'manufacture_steps': 'pbm',
        })
        cls.stock_location_2s = cls.warehouse_2s.lot_stock_id

        # Pre-production location (created automatically by Odoo for pbm warehouses)
        cls.preprod_location = cls.warehouse_2s.pbm_loc_id

        # --- Finished product & component ---
        # We reuse product_1 (finished) and product_2 (component) from TestMrpCommon.
        # Ensure enough stock of the component so most tests don't fail on stock shortage.
        cls.env['stock.quant']._update_available_quantity(
            cls.product_2,
            cls.stock_location_2s,
            quantity=100.0,
        )

        # --- BoM scoped to our 2-steps warehouse ---
        # TestMrpCommon's bom_1 may be bound to warehouse_1; create a clean one.
        cls.bom_2s = cls.env['mrp.bom'].create({
            'product_tmpl_id': cls.product_1.product_tmpl_id.id,
            'product_qty': 1.0,
            'type': 'normal',
            'bom_line_ids': [Command.create({
                'product_id': cls.product_2.id,
                'product_qty': 1.0,
            })],
        })

        # --- Base MO (confirmed, 2-steps) reused in most tests ---
        cls.mo, cls.prep_picking = cls._make_confirmed_mo(qty_final=1.0, qty_component=1.0)
        cls.component_move = cls._get_component_move(cls.mo)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @classmethod
    def _make_confirmed_mo(cls, qty_final=1.0, qty_component=1.0):
        """Create and confirm a MO on warehouse_2s.

        :return: (mo, prep_picking)  — the confirmed MO and its PREP picking.
        """
        mo = cls.env['mrp.production'].create({
            'product_id': cls.product_1.id,
            'bom_id': cls.bom_2s.id,
            'product_qty': qty_final,
            'picking_type_id': cls.warehouse_2s.manu_type_id.id,
        })
        mo.action_confirm()

        # After confirmation, a PREP picking must exist
        prep = mo.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
        assert len(prep) == 1, "Expected exactly 1 PREP picking after MO confirmation"
        return mo, prep

    @classmethod
    def _get_component_move(cls, mo):
        """Return the move_raw_ids line for product_2 on *mo*."""
        return mo.move_raw_ids.filtered(lambda m: m.product_id == cls.product_2)

    @classmethod
    def _get_qty_available(cls, product=None, location=None):
        """Return the available qty of a product on a location"""
        product = product or cls.product_2
        location = location or cls.stock_location_2s
        return product.with_context(
            location=location.id
        ).qty_available

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_mo_validation_except_open_prep_picking(self):
        """Validating an MO with an open PREP must raise, except if BackOrder MO"""
        # Do NOT validate the PREP picking — it remains open
        with self.assertRaises(RedirectWarning):
            self.mo.button_mark_done()

        # Call button_mark_done with skip_backorder=True => should not raise
        try:
            self.mo.with_context(skip_backorder=True).button_mark_done()
        except RedirectWarning:
            self.fail("Should not raise with `skip_backorder` in context")

    def test_mo_qty_done_update_after_validate_picking(self):
        """Validating the PREP must update `quantity_done`
        on the MO component with the sum of done quantities."""
        _validate_picking(self.prep_picking)
        self.assertEqual(
            self.component_move.quantity_done,
            1.0,
        )

    def test_mo_qty_done_no_affect_with_draft_picking(self):
        """Writing qty_done on a *draft* PREP picking must not
        update the MO component's quantity_done"""
        qty_before = self.component_move.quantity_done

        # Write a done qty directly on the PREP move without validating
        prep_move = self.prep_picking.move_ids.filtered(lambda m: m.product_id == self.product_2)
        prep_move.quantity_done = 1.0

        self.assertEqual(
            self.component_move.quantity_done,
            qty_before,
        )

    def test_stock_decreases_at_prep_validation(self):
        """Stock level must decrease immediately when the PREP picking
        is validated (not at MO validation)."""
        qty_before = self._get_qty_available()
        _validate_picking(self.prep_picking)
        qty_after_prep = self._get_qty_available()

        self.assertLess(qty_after_prep, qty_before)
        self.assertEqual(qty_before - qty_after_prep, 1.0)

    def test_stock_unchanged_at_mo_validation(self):
        """Validating the MO after the PREP must NOT decrease the stock
        a second time"""
        _validate_picking(self.prep_picking)
        qty_after_prep = self._get_qty_available()

        self.mo.qty_producing = self.mo.product_qty
        self.mo.button_mark_done()

        qty_after_mo = self._get_qty_available()
        self.assertEqual(qty_after_prep, qty_after_mo,)

    def test_neutralize_mo_qty_producing_update(self):
        """Incrementing `qty_producing` on the MO must NOT
        update the component's `quantity_done`"""
        # Initialization
        mo, prep = self._make_confirmed_mo(qty_final=2.0, qty_component=2.0)
        component_move = self._get_component_move(mo)

        prep_move = prep.move_ids.filtered(lambda m: m.product_id == self.product_2)
        _validate_picking(prep, qty_done_per_move={prep_move: 1.0})

        qty_done_after_prep = component_move.quantity_done
        self.assertEqual(qty_done_after_prep, 1.0)

        # Now increment qty_producing on the MO — native Odoo would update
        # quantity_done automatically, but _is_manual_consumption must block it.
        mo.qty_producing = 2.0
        self.assertEqual(
            component_move.quantity_done,
            qty_done_after_prep,
        )

    def test_neutralize_move_product_uom_qty_update(self):
        """Modifying `product_uom_qty` (To Consume) on the
        component must NOT change its quantity_done"""
        # Initialization
        mo, prep = self._make_confirmed_mo(qty_final=2.0, qty_component=2.0)
        component_move = self._get_component_move(mo)

        # Validate PREP partially (qty=1 out of 2)
        prep_move = prep.move_ids.filtered(lambda m: m.product_id == self.product_2)
        _validate_picking(prep, qty_done_per_move={prep_move: 1.0})

        qty_done_after_prep = component_move.quantity_done
        self.assertEqual(
            qty_done_after_prep,
            1.0,
        )

        # Modify the To Consume quantity — native Odoo would call _update_quantity_done
        # and potentially adjust quantity_done, but our override makes it a no-op.
        component_move.product_uom_qty = 3.0
        self.assertEqual(
            component_move.quantity_done,
            qty_done_after_prep,
        )
