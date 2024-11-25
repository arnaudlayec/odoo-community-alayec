# -*- coding: utf-8 -*-

from odoo import exceptions, Command
from odoo.tests import common, Form

from odoo.addons.base.tests import test_ir_attachment
import base64

class TestProjectImage(test_ir_attachment.TestIrAttachment):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_task_attachment(self):
        project = self.env['project.project'].create({'name': 'Project test 1'})
        task = self.env['project.task'].create({
            'name': 'Task Test 1',
            'project_id': project.id,
            'attachment_ids': [Command.create({'name': 'a1', 'raw': self.blob1})]
        })
        self.assertTrue(task.attachment_ids.ids)
