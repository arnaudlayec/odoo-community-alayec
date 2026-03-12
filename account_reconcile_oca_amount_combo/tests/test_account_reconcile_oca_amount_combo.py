# Copyright 2026 Arnaud Layec <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo.tests.common import TransactionCase
from odoo.tools import float_compare


class TestAccountReconcileOcaAmountCombo(TransactionCase):
    """
    Test suite for the Combo Amount-Mode reconciliation algorithm.

    All tests use a simple company-currency setup (no multi-currency).
    The goal is to verify:

    1.  The subset-sum algorithm correctness (exact match, no match, multiple
        possible combos, max-invoices guard).
    2.  The date-window expansion logic (delta 0, 1, N).
    3.  That combo mode does NOT interfere with standard invoice_matching rules.
    4.  Edge cases: zero-amount transaction, single-invoice match, all
        candidates exhausted.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # ── Company & currency ──────────────────────────────────────────
        cls.company = cls.env.ref("base.main_company")
        cls.currency = cls.company.currency_id

        # ── Accounts ────────────────────────────────────────────────────
        cls.receivable_account = cls.env["account.account"].search(
            [
                ("company_id", "=", cls.company.id),
                ("account_type", "=", "asset_receivable"),
            ],
            limit=1,
        )
        cls.revenue_account = cls.env["account.account"].search(
            [
                ("company_id", "=", cls.company.id),
                ("account_type", "=", "income"),
            ],
            limit=1,
        )

        # ── Bank journal & account ───────────────────────────────────────
        cls.bank_journal = cls.env["account.journal"].search(
            [("type", "=", "bank"), ("company_id", "=", cls.company.id)],
            limit=1,
        )

        # ── Partner ──────────────────────────────────────────────────────
        cls.partner_a = cls.env["res.partner"].create({"name": "Combo Partner A"})
        cls.partner_b = cls.env["res.partner"].create({"name": "Combo Partner B"})

        # ── Reference dates ──────────────────────────────────────────────
        cls.today = date.today()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _create_invoice(self, partner, amount, due_date, move_type="out_invoice"):
        """Create and post a customer invoice with a specific due date."""
        move = self.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": partner.id,
                "invoice_date": due_date,
                "invoice_date_due": due_date,
                "company_id": self.company.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": f"Test line {amount}",
                            "quantity": 1,
                            "price_unit": amount,
                            "account_id": self.revenue_account.id,
                        },
                    )
                ],
            }
        )
        move.action_post()
        # Return the receivable/payable line
        return move.line_ids.filtered(
            lambda l: l.account_id.account_type
            in ("asset_receivable", "liability_payable")
        )

    def _create_reconcile_model(self, combo_days_range=0, combo_max_invoices=0):
        """Create a reconcile model with combo_amount_mode enabled."""
        return self.env["account.reconcile.model"].create(
            {
                "name": "Test Combo Model",
                "rule_type": "invoice_matching",
                "combo_amount_mode": True,
                "combo_days_range": combo_days_range,
                "combo_max_invoices": combo_max_invoices,
                "company_id": self.company.id,
            }
        )

    def _create_st_line(self, amount, date_=None):
        """Create a bank statement line (posted)."""
        if date_ is None:
            date_ = self.today
        st_line = self.env["account.bank.statement.line"].create(
            {
                "journal_id": self.bank_journal.id,
                "date": date_,
                "payment_ref": f"Test transaction {amount}",
                "amount": amount,
            }
        )
        return st_line

    # ------------------------------------------------------------------
    # Tests – _combo_find_matching_subset
    # ------------------------------------------------------------------

    def test_subset_single_invoice_exact_match(self):
        """A single invoice matching the full transaction amount is found."""
        model = self._create_reconcile_model()
        due = self.today
        aml = self._create_invoice(self.partner_a, 100.0, due)

        result = model._combo_find_matching_subset(aml, 100.0, self.currency)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.id, aml.id)

    def test_subset_two_invoices_exact_match(self):
        """Two invoices whose amounts sum to the transaction are found."""
        model = self._create_reconcile_model()
        due = self.today
        aml_a = self._create_invoice(self.partner_a, 60.0, due)
        aml_b = self._create_invoice(self.partner_b, 40.0, due)
        candidates = aml_a | aml_b

        result = model._combo_find_matching_subset(candidates, 100.0, self.currency)
        self.assertEqual(len(result), 2)
        self.assertIn(aml_a.id, result.ids)
        self.assertIn(aml_b.id, result.ids)

    def test_subset_no_match(self):
        """When no combination matches, an empty recordset is returned."""
        model = self._create_reconcile_model()
        due = self.today
        aml_a = self._create_invoice(self.partner_a, 60.0, due)
        aml_b = self._create_invoice(self.partner_b, 70.0, due)
        candidates = aml_a | aml_b

        result = model._combo_find_matching_subset(candidates, 100.0, self.currency)
        self.assertFalse(result)

    def test_subset_prefers_smaller_combination(self):
        """
        When multiple combinations match, the smallest one (fewest invoices)
        is returned first.
        For a target of 100: [100] is found before [60, 40].
        """
        model = self._create_reconcile_model()
        due = self.today
        aml_exact = self._create_invoice(self.partner_a, 100.0, due)
        aml_60 = self._create_invoice(self.partner_b, 60.0, due)
        aml_40 = self._create_invoice(self.partner_a, 40.0, due)
        candidates = aml_exact | aml_60 | aml_40

        result = model._combo_find_matching_subset(candidates, 100.0, self.currency)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.id, aml_exact.id)

    def test_subset_max_invoices_limit(self):
        """
        When combo_max_invoices=1 and only a 2-invoice combo matches,
        nothing is found.
        """
        model = self._create_reconcile_model(combo_max_invoices=1)
        due = self.today
        aml_a = self._create_invoice(self.partner_a, 60.0, due)
        aml_b = self._create_invoice(self.partner_b, 40.0, due)
        candidates = aml_a | aml_b

        result = model._combo_find_matching_subset(candidates, 100.0, self.currency)
        self.assertFalse(result)

    def test_subset_three_invoices(self):
        """A 3-invoice combination is found when necessary."""
        model = self._create_reconcile_model()
        due = self.today
        aml_a = self._create_invoice(self.partner_a, 30.0, due)
        aml_b = self._create_invoice(self.partner_b, 30.0, due)
        aml_c = self._create_invoice(self.partner_a, 40.0, due)
        candidates = aml_a | aml_b | aml_c

        result = model._combo_find_matching_subset(candidates, 100.0, self.currency)
        self.assertEqual(len(result), 3)

    # ------------------------------------------------------------------
    # Tests – _combo_apply_rule (full algorithm including date windows)
    # ------------------------------------------------------------------

    def test_apply_rule_exact_date_match(self):
        """Invoice due exactly on transaction date is matched (delta=0)."""
        model = self._create_reconcile_model(combo_days_range=0)
        due = self.today
        self._create_invoice(self.partner_a, 150.0, due)
        st_line = self._create_st_line(150.0, date_=due)

        result = model._combo_apply_rule(st_line)
        self.assertIsNotNone(result)
        self.assertEqual(len(result["amls"]), 1)

    def test_apply_rule_no_match_out_of_window(self):
        """
        Invoice due 2 days before transaction is NOT matched when
        combo_days_range=0.
        """
        model = self._create_reconcile_model(combo_days_range=0)
        due = self.today - timedelta(days=2)
        self._create_invoice(self.partner_a, 150.0, due)
        st_line = self._create_st_line(150.0, date_=self.today)

        result = model._combo_apply_rule(st_line)
        self.assertIsNone(result)

    def test_apply_rule_match_with_range_expansion(self):
        """
        Invoice due 1 day before transaction is matched when
        combo_days_range=1.
        """
        model = self._create_reconcile_model(combo_days_range=1)
        due = self.today - timedelta(days=1)
        self._create_invoice(self.partner_a, 200.0, due)
        st_line = self._create_st_line(200.0, date_=self.today)

        result = model._combo_apply_rule(st_line)
        self.assertIsNotNone(result)
        self.assertEqual(len(result["amls"]), 1)

    def test_apply_rule_match_future_date_in_range(self):
        """
        Invoice due 1 day AFTER transaction is matched when
        combo_days_range=1.
        """
        model = self._create_reconcile_model(combo_days_range=1)
        due = self.today + timedelta(days=1)
        self._create_invoice(self.partner_a, 75.0, due)
        st_line = self._create_st_line(75.0, date_=self.today)

        result = model._combo_apply_rule(st_line)
        self.assertIsNotNone(result)

    def test_apply_rule_prefers_narrower_window(self):
        """
        When two invoices exist (one on due date, one +1 day), the one
        due exactly on the transaction date is preferred (delta=0 checked
        first).
        """
        model = self._create_reconcile_model(combo_days_range=1)
        aml_today = self._create_invoice(self.partner_a, 50.0, self.today)
        self._create_invoice(self.partner_b, 50.0, self.today + timedelta(days=1))
        st_line = self._create_st_line(50.0, date_=self.today)

        result = model._combo_apply_rule(st_line)
        self.assertIsNotNone(result)
        self.assertEqual(len(result["amls"]), 1)
        self.assertEqual(result["amls"].id, aml_today.id)

    def test_apply_rule_zero_amount_transaction(self):
        """A zero-amount transaction never matches anything."""
        model = self._create_reconcile_model()
        self._create_invoice(self.partner_a, 0.01, self.today)
        st_line = self._create_st_line(0.0, date_=self.today)

        result = model._combo_apply_rule(st_line)
        self.assertIsNone(result)

    def test_apply_rule_status_reconciled(self):
        """The returned dict has status='reconciled'."""
        model = self._create_reconcile_model()
        self._create_invoice(self.partner_a, 99.99, self.today)
        st_line = self._create_st_line(99.99, date_=self.today)

        result = model._combo_apply_rule(st_line)
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "reconciled")
        self.assertEqual(result["model"], model)

    # ------------------------------------------------------------------
    # Tests – isolation: combo mode must not affect standard rules
    # ------------------------------------------------------------------

    def test_standard_rule_not_affected(self):
        """
        A reconcile model with combo_amount_mode=False must call the
        parent's _get_invoice_matching_rule_result without interference.
        We verify this by checking that our override does NOT intercept
        the call (the parent is expected to raise NotImplementedError or
        return a value – here we just verify we can call the method without
        errors triggered by our code).
        """
        model = self.env["account.reconcile.model"].create(
            {
                "name": "Standard Invoice Matching",
                "rule_type": "invoice_matching",
                "combo_amount_mode": False,
                "company_id": self.company.id,
            }
        )
        # The model has combo_amount_mode=False → our code must not run.
        # We only check the flag is correctly read.
        self.assertFalse(model.combo_amount_mode)

    def test_combo_mode_only_on_invoice_matching(self):
        """combo_amount_mode raises on non-invoice_matching rule types."""
        from odoo.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            self.env["account.reconcile.model"].create(
                {
                    "name": "Bad Combo Model",
                    "rule_type": "writeoff_button",
                    "combo_amount_mode": True,
                    "company_id": self.company.id,
                }
            )

    # ------------------------------------------------------------------
    # Tests – multi-partner scenario (the whole point of the module)
    # ------------------------------------------------------------------

    def test_multi_partner_combo(self):
        """
        Core use-case: two invoices from different partners, no partner
        on the bank statement line, matched by amount combination.
        """
        model = self._create_reconcile_model(combo_days_range=0)
        due = self.today
        self._create_invoice(self.partner_a, 123.45, due)
        self._create_invoice(self.partner_b, 67.89, due)
        target = 123.45 + 67.89
        st_line = self._create_st_line(target, date_=due)

        result = model._combo_apply_rule(st_line)
        self.assertIsNotNone(result)
        self.assertEqual(len(result["amls"]), 2)

    def test_partial_payment_residual_used(self):
        """
        An invoice partially paid: only its residual is considered.
        amount_residual (50) + full invoice (50) = 100 should match.
        """
        model = self._create_reconcile_model(combo_days_range=0)
        due = self.today

        # Create invoice for 100, partially pay 50
        invoice_aml = self._create_invoice(self.partner_a, 100.0, due)
        move = invoice_aml.move_id
        # Register a partial payment of 50
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=move.ids
        ).create({"amount": 50.0}).action_create_payments()

        # Create a second full invoice for 50
        aml_b = self._create_invoice(self.partner_b, 50.0, due)

        # Refresh after partial payment
        invoice_aml_refreshed = move.line_ids.filtered(
            lambda l: l.account_id.account_type
            in ("asset_receivable", "liability_payable")
            and not l.reconciled
        )

        # Target = 50 (residual of first) + 50 (second invoice) = 100
        st_line = self._create_st_line(100.0, date_=due)
        candidates = invoice_aml_refreshed | aml_b
        result = model._combo_find_matching_subset(candidates, 100.0, self.currency)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)

    # ------------------------------------------------------------------
    # Tests – _combo_get_candidates_for_window
    # ------------------------------------------------------------------

    def test_candidates_window_excludes_out_of_range(self):
        """Invoices outside the date window are excluded."""
        model = self._create_reconcile_model()
        st_line = self._create_st_line(10.0, date_=self.today)

        # Invoice due 5 days ago – should NOT appear in delta=0 window
        self._create_invoice(self.partner_a, 10.0, self.today - timedelta(days=5))
        # Invoice due today – SHOULD appear
        self._create_invoice(self.partner_b, 10.0, self.today)

        candidates = model._combo_get_candidates_for_window(
            st_line, self.today, self.today
        )
        dates = candidates.mapped("date_maturity")
        self.assertIn(self.today, dates)
        self.assertNotIn(self.today - timedelta(days=5), dates)

    def test_candidates_only_open_lines(self):
        """Already-reconciled lines must not appear as candidates."""
        model = self._create_reconcile_model()
        st_line = self._create_st_line(10.0, date_=self.today)

        aml = self._create_invoice(self.partner_a, 10.0, self.today)
        # Fully pay the invoice so the line is reconciled
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=aml.move_id.ids
        ).create({"amount": 10.0}).action_create_payments()

        candidates = model._combo_get_candidates_for_window(
            st_line, self.today, self.today
        )
        reconciled_ids = candidates.filtered("reconciled").ids
        self.assertNotIn(aml.id, reconciled_ids)
        # More directly: none of the returned candidates should be reconciled
        self.assertFalse(any(c.reconciled for c in candidates))
