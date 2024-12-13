# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command

class ProjectDefaultMixin(models.AbstractModel):
    """ Add this mixin to your model (like Sale Orders) to add a required `project_id`
        field automatically filled-in if active user has only 1 project in favorites
    """
    _name = "project.default.mixin"
    _description = "Project Default"


    #===== Fields' methods =====#
    def _default_project_id_domain(self):
        """ Allow to select either:
            - projects in user's favorites, if any
            - else, all allowed projects 
        """
        Project = self.env['project.project']

        projects_all = Project.search(Project._get_domain_fav_projects(fav_only=False))
        projects_fav = projects_all.filtered_domain([('favorite_user_ids', '=', self.env.uid)])
        projects = projects_fav if projects_fav.ids else projects_all

        return [Command.link(x) for x in projects.ids]


    #===== Fields =====#
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
        required=True,
        ondelete='cascade',
        index='btree_not_null',
        default=lambda self: self._get_project_id(),
        domain="[('id', 'in', project_id_domain)]",
        help="Within your favorite projects"
    )
    project_id_domain = fields.One2many(
        comodel_name='project.project',
        default=_default_project_id_domain,
        compute='_compute_project_id_domain'
    )

    def _compute_project_id_domain(self):
        self.project_id_domain = self._default_project_id_domain()

    def _get_project_id(self, vals={}, record=False, raise_if_not_found=False, return_record=False):
        """ Try to get a `project_id_` from various possible source
            Useful in other situation than here, can be called like:
            `self.env['project.default.mixin']._get_project_id()`
            c.f. usage in `wizard/project_choice_wizard.py`

            :option vals:   can be provided as alternate data source to look for `project_id`
                            is set by default to `self._context`
            :option record: in this Mixin is not inherited, this method can be called in
                            standalone and `record` can be passed instead of `self`
        """
        record = record or self
        vals = self._context | vals

        project_id_ = (
            vals.get('project_id') # custom call
            or 'project_id' in record and record.project_id.id # when validating this wizard
            or vals.get('default_project_id') # 1/ passed from a form to an embedded tree view or 2/ custom (server action)
            or ( # on smart button click from a Project form
                vals.get('active_model') == 'project.project'
                and vals.get('active_id')
            )
            or self.env.user.favorite_project_id.id # works if single project
        )

        if not project_id_ and raise_if_not_found:
            raise exceptions.ValidationError(_(
                "Cannot do this action with no project selected."
                " Details: %s",
                self._context
            ))
        
        return (
            self.env['project.project'].sudo().browse(project_id_) if return_record
            else project_id_
        )