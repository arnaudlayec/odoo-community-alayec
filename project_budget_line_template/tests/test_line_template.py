# -*- coding: utf-8 -*-

from odoo import Command, exceptions, fields
from odoo.tests.common import Form, TransactionCase

from odoo.addons.account_move_budget.tests.test_account_move_budget import TestAccountMoveBudget

class TestLineTemplate(TestAccountMoveBudget):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Budget
        cls.Budget = cls.env['account.move.budget']
        cls.budget_no_project = cls.Budget.create({
            'name': 'Test Budget 01',
            'date_from': '2022-01-01',
            'date_to': '2022-01-01',
        })

        # Analytic
        AnalyticPlan = cls.env['account.analytic.plan']
        AnalyticAccount = cls.env['account.analytic.account']
        cls.analytic = AnalyticAccount.create({
            'name': 'Analytic Account test',
            'plan_id': AnalyticPlan.create({'name': 'Analytic Plan test'}).id,
        })
        cls.analytic2 = cls.analytic.copy({'name': 'Analyic Account Test 02'})

        # Template & line
        cls.Line = cls.env['account.move.budget.line']
        cls.TemplateLine = cls.env['account.move.budget.line.template']
        cls.template1, _, cls.template2 = cls.TemplateLine.create([{
            'sequence': 1,
            'name': 'Template Test 01',
            'analytic_account_id': cls.analytic.id,
            'account_id': cls.account.id,
        }, {
            'sequence': 2,
            'name': 'Should be ignored',
            'analytic_account_id': cls.analytic.id,
        }, {
            'sequence': 3,
            'name': 'Template Test 02',
            'analytic_account_id': cls.analytic2.id,
            'account_id': cls.account.id,
            'partner_id': cls.env.user.partner_id.id,
        }])


    def _create_new_line(self, default=False):
        """ Don't provide `account_id` should be guessed template line
            (`account_id` is required in `account.move.budget.line`)
        """
        Line = self.Line.with_context(default_analytic_account_id=default and self.analytic.id)
        try:
            f = Form(Line)
            f.budget_id = self.budget_no_project
            f.date = '2022-01-01'
            if not default:
                f.analytic_account_id = self.analytic
            new_line = f.save()
        except:
            self.fail('account_id should have been guessed as default via template budget line')
        
        return new_line

    def test_01_create(self):
        """ Ensure fields templating works at creation, with `create` """
        # new line
        new_line = self._create_new_line()

        # template1 should have been used, which only sets name and account_id
        self.assertEqual(new_line.name, self.template1.name)
        self.assertFalse(new_line.partner_id)
    
    def test_02_default(self):
        """ Ensure fields templating works at creation, with `default` """
        # new line
        new_line = self._create_new_line(default=True)

        # template1 should have been used, which only sets name and account_id
        self.assertEqual(new_line.name, self.template1.name)
        self.assertFalse(new_line.partner_id)
    
    def test_03_onchange(self):
        """ Test `onchange` and filling of only yet empty field """
        new_line = self._create_new_line() # create line on analytic(1)
        with Form(new_line) as f:
            f.analytic_account_id = self.analytic2 # change to analytic2, with a template line defining the partner
        
        # `partner` should have been set, but `name` should not have been overwritten
        self.assertEqual(new_line.name, self.template1.name)
        self.assertEqual(new_line.partner_id, self.template2.partner_id)
