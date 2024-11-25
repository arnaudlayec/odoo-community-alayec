# -*- coding: utf-8 -*-

from odoo import exceptions, Command
from odoo.tests import common, Form

class TestProjectVisibility(common.TransactionCase):
    """ Test only the synchro between `assignment_ids.user_ids` and `message_partner_ids`,
        not the whole Project access rules (already tested in Odoo)
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Project = cls.env['project.project'].with_context({'mail_create_nolog': True})
        cls.project = cls.Project.create({
            'name': 'Project',
            'privacy_visibility': 'followers'
        })
        
        Role = cls.env['project.role']
        cls.role = Role.create({'name': 'Role'})

        cls.grp_user = cls.env.ref('project.group_project_user')
        cls.User = cls.env['res.users'].with_context({'no_reset_password': True})
        cls.user = cls.User.create({
            'name': 'User',
            'login': 'User',
            'email': 'user@test.com',
            'groups_id': [Command.set([cls.grp_user.id])]
        })

        Assignment = cls.env['project.assignment']
        cls.assignment = Assignment.create({
            'project_id': cls.project.id,
            'role_id': cls.role.id,
            'user_id': cls.user.id,
            'primary': True,
        })

    def test_synch_assignees_to_followers(self):
        """ Test if synch. logic ensures well that followers are at
            least a subset of users assigned with primary roles
        """
        # User assigned with primary role: should be in followers
        self.assertTrue(self.user.partner_id.id in self.project.message_partner_ids.ids)
        # User unassigned from a role: it should by removed from followers
        self.assignment.unlink()
        self.assertFalse(self.user.partner_id.id in self.project.message_partner_ids.ids)
    
    def test_followers_update(self):
        """ Test if:
            - adding external partner (i.e. not internal user) is ok
            - a user still assigned to a primary role cannot unfollow
            - an internal user with no assignment of primary role cannot follow
        """
        # Adding external partner should be ok
        Partner = self.env['res.partner']
        partner = Partner.create({
            'name': 'Partner',
            'email': 'partner@test.com'
        })
        try:
            self.project.message_subscribe(partner.ids)
        except:
            self.fail("External partner should be able to subscribe")

        # Cannot unfollow a user assigned with primary role (should raise)
        with self.assertRaises(exceptions.ValidationError):
            self.project.message_unsubscribe(self.user.partner_id.ids)
        
        # Cannot add user with no primary role (should raise too)
        user2 = self.User.create({
            'name': 'User2',
            'login': 'User2',
            'email': 'user2@test.com',
            'groups_id': [Command.set([self.grp_user.id])]
        })
        with self.assertRaises(exceptions.ValidationError):
            self.project.message_subscribe(user2.partner_id.ids)

    def test_project_privacy_change(self):
        """ Test if existings roles are well synched to followers if
            project's privacy changes after role assignments
        """
        project2 = self.Project.create({
            'name': 'Project2',
            'privacy_visibility': 'portal'
        })
        # Assign `user` to a primary role on `project2` before
        # `project2` is set to privacy `followers`
        assignment2 = self.assignment.copy({'project_id': project2.id})
        project2.privacy_visibility = 'followers'
        # `user` should be in followers
        self.assertTrue(self.user.partner_id.id in project2.message_partner_ids.ids)

    def test_global_user(self):
        """ Test if Global Users see all tasks & projects no matter its roles/subscriptions """
        # Set user as Global User
        grp_user_global = self.env.ref('project_role_visibility.group_project_user_global')
        self.user.groups_id = [Command.set([grp_user_global.id])]
        # Create an empty project, restricted in visibility (`followers`)
        project2 = self.Project.create({
            'name': 'Project2',
            'privacy_visibility': 'followers'
        })
        # The user should have visibility on it
        try:
            project2.with_user(self.user).check_access_rights('read')
            project2.with_user(self.user).check_access_rule('read')
        except exceptions.AccessError:
            self.fail("User (Global) should have access to all projects & tasks")
