# -*- coding: utf-8 -*-

from odoo import fields, exceptions, Command
from odoo.tests.common import Form

from odoo.addons.analytic.tests.test_analytic_account import TestAnalyticAccount

class TestProjectTaskAnalyticType(TestAnalyticAccount):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test project
        Project = cls.env['project.project']
        cls.project = Project.create({
            'name': 'Project Test 01',
        })
        cls.Task = cls.env['project.task']

        # Configure type with analytic
        cls.type = cls.env['project.type'].create({
            'name': 'Type Test 01',
            'analytic_account_id': cls.analytic_account_1.id
        })


    def test_01_task_analytic_follows_type(self):
        """ Test if task analytic follows well type's analytic """
        # Create Task on the type
        task = self.Task.create({
            'project_id': self.project.id,
            'name': 'Test Task 01',
            'type_id': self.type.id
        })
        
        # Task analytic should move to type's
        self.assertEqual(task._get_task_analytic_account_id(), self.analytic_account_1)

        # Any change of the type should impact the task
        self.type.analytic_account_id = self.analytic_account_2
        self.assertEqual(task._get_task_analytic_account_id(), self.analytic_account_2)

    def test_02_task_skip_default(self):
        """ Don't set task analytic as type's one if another default analytic is asked """
        vals = {
            'project_id': self.project.id,
            'analytic_account_id': self.analytic_account_3.id # should be the prioritary
        }
        default_vals = (
            self.Task.with_context(default_type_id=self.type.id)
            ._set_default_analytic_per_type(vals)
        )

        # Ensure task follows other default rather than type's value
        self.assertEqual(default_vals.get('analytic_account_id'), self.analytic_account_3.id)
