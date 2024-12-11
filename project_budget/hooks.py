# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, api, _

def uninstall_hook(cr, registry):
    """ Restore initial menus """

    env = api.Environment(cr, SUPERUSER_ID, {})
    parent_id_ = env.ref('account.menu_finance_entries_accounting_miscellaneous').id
    env.ref('account_move_budget.account_move_budget_menu').write({
        'parent_id': parent_id_,
        'name': _('Account Move Budgets')
    })
    env.ref('project_budget_line_template.account_move_budget_line_template_menu').write({
        'parent_id': parent_id_,
    })
