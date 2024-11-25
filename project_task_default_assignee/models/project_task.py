# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command

class ProjectTask(models.Model):
    _inherit = ['project.task']

    user_ids = fields.Many2many(
        compute='_compute_user_ids',
        store=True,
        readonly=False
    )

    @api.depends('type_id')
    def _compute_user_ids(self):
        """ Auto-fill `user_ids` with users assigned to the role linked to the task through its type.
            Logic is:
             - `type_id` is chosen on the task
             - `type_id` may have a (single) role configured (Many2one)
             - users may be assigned to this role *on this project*
            => find those users and add them to the task
        """
        # can be called for 1 task outside of `onchange`
        project_ids_ = self.project_id.ids or [x.get('project_id') for x in vals_list]

        # Get user assignments on projects roles
        rg_result = self.env['project.assignment'].read_group(
            domain=[('project_id', 'in', project_ids_)],
            groupby=['project_id', 'role_id'],
            fields=['user_ids:array_agg(user_id)'],
            lazy=False
        )
        mapped_user_ids = {
            (x['project_id'][0], x['role_id'][0]): x['user_ids']
            for x in rg_result
        }

        for task in self:
            key = (task.project_id.id, task.type_id.role_id.id)
            user_ids = mapped_user_ids.get(key) # several users on 1 role
            if user_ids:
                task.user_ids = [Command.link(x) for x in user_ids]
