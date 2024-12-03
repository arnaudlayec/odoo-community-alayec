# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Task(models.Model):
    _inherit = ["project.task"]

    #===== Fields' method =====#
    def _get_shared_stage_ids(self):
        return self.env['project.task.type'].search([('user_id', '=', False), ('fold', '=', False)])
    
    def stage_find(self, section_id, domain=[], order='sequence, id'):
        """ Gives default stage_id: override so stages are shared between projects """
        return fields.first(self._get_shared_stage_ids()).id
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Do not show personal stage on `My Task` Kanban """
        return self._get_shared_stage_ids()
    
    
    #===== Fields =====#
    stage_id = fields.Many2one(
        # we don't fully disabled *Personal Stages*, so we filter only on non-user Stages
        domain=[('user_id', '=', False)],
    )


    #===== Logics =====#
    def _populate_missing_personal_stages(self):
        """ If wanted to fully disable *Personal Stage*,
            return an empty result without calling *super()*
        """
        res = super()._populate_missing_personal_stages()
        self.env['project.task.type'].sudo().search([('user_id', '!=', False)]).active = False
        return res
