# -*- coding: utf-8 -*-

from odoo import exceptions, Command, fields
from odoo.tests import common, Form

class TestProjectContact(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Partner = cls.env['res.partner']
        cls.partner = Partner.create({'name': 'Partner'})

        Project = cls.env['project.project'].with_context({'mail_create_nolog': True})
        cls.project = Project.create({'name': 'Project'})

        ResPartnerCategory = cls.env['res.partner.category']
        cls.category1 = ResPartnerCategory.create({'name': 'Architect'})
        cls.category2 = ResPartnerCategory.create({'name': 'Subcontractor'})

    def test_category_prefill(self):
        """ Test if code to prefill category as per partner's one is ok """
        self.partner.category_id = [Command.set([self.category1.id, self.category2.id])]
        with Form(self.project) as ProjectForm:
            with ProjectForm.contact_ids.new() as contact: # see Odoo's testing doc on O2m
                contact.partner_id = self.partner
        contact = fields.first(self.project.contact_ids)
        self.assertEqual(contact.category_id, fields.first(self.partner.category_id))
    
    def test_partner_project_count(self):
        """ Test good count of a partner's related projects """
        # Assign `partner` as project's client
        self.project.partner_id = self.partner
        # Assign `partner` as contact with several function in the project
        self.env['project.contact'].create([{
            'partner_id': self.partner.id,
            'project_id': self.project.id,
            'category_id': self.category2.id
        }])
        # `partner` has only 1 related project 
        self.assertEqual(1, self.partner.project_count)
    
    def test_action_open_project_by_partner(self):
        # test code of `action_open_project_by_partner`
        self.partner.action_open_project_by_partner() 

