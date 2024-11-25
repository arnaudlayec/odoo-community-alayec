# -*- coding: utf-8 -*-

from odoo import fields, exceptions, Command
from odoo.tests import common, Form

class TestProjectTaskTeamPlanning(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_01_type_role_affectation(self):
        """ Create a task: its default stage does not depend of the stage or task project """
        
        stage = self.env['project.task.type'].sudo().create({'name': 'Stage Test 1'})
        self.assertTrue(self.env['project.task']._get_default_stage_id())

        project = self.env['project.project'].create({
            'name': 'Project Test 1',
            'task_ids': [Command.create({'name': 'Task Test 1'})]
        })
        self.assertTrue(fields.first(project.task_ids).stage_id.id)
