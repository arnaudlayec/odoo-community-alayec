# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command, exceptions, _

class ProjectTaskCopy(models.TransientModel):
    _name = "project.task.copy.wizard"
    _description = "Project Task Copy Wizard"
    _inherit = ['project.default.mixin']

    #===== Constrain =====#
    @api.constrains('project_id')
    def _constrain_active_ids(self):
        """ Tasks must be selected for opening this wizard """
        if not self._context.get('active_ids'):
            raise exceptions.ValidationError(_(
                'Please select tasks to copy.'
            ))

    #===== Action =====#
    def button_copy(self):
        self._constrain_active_ids()
        Task = self.env['project.task']
        targets = Task
        sources = Task.browse(self._context.get('active_ids'))

        for task in sources:
            targets |= task.copy(self._get_default_vals(task))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Copied Tasks'),
            'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
            'res_model': 'project.task',
            'domain': [('id', 'in', targets.ids)],
            'context': {
                'default_project_id': self.project_id.id,
            }
        }
    
    def _get_default_vals(self, task):
        """ Can be overwritten """
        return {
            'project_id': self.project_id.id,
            'name': task.name, # so the copied task does not have ' (copied)' in its title
        }
