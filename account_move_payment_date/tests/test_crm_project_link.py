# -*- coding: utf-8 -*-

from odoo import exceptions
from odoo.tests import common

class TestProjectContact(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.lead = cls.env['crm.lead'].create({'name': 'Lead'})

    def test_convert_opportunity_to_project(self):
        """ Test creation of project from an opportunity """
        self.lead.action_create_project()
        self.assertTrue(self.lead.project_id.id != False)
    
    def test_link_opportunity_from_project(self):
        """ Test mirroring of M2o field between `project.project` and `crm.lead` """
        project = self.env['project.project'].create({'name': 'Project'})
        # Link
        project.opportunity_id = self.lead
        self.assertEqual(self.lead.project_id.id, project.id)
        # Unlink
        project.opportunity_id = False
        self.assertEqual(self.lead.project_id.id, False)
