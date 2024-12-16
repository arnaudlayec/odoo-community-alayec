# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class ProjectType(models.Model):
    _inherit = ['project.type']

    role_id = fields.Many2one(
        comodel_name='project.role',
        string='Role',
        compute='_compute_role_id',
        store=True,
        readonly=False,
        recursive=True,
        help="Tasks affected to this type will be auto-assigned to users carrying"
             " this role in the project. If not configured, assignees of this task's"
             " type are not modified."
    )
    computed_role_id = fields.Many2one(
        comodel_name='project.role',
        string='Role in parents',
        compute='_compute_computed_role_id'
    )

    #===== Constrain =====#
    @api.constrains('role_id')
    def _constrain_role_only_parent(self):
        """ If a role is set on a parent, can't customize it """
        for type in self:
            if type.computed_role_id.id and type.role_id != type.computed_role_id:
                raise exceptions.ValidationError(
                    _("A role is already set on this type's parent: modify it instead.")
                )

    #===== Onchange & compute =====#
    @api.onchange('role_id')
    def _propagate_role_id(self):
        """ If role is changed on a parent, propagate it to childs """
        for type in self:
            type.child_ids.role_id = type.role_id
    @api.depends('parent_id', 'parent_id.role_id')
    def _compute_role_id(self):
        """ If parent is changed, try to get its role (if any) """
        for type in self:
            type.role_id = type.computed_role_id

    @api.depends('parent_id', 'parent_id.role_id')
    def _compute_computed_role_id(self):
        """ Find 1st role found in parents, recursively (if any) """
        for type in self:
            parent_id = type.parent_id
            computed_role_id = parent_id.role_id
            while parent_id.id and not computed_role_id.id:
                parent_id = parent_id.parent_id
                computed_role_id = parent_id.role_id
            type.computed_role_id = computed_role_id
