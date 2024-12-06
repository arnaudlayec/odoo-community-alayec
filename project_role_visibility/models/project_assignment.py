# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _, Command
from collections import defaultdict

class ProjectAssignment(models.Model):
    _inherit = "project.assignment"
    _order = "role_id DESC, primary DESC"

    #===== Fields =====#
    primary = fields.Boolean(
        string='Primary?',
        default=False,
        required=True,
    )
    role_id = fields.Many2one(
        ondelete='cascade'
    )
    # dynamic domain for `user_id`
    domain_user_ids = fields.One2many(
        'res.users',
        compute='_compute_domain_user_ids'
    )
    
    
    #===== Constrains for unique primary assignement per role & per project =====#
    def _get_other_primary_assignments(self):
        domain = [
            ('id', 'not in', self._origin.ids),
            ('primary', '=', True),
            ('project_id', 'in', self.project_id._origin.ids),
            ('role_id', 'in', self.role_id._origin.ids)
        ]
        return [(x.project_id.id, x.role_id.id) for x in self.search(domain)]
    def _primary_already_set(self, assignments_primary):
        """ For a given assignment, test if a `primary` assignment exists in its siblings """
        self.ensure_one()
        return (
            (self.project_id._origin.id, self.role_id._origin.id)
            in assignments_primary
        )
    @api.constrains("project_id", "role_id", "primary")
    def _restrict_unique_primary_role(self):
        """ Ensure unique `primary` assignation of same role within a project. In Python
            because PostgreSQL constrains does not support conditionnal UNIQUE constrain
        """
        assignments_primary = self._get_other_primary_assignments()
        for assignment in self:
            if assignment.primary and assignment._primary_already_set(assignments_primary):
                raise exceptions.ValidationError(
                    _("A primary assignment may be assigned only once per role within a project.")
                )
    @api.onchange('role_id')
    def _onchange_role_id(self):
        """ Suggest `primary` to True if this role is not already set as Primary on this project
            Very useful in assignation form
        """
        assignments_primary = self._get_other_primary_assignments()
        for assignment in self:
            assignment.primary = not assignment._primary_already_set(assignments_primary)
    

    #===== CRUD =====#
    @api.model_create_multi
    def create(self, vals_list):
        self._add_project_followers(vals_list)
        return super().create(vals_list)
    
    def write(self, vals):
        self._update_project_followers(vals)
        return super().write(vals)

    def unlink(self):
        # Remove followers *and after* unlink()
        self._remove_project_followers()
        super().unlink()
    
    #===== Synchro of assignees -> to followers =====
    def _should_synch(self, vals):
        """ Can be overriden to change logic on `primary` """
        return True # vals.get('primary')
    def _filter_has_access(self):
        return self # self.filtered('primary')
    
    def _add_project_followers(self, vals_list):
        """ Called by create(): add assignees to followers """
        # Get projects with privacy `followers` before loop on `vals_list`
        mapped_followers_ids = {
            vals['project_id']: []
            for vals in vals_list if vals.get('project_id')
        }
        Project = self.sudo().env['project.project']
        mapped_project_ids = {
            project.id: project
            for project in Project.browse(set(mapped_followers_ids.keys()))
            if project._should_synch_roles()
        }
        # Get a quick user->partner dict
        Users = self.sudo().env['res.users']
        mapped_partner_ids_ = {
            user.id: user.partner_id.id
            for user in Users.browse([
                vals.get('user_id') for vals in vals_list
            ])
        }
        
        # Compute new followers per project
        for vals in vals_list:
            project_id = mapped_project_ids.get(vals.get('project_id'))
            partner_id_ = mapped_partner_ids_.get(vals.get('user_id'))
            if self._should_synch(vals) and project_id and partner_id_:
                mapped_followers_ids[project_id.id].append(partner_id_)
        
        # Add project's subscription in bulk
        for project in list(mapped_project_ids.values()):
            partner_ids_ = mapped_followers_ids.get(project.id)
            if partner_ids_:
                project._message_subscribe(partner_ids_)

    def _update_project_followers(self, vals):
        pass

        # """ Called by write(): update followers on changes of `primary` """
        # if (
        #     'primary' in vals and vals.get('primary') != self.primary
        #     and self.project_id._should_synch_roles()
        # ):
        #     partner_ids_ = self.user_id.partner_id.ids
        #     if self._should_synch(vals): # moved to `primary`
        #         self.project_id._message_subscribe(partner_ids_)
        #     else: # `primary` unset
        #         self.project_id.with_context(unsubscribe_no_raise=True).message_unsubscribe(partner_ids_)
    
    def _remove_project_followers(self):
        """ Removes the follower object before role assignments """
        assignment_ids_to_clean = self._filter_has_access()
        project_ids_to_clean = assignment_ids_to_clean.project_id.filtered(lambda x: x._should_synch_roles())

        # Group assignment per project since `message_unsubscribe` is per project
        mapped_partner_ids = defaultdict(list)
        for assignment in assignment_ids_to_clean:
            project_followers = assignment.project_id.assignment_ids.user_id.partner_id
            if assignment.user_id.partner_id.id in project_followers.ids:
                mapped_partner_ids[assignment.project_id].append(assignment.user_id.partner_id.id)
        
        # Unsubscribe
        for project, partner_ids_ in mapped_partner_ids.items():
            project.with_context(unsubscribe_no_raise=True).message_unsubscribe(partner_ids_)

    #===== Compute of dynamic domain user for `user_id` =====#
    @api.depends('project_id', 'role_id')
    def _compute_domain_user_ids(self):
        """ When assigning new role, suggest only active users
            not already assigned on the same role (in the project)
        """
        Users = self.with_context(active_test=True).env['res.users']
        user_ids = Users.search([]).ids
        # Perf: get list of already assigned users, per `project_id`
        # and `role_id` outside loop on `self`
        mapped_assigned_user_ids = defaultdict(list)
        for x in self.project_id._origin.assignment_ids:
            mapped_assigned_user_ids[(x.project_id.id, x.role_id.id)].append(x.user_id.id)
        # Create list of assignable users for domain of `user_id`
        for assignment in self:
            assigned_user_ids = mapped_assigned_user_ids.get(
                (assignment.project_id._origin.id, assignment.role_id._origin.id), []
            )
            user_ids = (
                [uid for uid in user_ids if uid not in assigned_user_ids] +
                ([assignment.user_id._origin.id] if assignment.user_id._origin.id else [])
            )
            assignment.domain_user_ids = [Command.set(user_ids)]
