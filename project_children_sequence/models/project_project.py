# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command
from odoo.osv import expression

class Project(models.Model):
    _inherit = ["project.project"]

    #====== Fields ======#
    # 2024-11-27: cancel feature of children projects's names following parent's one
    # name = fields.Char(
    #     compute='_compute_name',
    #     store=True,
    #     recursive=True,
    #     readonly=False
    # )
    sequence_code = fields.Char(
        string='Code',
        readonly=False
    )
    sequence_code_choose = fields.Boolean(
        string='Set a custom Code',
        default=False,
        store=False,
    )
    parent_id = fields.Many2one(
        ondelete='restrict',
        domain=['&', ('parent_id', '=', False), '|', ('active', '=', True), ('active', '=', False)]
    )
    children_sequence_id = fields.Many2one(
        'ir.sequence',
        string='Sequence for children projects',
        check_company=True,
        copy=False
    )

    #===== Constraints  =====#
    @api.constrains("parent_id")
    def _restrict_2level_hierarchy(self):
        """ Prevent from 2-levels hierarchy """
        if self.parent_id.parent_id.id:
            raise exceptions.ValidationError(
                _("A child project cannot become itself a parent project.")
            )

    #===== CRUD hooks =====#
    @api.model_create_multi
    def create(self, vals_list):
        vals_list = self._set_child_sequence(vals_list)
        return super().create(vals_list)
    
    def _set_child_sequence(self, vals_list):
        """ Returns enforced `vals_list` data with modified `sequence_code`
            for children projects, as per their parent's
        """

        # Perf: retrieve all parents' records at once outside `vals_list` loop
        mapped_parent_ids = {}
        parent_project_ids_ = [vals['parent_id'] for vals in vals_list if vals.get('parent_id')]
        if parent_project_ids_:
            parent_project_ids = self.env['project.project'].browse(parent_project_ids_)
            mapped_parent_ids = {x.id: x for x in parent_project_ids}
        
        for vals in vals_list:
            parent_id = mapped_parent_ids.get(vals.get('parent_id'))
            if parent_id and parent_id.id:
                # 1st time the parent project is a parent: initiate its sub-sequence
                if not parent_id.children_sequence_id.id:
                    parent_id._create_child_sequence_code()
                
                vals |= {'sequence_code': parent_id.children_sequence_id.next_by_id()}
                # 'name': parent_id.name if parent_id.name != parent_id.sequence_code else False,
        
        return vals_list
        
    def _create_child_sequence_code(self):
        """ Manages sub-projects with sequence_code per parent project (eg. 1234-01) """
        self.ensure_one()

        domain = [('code', '=', 'project.sequence.child_tmpl')]
        seq_tmpl = self.env['ir.sequence'].sudo().with_context(active_test=False).search(domain, limit=1)

        seq_new = seq_tmpl.sudo().copy()
        seq_new.write({
            'code': seq_tmpl.code + '_' + self.sequence_code,
            'name': _('Child Project sequence of ') + self.display_name,
            'prefix': self.sequence_code + (seq_tmpl.prefix or ''),
            'company_id': self.company_id.id,
            'active': True
        })
        self.children_sequence_id = seq_new

    def unlink(self):
        self.children_sequence_id.unlink()
        super().unlink()

    #===== Compute =====#
    # @api.depends('parent_id', 'parent_id.name')
    # def _compute_name(self):
    #     """ Enforces 'name' to parent's one """
    #     for project in self:
    #         if project.parent_id.id:
    #             project.name = project.parent_id.name
    