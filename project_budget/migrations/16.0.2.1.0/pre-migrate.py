# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)

def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})

    _migrate_analytic_account_column(cr, version)


def _migrate_analytic_account_column(cr, version):
    _logger.info("[Migration] Remove from `account_analytic_account` the column `is_project_budget`")
    cr.execute("""
        ALTER TABLE account_analytic_account
                DROP COLUMN IF EXISTS is_project_budget CASCADE;
    """)
    cr.execute("""
        DELETE FROM ir_ui_view WHERE arch_db->>'fr_FR' LIKE '%%analytic_budget_plan_id%';
    """)
