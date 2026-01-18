# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ImportApiLine(models.Model):
    _name = 'import.api.line'
    _description = 'API log line'
    _rec_name = 'display_name'

    #===== Fields' methods =====#
    def _selection_record_ref(self):
        Model = self.env['ir.model'].sudo()
        return [
            (x['model'], x['name']) for x
            in Model.search_read([], ['model', 'name'])
        ]

    #===== Fields =====#
    # api logger
    logger_id = fields.Many2one(
        comodel_name='import.api.call',
        string='API call',
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(related="logger_id.company_id",)
    active = fields.Boolean(related='logger_id.active',store=True,)
    model = fields.Char(related='logger_id.model',)
    # line
    state = fields.Selection(
        selection=[
            ('global', "Global line"),
            ('success', "Imported"),
            ('info', "Needing review"),
            ('error', "Not imported"),
        ],
        compute='_compute_state',
        store=True,
    )
    external_id = fields.Char(string='External ID', readonly=True,)
    message = fields.Text(string='Message', readonly=True,)
    field = fields.Char(string='Field', help='In payload', readonly=True,)
    value = fields.Char(string='Value', readonly=True,)
    record_id = fields.Many2oneReference(string='Odoo ID', readonly=True,)
    record_ref = fields.Reference(
        string="Imported record",
        compute='_compute_record_ref',
        selection='_selection_record_ref',
    )

    #===== Compute =====#
    def _compute_display_name(self):
        for line in self:
            line.display_name = (
                f"[{line.logger_id}] {line.external_id} - {line.record_ref}"
            )
    
    @api.depends('record_id', 'model')
    def _compute_record_ref(self):
        """ Find which of fields in `_get_record_fields`
            is defined, for display in list view
        """
        for line in self:
            line.record_ref = (
                f"{line.model},{line.record_id}"
                if line.model in self.env and line.record_id
                else False
            )

    @api.depends('record_id', 'message')
    def _compute_state(self):
        for line in self:
            if not line.external_id:
                line.state == 'global'
            elif not line.record_id:
                line.state = 'error'
            elif line.message:
                line.state = 'info'
            else:
                line.state = 'success'
    
    #===== Logics =====#
    def _display(self):
        """ :arg line: either a log.line `record` or `vals` dict """
        report = _(
            "%s | External ID: %s | Model: %s | Odoo ID: %d",
            self.message, self.external_id, self.model, self.record_id,
        )
        if self.field:
            report += _(" | Field: %s", self.field)
        if self.value:
            report += _(" | Value: %s", self.value)
        return report
