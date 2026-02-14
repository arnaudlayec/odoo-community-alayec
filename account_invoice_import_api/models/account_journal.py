# -*- coding: utf-8 -*-

from odoo import models

class AccountJournal(models.Model):
    _inherit = ['account.journal']

    def _auto_reconcile(self):
        lines = self.env['account.bank.statement.line'].search([
            ('journal_id', 'in', self.ids),
            ('is_reconciled', '=', False),
        ])
        lines._auto_reconcile()
