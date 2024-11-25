# -*- coding: utf-8 -*-

from odoo import Command, exceptions, fields

from odoo.tests.common import Form, TransactionCase
from odoo.addons.account_move_budget.tests.test_account_move_budget import TestAccountMoveBudget

class TestAccountMoveBudgetProject(TestAccountMoveBudget):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.Project = cls.env['project.project']
        cls.project = cls.Project.create({
            'name': 'Project test',
            'date_start': '2022-01-01',
            'date': '2023-12-31'
        })
        
        Budget = cls.env['account.move.budget']
        cls.budget = Budget.search([('project_id', '=', cls.project.id)])

        # Attribute, ProductTemplate, ProductVariant
        ProductAttribute = cls.env['product.attribute']
        cls.attribute = ProductAttribute.create({
            'name': 'Year test',
            'values_date_ranged': True,
            'value_ids': [Command.create({'name': y, 'date_from': y + '-01-01'}) for y in ['2022', '2023']]
        })
        ProductTemplate = cls.env['product.template']
        # fix value
        cls.product_tmpl_fix = ProductTemplate.create({
            'name': 'Fix value test',
            'uom_id': cls.env.ref('uom.product_uom_hour').id,
            'uom_po_id': cls.env.ref('uom.product_uom_hour').id
        })
        # date-ranged values
        cls.product_tmpl_daterange = ProductTemplate.create({
            'name': 'Service test',
            'type': 'service',
            'uom_id': cls.env.ref('uom.product_uom_hour').id,
            'uom_po_id': cls.env.ref('uom.product_uom_hour').id,
            'attribute_line_ids': [Command.create({
                'attribute_id': cls.attribute.id,
                'value_ids': [Command.set(cls.attribute.value_ids.ids)],
            })]
        })
        cls.product2022, cls.product2023 = cls.product_tmpl_daterange.product_variant_ids
        cls.product2022.standard_price = 450
        cls.product2023.standard_price = 700

        # Analytic Account
        AnalyticPlan = cls.env['account.analytic.plan']
        AnalyticAccount = cls.env['account.analytic.account']
        cls.analytic = AnalyticAccount.create({
            'name': 'Analytic Account test',
            'plan_id': AnalyticPlan.create({'name': 'Analytic Plan test'}).id,
            'product_tmpl_id': cls.product_tmpl_fix.id
        })

        Line = cls.env['account.move.budget.line']
        cls.lines = {
            'standard': Line.create({
                'project_id': cls.project.id,
                'budget_id': cls.budget.id,
                'debit': 100000,
                'date': '2022-01-01',
                'account_id': cls.account.id,
            }),
            'fix': Line.create({
                'project_id': cls.project.id,
                'budget_id': cls.budget.id,
                'type': 'fix',
                'analytic_account_id': cls.analytic.id, # test product default via analytic
                'qty_debit': 50,
                'standard_price': 50,
                'date': '2022-01-01',
                'account_id': cls.account.id,
            }),
            'date_range': Line.create({
                'project_id': cls.project.id,
                'budget_id': cls.budget.id,
                'type': 'date_range',
                'product_tmpl_id': cls.product_tmpl_daterange.id,
                'qty_debit': 300,
                'date': '2022-01-01',
                'account_id': cls.account.id,
            })
        }


    def test_01_code(self):
        # button
        self.project.button_open_budget_lines()
        self.project.budget_line_ids[1].button_open_budget_line_form()
        self.product2022.button_open_attributes()

    def test_02_project_budget_synchro(self):
        self.assertEqual(self.budget.name, self.project.display_name)
        
        self.project.date_start = '2021-01-01'
        self.assertEqual(self.budget.date_from, self.project.date_start)

    def test_03_a_default_product_tmpl(self):
        """ Default product_tmpl on budget lines from analytic account """
        self.assertEqual(self.lines['fix'].product_tmpl_id, self.analytic.product_tmpl_id)
        self.assertEqual(self.lines['date_range'].product_tmpl_id, self.product_tmpl_daterange)

    def test_04_product_variant(self):
        # prefill of `date_from`, from product's attributes value
        self.assertEqual(str(self.product2022.date_from), '2022-01-01')

        # right display of `date_from` and `date_to` in the form
        self.assertEqual(self.product2022.standard_price_date_ranged, True)

        # date to
        self.assertEqual(str(self.product2022.date_to), '2022-12-31')
        self.assertEqual(self.product2023.date_to, False)

        # constrain: can't change type or uom if budget
        with self.assertRaises(exceptions.ValidationError):
            self.product_tmpl_daterange.type = 'consu'

    def test_05_line_credit(self):
        self.budget.line_ids._compute_debit_credit()
        self.assertEqual(self.lines['fix'].debit, 50*50)
        self.assertEqual(self.lines['date_range'].debit, 300/2*450 + 300/2*700)
    
    def _get_total_budget(self):
        return 100000 + 50*50 + (300/2 * 450 + 300/2 * 700)
    def test_06_project_sum(self):
        """ Tests `budget_line_sum` (€) and `allocated_hours` (hours) """
        self.budget.line_ids._compute_debit_credit()

        # Total in € (sum each types: standard, fix, date_range)
        self.project._compute_budget_line_sum()
        self.assertEqual(self.project.budget_line_sum, self._get_total_budget())

        # Total in H
        total_hour = 50 + 300
        self.project._compute_allocated_hours()
        self.assertEqual(self.project.allocated_hours, total_hour)

    def test_07_budget_templates(self):
        """ Test budget template & default-template-for-all-projects features """
        self.budget.template = True
        self.budget.template_default_project = True

        f = Form(self.Project)
        f.name = 'Project Test 2'
        project = f.save()
        self.assertTrue(project.budget_ids)
        self.assertTrue(project.budget_line_ids)
