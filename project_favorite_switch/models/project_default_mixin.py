# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class ProjectDefaultMixin(models.AbstractModel):
    """ Add this mixin to your model (like Sale Orders) to add a required `project_id`
        field automatically filled-in if active user has only 1 project in favorites
    """
    _name = "project.default.mixin"
    _description = "Project Default"
    
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        ondelete='cascade',
        index='btree_not_null',
        default=lambda self: self._get_project_id(),
        domain=lambda self: [
            ('favorite_user_ids', '=', self.env.uid),
            ('stage_id.fold', '=', False)
        ],
        help="Within your favorite projects"
    )
    

    def _get_project_id(self, vals={}, record=False, raise_if_not_found=False):
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
        vals = vals or self._context

        project_id_ = (
            vals.get('project_id') # custom call
            or 'project_id' in record and record.project_id.id # when validating this wizard
            or record._context.get('default_project_id') # 1/ passed from a form to an embedded tree view or 2/ custom (server action)
            or ( # on smart button click from a Project form
                record._context.get('active_model') == 'project.project'
                and record._context.get('active_id')
            )
            or record.env.user.favorite_project_id.id # works if single project
        )

        if not project_id_ and raise_if_not_found:
            raise exceptions.ValidationError(_(
                "Cannot do this action with no project selected."
                " Details: %s",
                self._context
            ))
        
        return project_id_