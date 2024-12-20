# -*- coding: utf-8 -*-

from odoo import fields, exceptions, Command
from odoo.tests import common, Form

class TestProjectTaskCopy(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Project = cls.env['project.project']
        cls.project1 = Project.create({
            'name': 'Project test 1',
            'task_ids': [Command.create({'name': 'Task Test 1'})]
        })
        cls.project2 = cls.project1.copy({'name': 'Project test 2'})

    def test_01_project_task_copy_unitary(self):
        """ Create a new task in project2 from project1's task """
        Task = self.env['project.task']
        f = Form(Task)
        f.project_id = self.project2
        f.copy_project_id = self.project1
        f.copy_task_id = fields.first(self.project1.task_ids)
        task2 = f.save()

        self.assertTrue(
            self.project2.task_ids.mapped('name'),
            self.project1.task_ids.mapped('name')
        )

    def test_02_project_task_copy_bulk(self):
        """ Test to copy all tasks of `project1` to `project2` """
        count_before = len(self.project2.task_ids.ids)
        
        f = Form(self.env['project.task.copy.wizard']
            .with_context(active_ids=self.project1.task_ids.ids)
        )
        f.project_id = self.project2
        wizard = f.save()
        
        wizard.button_copy()
        self.assertEqual(
            len(self.project2.task_ids.ids),
            len(self.project1.task_ids.ids) + count_before
        )
