# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, api, _

def uninstall_hook(cr, registry):
    """ Restore initial menus """

    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('account_move_budget.account_move_budget_menu').write({
        'parent_id': env.ref('account.menu_finance_entries_accounting_miscellaneous'),
        'name': _('Account Move Budgets')
    })
