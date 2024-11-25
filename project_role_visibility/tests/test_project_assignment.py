# -*- coding: utf-8 -*-

from odoo import exceptions
from odoo.tests import common

class TestProjectAssignment(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Users = cls.env['res.users'].with_context({'no_reset_password': True})
        cls.user1 = Users.create({'name': 'User1', 'login': 'User1'})
        cls.user2 = Users.create({'name': 'User2', 'login': 'User2'})

        Project = cls.env['project.project'].with_context({'mail_create_nolog': True})
        cls.project = Project.create({'name': 'Project'})

        Role = cls.env['project.role']
        cls.role = Role.create({'name': 'Role'})

        # Create base assignments of `user1` and `user2` on the project & role 
        cls.Assignment = cls.env['project.assignment']
        cls.assignment1 = cls.Assignment.create({
            'user_id': cls.user1.id,
            'project_id': cls.project.id,
            'role_id': cls.role.id
        })
        cls.assignment2 = cls.Assignment.create({
            'user_id': cls.user2.id,
            'project_id': cls.project.id,
            'role_id': cls.role.id
        })

    def test_primary_assignation(self):
        """ Test:
            - constrain preventing the same role being assigned twice as `primary`
            - `primary` default value computed by `_onchange_role_id()`
        """
        # Test default value computation
        self.assignment1._onchange_role_id()
        self.assertTrue(self.assignment1.primary) # first one takes `primary=True`
        self.assignment2._onchange_role_id()
        self.assertFalse(self.assignment2.primary) # 2nd one stays with `primary=False`

        # Test constrain: should raise
        with self.assertRaises(exceptions.ValidationError):
            self.assignment2.write({'primary': True})

    def test_domain_user_ids(self):
        """ Tests if already assigned users are not suggested again """
        self.assertTrue(self.user1.id not in self.assignment2.domain_user_ids.ids)
