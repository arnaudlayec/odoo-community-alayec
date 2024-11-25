# -*- coding: utf-8 -*-

from odoo import exceptions
from odoo.tests import common, Form

from odoo.addons.project_type.tests.test_project_type import TestProjectType

class TestProjectTaskDefaultAssignee(TestProjectType):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # project
        cls.project = cls.env['project.project'].create({"name": "Project test 1"})
        
        # role
        cls.role = cls.env['project.role'].create({"name": "Parent Role Test 1"})
        cls.role2 = cls.role.copy({"name": "Children Role Test"})
        
        # user
        cls.user = cls.env['res.users'].create({
            "name": "User",
            "login": "user",
        })


    def test_01_type_role_affectation(self):
        """ Test:
            0. children types can have a role only if none on parent
            1. role configured on a parent type descends to its children
            2. children types cannot have role different to their parent's
        """
        # 0. even with a parent (with no role), a child type can have its own role
        self.cat2.parent_id = self.cat
        try:
            with Form(self.cat2) as f_cat2:
                f_cat2.role_id = self.role2
        except:
            self.fail("Should be OK to affect a role to children if none on parent")

        # 1. role of children type should move to its parent role
        with Form(self.cat) as f_cat:
            f_cat.role_id = self.role
        self.assertEqual(self.cat2.role_id, self.cat.role_id)
        # on change of parent, if should take new parent's role
        role_other_parent = self.env["project.role"].create({"name": "Parent Role Test 2"})
        cat_other_parent = self.env["project.type"].create({
            "name": "Other Parent test 2",
            "role_id": role_other_parent.id
        })
        with Form(self.cat2) as f_cat2: # change the parent
            f_cat2.parent_id = cat_other_parent
        self.assertEqual(self.cat2.computed_role_id, role_other_parent)
        self.assertEqual(self.cat2.role_id, role_other_parent)

        # 2. cannot change the role of children now it is set by the parent
        with self.assertRaises(exceptions.ValidationError):
            self.cat2.role_id = self.role2


    def test_02_task_assignees_per_role_and_type(self):
        """ Test user auto-assignation to task as per task' type, type's role and user's role """
        self.cat.role_id = self.role
        self.env['project.assignment'].create({
            "project_id": self.project.id,
            "role_id": self.role.id,
            "user_id": self.user.id,
        })

        f = Form(self.env['project.task'])
        f.name = 'Test Task 1'
        f.project_id = self.project
        f.type_id = self.cat
        task = f.save()

        # user should be assigned to the task via its role
        self.assertTrue(self.user.id in task.user_ids.ids)
