# -*- coding: utf-8 -*-

from odoo import exceptions
from odoo.tests import common, Form

class TestProjectFavoriteSwitch(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.User = cls.env['res.users'].with_context({'no_reset_password': True})
        cls.user = cls.User.create({
            'name': 'Test',
            'login': 'Test',
            'email': 'user@test.com'
        })

        cls.Project = cls.env['project.project']

    def test_user_fav_project_id_shortcut(self):
        """ Test computation of `favorite_project_id` of `res.users` """
        project1 = self.Project.create({'name': 'Project1'})
        project2 = self.Project.create({'name': 'Project2'})

        # Add a 1st project: `favorite_project_id` is set
        project1.with_user(self.user).toggle_favorite()
        self.assertEqual(self.user.favorite_project_id, project1)

        # Add a 2nd project: `favorite_project_id` is False
        project2.with_user(self.user).toggle_favorite()
        self.assertFalse(self.user.favorite_project_id.id)

    def test_automated_fav_on_following(self):
        """ Test automated addition/removal of project in user's favorite
            when user's added/removed to/from project's Chatter followers
        """
        project = self.Project.create({'name': 'Project3'})

        # Subscribe: project is in user favorite
        project.message_subscribe(self.user.partner_id.ids)
        self.assertTrue(self.user in project.favorite_user_ids)

        # Unsubscribe: the inverse
        project.message_unsubscribe(self.user.partner_id.ids)
        self.assertTrue(self.user not in project.favorite_user_ids)


    def test_wizard_project_choice(self):
        """ Test the call to wizard (aiming to load a view on a specific project)
            1.1 With wizard explicit opening, project choice ; 1.2 and *then* redirection
            2.1 Test `project_id` guessing (from the user or context)
            2.2 With guessable project: immediat redirection
        """
        # new clean Project & User
        project = self.Project.create({'name': 'Project4'})
        user = self.User.create({'name': 'Test4', 'login': 'Test4'})
        Wizard = self.env['project.choice.wizard']

        # 1.1 Wizard with no guessable project: explicit opening
        res = Wizard.action_choose_project_and_redirect(action={})
        self.assertEqual(res.get('res_model'), 'project.choice.wizard')

        # 1.2 Project choice in wizard
        context_keys = ['test_project_id']
        action = lambda project_id: {'domain': "[('test','=',True)]"}
        Wizard = Wizard.with_context({'action': action, 'context_keys': context_keys})
        final_action = {
            # ensure of `context` and `domain` keys/parts 
            'context': {'test_project_id': project.id},
            'domain': ['&', ('test', '=', True), ('project_id', '=', project.id)]
        }

        f = Form(Wizard)
        f.project_id = project
        res = f.save().button_validate()
        self.assertEqual(res, final_action)
    
        # 2.1 Guess `project_id` by user's favorite
        Wizard = Wizard.with_context({}) # reset context
        project.with_user(user).toggle_favorite()
        Wizard = Wizard.with_user(user)
        self.assertEqual(Wizard._get_project_id(), project.id)

        # 2.2 Skip wizard opening if guessable
        res = Wizard.action_choose_project_and_redirect(action, context_keys)
        self.assertEqual(res, final_action)

    def test_task_default_project(self):
        # new clean Project & User as favorite
        project = self.Project.create({'name': 'Project5'})
        user = self.User.create({'name': 'Test5', 'login': 'Test5'})
        project.with_user(user).toggle_favorite()

        # new task by user: project should be pre-selected
        task = self.env['project.task'].with_user(user).create({'name': 'Task Test 1'})
        self.assertEqual(task.project_id, project)
