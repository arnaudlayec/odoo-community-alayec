# Copyright 2026 Arnaud Layec <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import itertools
import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    # ------------------------------------------------------------------
    # New fields
    # ------------------------------------------------------------------

    combo_amount_mode = fields.Boolean(
        string="Combo Amount-Mode",
        default=False,
        help=(
            "When enabled, this rule tries to find a combination of open "
            "invoices/bills whose residual amounts sum exactly matches the "
            "bank transaction amount.  No partner is required on the "
            "transaction: all open invoices of the company are searched.\n\n"
            "This mode is a last-resort rule and should be placed last in "
            "the reconciliation model sequence.  Automated validation is "
            "strongly discouraged."
        ),
    )

    combo_days_range = fields.Integer(
        string="Range of Days",
        default=0,
        help=(
            "Half-range (in days) around the bank transaction date used to "
            "filter candidate invoices/bills by their due date "
            "(date_maturity).\n"
            "• 0 → only invoices due exactly on the transaction date\n"
            "• 1 → transaction date −1 day … +1 day  (window of 3 days)\n"
            "• N → window of 1 + 2×N days\n\n"
            "The search starts with the narrowest window (day of the "
            "transaction) and widens by one day on each side until a "
            "matching combination is found or the maximum range is reached."
        ),
    )

    combo_max_invoices = fields.Integer(
        string="Maximum Number of Invoices/Bills to Look For",
        default=0,
        help=(
            "Maximum number of invoices/bills to include in a single "
            "combination.  0 (or empty) means no limit, but be aware that "
            "the search is exponential — always set a reasonable limit "
            "(recommended: 5–8)."
        ),
    )

    # ------------------------------------------------------------------
    # Constraints / onchange
    # ------------------------------------------------------------------

    @api.constrains("combo_amount_mode", "rule_type")
    def _check_combo_amount_mode_rule_type(self):
        for record in self:
            if record.combo_amount_mode and record.rule_type != "invoice_matching":
                raise models.ValidationError(
                    _(
                        "Combo Amount-Mode is only compatible with the "
                        "'Rule to match invoices/bills' rule type."
                    )
                )

    @api.onchange("combo_amount_mode")
    def _onchange_combo_amount_mode(self):
        """Reset fields that are incompatible with combo mode."""
        if self.combo_amount_mode:
            self.match_partner = False
            self.match_same_currency = False
            self.match_total_amount = False
            self.allow_payment_tolerance = False
            self.unique_matching = False

    # ------------------------------------------------------------------
    # Core algorithm – subset-sum search
    # ------------------------------------------------------------------

    def _combo_find_matching_subset(self, candidates, target_amount, currency):
        """
        Find the first subset of *candidates* whose sum of ``amount_residual``
        equals *target_amount* (within currency rounding).

        The search is ordered: subsets of size 1 are tried before size 2,
        etc., so the smallest matching combination is returned first.
        Within each size, candidates are iterated in the order they are
        provided (caller is responsible for ordering).

        :param candidates: recordset of ``account.move.line``
        :param float target_amount: absolute amount of the bank transaction
            (positive)
        :param res.currency currency: company currency used for rounding
        :returns: recordset of ``account.move.line`` (matching subset) or
            ``account.move.line`` empty recordset if not found
        """
        rounding = currency.rounding
        candidate_list = list(candidates)

        # Determine the maximum subset size to explore.
        max_size = len(candidate_list)
        if self.combo_max_invoices and self.combo_max_invoices < max_size:
            max_size = self.combo_max_invoices

        for size in range(1, max_size + 1):
            for combo in itertools.combinations(candidate_list, size):
                combo_sum = sum(
                    abs(line.amount_residual) for line in combo
                )
                if (
                    float_compare(
                        combo_sum, target_amount, precision_rounding=rounding
                    )
                    == 0
                ):
                    # Return as a recordset
                    return self.env["account.move.line"].browse(
                        [line.id for line in combo]
                    )
        return self.env["account.move.line"]

    def _combo_get_candidates_for_window(self, st_line, date_from, date_to):
        """
        Return open receivable/payable ``account.move.line`` records whose
        ``date_maturity`` falls within [date_from, date_to].

        Only lines belonging to the same company as the bank journal are
        returned.  Currency filtering is intentionally omitted (the caller
        works in company currency).

        :param account.bank.statement.line st_line: the bank transaction
        :param date date_from: start of the search window (inclusive)
        :param date date_to: end of the search window (inclusive)
        :returns: recordset of ``account.move.line``
        """
        domain = [
            ("company_id", "=", st_line.company_id.id),
            ("reconciled", "=", False),
            ("account_id.reconcile", "=", True),
            # Only customer invoices / vendor bills lines (receivable/payable)
            (
                "account_id.account_type",
                "in",
                ["asset_receivable", "liability_payable"],
            ),
            ("move_id.state", "=", "posted"),
            ("date_maturity", ">=", date_from),
            ("date_maturity", "<=", date_to),
            # Exclude lines already matched to this statement line
            ("statement_line_id", "=", False),
        ]
        return self.env["account.move.line"].search(
            domain, order="date_maturity asc, id asc"
        )

    def _combo_apply_rule(self, st_line):
        """
        Entry point for the combo-amount matching algorithm.

        Returns a dict compatible with the result expected by
        ``_get_invoice_matching_rule_result`` in ``account_reconcile_model_oca``,
        i.e.::

            {
                "amls": account.move.line recordset,
                "model": self,
                "status": "write_off" | "reconciled",
            }

        or ``None`` if no matching combination was found.

        :param account.bank.statement.line st_line: the bank transaction
        :returns: dict or None
        """
        # We work with the absolute residual amount of the statement line
        # expressed in the company currency.
        currency = st_line.company_id.currency_id
        target_amount = abs(st_line.amount)

        if float_compare(target_amount, 0.0, precision_rounding=currency.rounding) <= 0:
            _logger.debug(
                "combo_apply_rule: skipping line %s with non-positive amount",
                st_line.id,
            )
            return None

        transaction_date = st_line.date
        max_range = max(0, self.combo_days_range or 0)

        # Iterate from narrowest window outward
        for delta in range(0, max_range + 1):
            date_from = transaction_date - timedelta(days=delta)
            date_to = transaction_date + timedelta(days=delta)

            candidates = self._combo_get_candidates_for_window(
                st_line, date_from, date_to
            )

            if not candidates:
                continue

            matching_lines = self._combo_find_matching_subset(
                candidates, target_amount, currency
            )

            if matching_lines:
                _logger.info(
                    "combo_apply_rule: found %d matching invoice(s) for "
                    "statement line %s (delta=%d day(s))",
                    len(matching_lines),
                    st_line.id,
                    delta,
                )
                return {
                    "amls": matching_lines,
                    "model": self,
                    "status": "reconciled",
                }

        _logger.debug(
            "combo_apply_rule: no matching combination found for "
            "statement line %s",
            st_line.id,
        )
        return None

    # ------------------------------------------------------------------
    # Override of the invoice-matching rule dispatcher
    # ------------------------------------------------------------------

    def _get_invoice_matching_rule_result(self, st_line, partner, candidates):
        """
        Override to intercept calls when ``combo_amount_mode`` is enabled.

        When the flag is set, the standard invoice-matching logic is entirely
        bypassed and replaced by the combo-amount algorithm.  For all other
        models the parent implementation is called unchanged, ensuring zero
        impact on existing reconciliation rules.
        """
        # Guard: only intercept our own mode
        if not self.combo_amount_mode:
            return super()._get_invoice_matching_rule_result(
                st_line, partner, candidates
            )

        return self._combo_apply_rule(st_line)

    def _get_partner_from_mapping(self, st_line):
        """
        In combo mode we skip partner mapping entirely (no partner is
        expected on the transaction).
        """
        if self.combo_amount_mode:
            return self.env["res.partner"]
        return super()._get_partner_from_mapping(st_line)
