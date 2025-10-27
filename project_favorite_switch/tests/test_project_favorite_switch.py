# -*- coding: utf-8 -*-

from odoo import exceptions
from odoo.tests import common, Form
from odoo.tools.safe_eval import safe_eval

class TestProjectFavoriteSwitch(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    @classmethod
    def _create_user_and_projects(cls):
        cls.User = cls.env['res.users'].with_context({'no_reset_password': True})
        cls.Project = cls.env['project.project']

        # clean if need to reset
        cls.User.search([('name', '=', 'Test')]).unlink()
        cls.Project.search([('name', 'like', 'Test')]).unlink()
        
        # create
        cls.user = cls.User.create({
            'name': 'Test',
            'login': 'Test',
            'email': 'user@test.com'
        })
        cls.project1 = cls.Project.create({'name': 'Project Test 1'})
        cls.project2 = cls.Project.create({'name': 'Project Test 2'})

    #===== res.users =====#
    def test_01_user_fav_project_id_shortcut(self):
        """ Test computation of `favorite_project_id` of `res.users` """
        self._create_user_and_projects()

        # Add a 1st project: `favorite_project_id` is set
        self.project1.with_user(self.user).toggle_favorite()
        self.assertEqual(self.user.favorite_project_id, self.project1)

        # Add a 2nd project: `favorite_project_id` is False
        self.project2.with_user(self.user).toggle_favorite()
        self.assertFalse(self.user.favorite_project_id.id)

    def test_02_automated_fav_on_following(self):
        """ Test automated addition/removal of project in user's favorite
            when user's added/removed to/from project's Chatter followers
        """
        self._create_user_and_projects()

        # Subscribe: project is in user favorite
        self.project1.message_subscribe(self.user.partner_id.ids)
        self.assertTrue(self.user in self.project1.favorite_user_ids)

        # Unsubscribe: the inverse
        self.project1.message_unsubscribe(self.user.partner_id.ids)
        self.assertTrue(self.user not in self.project1.favorite_user_ids)


    #===== project.choice.wizard =====#
    def test_03_wizard_project_choice(self):
        """ Test the call to wizard (aiming to load a view on a specific project)
            1.1 With wizard explicit opening, project choice ; 1.2 and *then* redirection
            2.1 Test `project_id` guessing (from the user or context)
            2.2 With guessable project: immediat redirection
        """
        self._create_user_and_projects()

        # 1.1 Wizard with no guessable project: explicit opening
        Wizard = self.env['project.choice.wizard']
        action = Wizard.action_choose_project_and_redirect(action_arg={})
        self.assertEqual(action.get('res_model'), 'project.choice.wizard')

        # 1.2 Project choice in wizard
        action_arg = 'project.action_view_task'
        context_keys = ['test_project_id']
        Wizard = Wizard.with_context({'action_arg': action_arg, 'context_keys': context_keys})
        f = Form(Wizard)
        f.project_id = self.project1
        action = f.save().button_validate()
        # ensure of `context` and `domain` keys/parts
        self.assertEqual(action.get('res_model'), 'project.task')
        self.assertEqual(action.get('context', {}).get('test_project_id'), self.project1.id)
        self.assertTrue(('project_id', '=', self.project1.id) in action.get('domain'))
    
        # 2.1 Guess `project_id` by user's favorite
        Wizard = Wizard.with_context({}).with_user(self.user) # reset context
        self.project1.with_user(self.user).toggle_favorite()
        self.assertEqual(Wizard._get_project_id(), self.project1.id)

        # 2.2 Skip wizard opening if guessable
        # and ensure opened views can use `default_project_id` by default (like to hide some filters in <searchpanel>)
        action = Wizard.action_choose_project_and_redirect(action_arg)
        self.assertEqual(action.get('target'), 'main') # clear breacrumbs on newly open page
        self.assertEqual(action.get('context', {}).get('default_project_id'), self.project1.id)
    
    def test_04_task_default_project(self):
        # new clean Project & User as favorite
        self._create_user_and_projects()
        self.project1.with_user(self.user).toggle_favorite()

        # new task by user: project should be pre-selected
        task = self.env['project.task'].with_user(self.user).create({'name': 'Task Test 1'})
        self.assertEqual(task.project_id, self.project1)
