# Copyright 2026 Arnaud Layec <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Reconcile OCA - Amount Combo",
    "summary": (
        "Reconcile grouped bank transactions with multiple invoices "
        "by amount combination matching"
    ),
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "website": "https://github.com/OCA/account-reconcile",
    "author": "Your Name, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "account_reconcile_model_oca",
    ],
    "data": [
        "views/account_reconcile_model_views.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
    "maintainers": ["your_github_handle"],
}
