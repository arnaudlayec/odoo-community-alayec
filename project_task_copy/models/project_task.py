# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = ['project.task']

    copy_project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project Filter',
        store=False
    )
    copy_task_id = fields.Many2one(
        comodel_name='project.task',
        string='Task to copy',
        store=False,
        domain="[('project_id', '=', copy_project_id)]"
    )
    
    @api.onchange('copy_task_id')
    def _onchange_copy_from_task_id(self):
        for task in self.filtered(lambda x: x.copy_task_id.id):
            task._copy_from_one()
    
    def _copy_from_one(self):
        """ :arg self: task to receive the value
            :arg self.copy_task_id: foreign task holding the values to be copied
        """
        self.ensure_one()
        for field in self._fields_to_copy():
            if field in self:
                self[field] = self.copy_task_id[field] or False
    
    def _fields_to_copy(self):
        return ['name', 'description', 'tag_ids']
