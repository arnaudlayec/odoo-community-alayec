# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)

def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})

    _migrate_analytic_lines(env)

def _migrate_analytic_lines(env):
    _logger.info("""
        `_compute` in `analytic_account_id` is removed =>
            - migrate analytic lines in dedicated lines
            - set to False `analytic_account_id`
    """)

    histories = env['hr.employee.timesheet.cost.history'].search([('analytic_account_id', '!=', False)])
    fields = [x for x in histories._get_fields_related() if x != 'analytic_account_id']
    for history in histories:
        # copy the line only with the analytic
        defined = [field for field in fields if history[field]]
        vals = {field: False for field in defined}
        history.copy(vals)

        # remove the analytic_account_id
        history.analytic_account_id = False
