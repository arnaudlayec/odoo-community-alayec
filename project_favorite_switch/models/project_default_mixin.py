# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectDefaultMixin(models.AbstractModel):
    """ Add this mixin to your model (like Sale Orders) to add a required `project_id`
        field automatically filled-in if active user has only 1 project in favorites
    """
    _name = "project.default.mixin"
    _description = "Project Default"

    def _get_project_id(self, vals={}):
        """ Try to get a `project_id_` from various possible source
            Useful in other situation than here, can be called like:
            `self.env['project.default.mixin']._get_project_id()`
            c.f. usage in `wizard/project_choice_wizard.py`
        """
        return (
            vals.get('project_id') # custom call
            or 'project_id' in self and self.project_id.id # when validating this wizard
            or self._context.get('default_project_id') # 1/ passed from a form to an embedded tree view or 2/ custom (server action)
            or ( # on smart button click from a Project form
                self._context.get('active_model') == 'project.project'
                and self._context.get('active_id')
            )
            or self.env.user.favorite_project_id.id # works if single project
        )
    
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        ondelete='cascade',
        index='btree_not_null',
        default=_get_project_id,
        domain="[('favorite_user_ids', '=', uid)]",
        help="Within your favorite projects"
    )
    