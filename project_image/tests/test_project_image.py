# -*- coding: utf-8 -*-

from odoo import exceptions
from odoo.tests import common, Form

from odoo.addons.base.tests import test_image
import base64

class TestProjectImage(test_image.TestImage):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_project_image(self):
        project = self.env['project.project'].create({
            'name': 'Project test 1',
            'image_1920': base64.b64encode(self.img_1x1_png)
        })
        self.assertTrue(project.image_1024)
