# -*- coding: utf-8 -*-

from odoo import exceptions
from odoo.tests import common

class TestProjectChildrenSequence(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        grp_manager = cls.env.ref('project.group_project_manager')
        User = cls.env['res.users'].with_context({'no_reset_password': True})
        cls.user_manager = User.create({
            'name': 'Test',
            'login': 'Test',
            'groups_id': [(6, 0, [grp_manager.id])]
        })

        cls.Project = cls.env['project.project'].with_context({'mail_create_nolog': True})
        cls.project_parent = cls.Project.create({})
        cls.project_parent_with_name = cls.Project.create({
            'name': 'Parent project'
        })
        cls.project_child = cls.Project.create({
            'parent_id': cls.project_parent.id,
        })
        cls.project_child_with_name = cls.Project.create({
            'name': 'Child project',
            'parent_id': cls.project_parent_with_name.id
        })

    def test_2level_hierarchy(self):
        """ Tests maximum of 2-levels hierarchy, i.e. a child project cannot also become a parent project """
        # A sub-project of sub-project should raise
        with self.assertRaises(exceptions.ValidationError):
            self.Project.create({'parent_id': self.project_child.id})

    def test_child_sequence(self):
        """ Test if child sequence is well created on parent project, and starts with parent's `sequence_code` """
        self.assertTrue(self.project_parent.children_sequence_id.id)
        self.assertTrue(
            self.project_child.sequence_code.startswith(self.project_parent.sequence_code)
        )

    # def test_child_display_name(self):
    #     """ Tests if :
    #         - `name` of child project is enforced to parent's name, when defined
    #         - elsewise, child's `display_name` is exactly child's `sequence_code`
    #     """
    #     self.assertEqual(self.project_child.display_name, self.project_child.sequence_code)
    #     self.assertEqual(self.project_child_with_name.name, self.project_parent_with_name.name)
