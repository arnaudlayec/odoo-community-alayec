# -*- coding: utf-8 -*-

from odoo import Command, exceptions, fields
from odoo.tests.common import Form, TransactionCase

from datetime import timedelta

from odoo.addons.project_budget_line_template.tests.test_line_template import TestLineTemplate

class TestAccountMoveBudgetProject(TestLineTemplate):
    
    BUDGET_STANDARD = 100000.0
    BUDGET_FIX = 50.0
    UNIT_PRICE = 50.0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Project & budget
        cls.Project = cls.env['project.project']
        cls.project = cls.Project.create({
            'name': 'Project test',
            'date_start': '2022-01-01',
            'date': '2023-12-31'
        })
        
        cls.budget = cls.Budget.search([('project_id', '=', cls.project.id)])

        # Line
        vals = {
            'project_id': cls.project.id,
            'budget_id': cls.budget.id,
            'date': '2022-01-01',
            'account_id': cls.account.id,
        }
        cls.line_unit, cls.line_amount = cls.Line.create([
            vals | {
                'type': 'unit',
                'qty_debit': cls.BUDGET_FIX,
                'standard_price': cls.UNIT_PRICE,
                'analytic_account_id': cls.analytic.id,
            },
            vals | {
                'debit': cls.BUDGET_STANDARD,
                'analytic_account_id': cls.analytic2.id,
            }
        ])


    def test_01_code(self):
        # button
        self.project.button_open_budget_lines()
        self.project.budget_line_ids[1].button_open_budget_line_form()

    def test_02_project_budget_synchro(self):
        self.assertEqual(self.budget.name, self.project.display_name)
        
        self.project.date_start = '2021-01-01'
        self.assertEqual(self.budget.date_from, self.project.date_start)

    def test_03_line_credit(self):
        self.budget.line_ids._compute_debit_credit()
        print('line_unit', self.line_unit.read(['type', 'qty_debit', 'standard_price', 'debit', 'analytic_account_id']))
        self.assertEqual(self.line_unit.debit, self.BUDGET_FIX * self.UNIT_PRICE)
    
    def test_04_project_sum(self):
        """ Tests `budget_line_sum` (€) """
        self.budget.line_ids._compute_debit_credit()
        self.project._compute_budget_line_sum()
        self.assertEqual(self.project.budget_line_sum, self.BUDGET_STANDARD + self.BUDGET_FIX * self.UNIT_PRICE)

    def test_05_budget_templates(self):
        """ Test budget template & default-template-for-all-projects features """
        self.budget.template = True
        self.budget.template_default_project = True

        f = Form(self.Project)
        f.name = 'Project Test 2'
        project = f.save()
        self.assertTrue(project.budget_ids)
        self.assertTrue(project.budget_line_ids)




    # def test_08_security_access_rules(self):
    #     # Prepare user data set
    #     group_project_user = self.env.ref('project.group_project_user')
    #     group_account_user = self.env.ref('account.group_account_user')

    #     user_project = self.env['res.users'].create({'name': 'User Project 01', 'login': 'user_project_01'})
    #     group_project_user.users = [Command.link(user_project.id)]

    #     user_account = self.env['res.users'].create({'name': 'User Account 01', 'login': 'user_account_01'})
    #     group_account_user.users = [Command.link(user_account.id)]

    #     # Prepare 
    #     budget_global = self.budget.copy({
    #         'project_id': False,
    #         'line_ids': [Command.clear()],
    #         'date_from': fields.Date.today(),
    #         'date_to': fields.Date.today() + timedelta(days=1),
    #     })

    #     # Tests rights of user_project: should only see project-related budget
    #     try:
    #         self.budget.with_user(user_project).check_access("read")
    #     except:
    #         self.fail('Access of project user to project budget should be ok')
    #     with self.assertRaises(exceptions.AccessError):
    #         budget_global.with_user(user_project).check_access("read")
        
    #     # Tests rights of user_account: should see all budgets
    #     try:
    #         self.budget.with_user(user_account).check_access("read")
    #         budget_global.with_user(user_account).check_access("read")
    #     except:
    #         self.fail('Access of account user to any budget should be ok')
